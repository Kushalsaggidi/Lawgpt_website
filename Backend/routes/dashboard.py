import os
import logging
import requests
import torch
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ---------- Logging Setup ---------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("LawGPT-API")

# ---------- Globals ---------- #
dashboard_bp = Blueprint('dashboard', __name__)
executor = ThreadPoolExecutor(max_workers=3)

model = None
tokenizer = None
model_loaded = False

# ---------- 1. Initialize Gemini ---------- #
def setup_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not found")
        return False
    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini configured")
        return True
    except Exception as e:
        logger.error(f"Gemini configuration error: {e}")
        return False

def gemini_query(prompt):
    if not setup_gemini():
        return "[Gemini] Error: API key missing"
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(prompt)
        text = getattr(response, 'text', None)
        if text:
            logger.info("Gemini response received")
            return text
        logger.warning("Gemini returned empty response")
        return "[Gemini] Error: Empty response"
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"[Gemini] Error: {e}"

# ---------- 2. Mistral via Ollama ---------- #
import json

def mistral_query(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "mistral", "prompt": prompt, "stream": True}  # Enable streaming!
    try:
        resp = requests.post(url, json=payload, stream=True, timeout=120)  # stream=True for streamed response!
        resp.raise_for_status()
        final_text = ""
        for line in resp.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                part = data.get("response", "")
                final_text += part
                # Optionally print progress:
                # print("[STREAM]", repr(part))
        logger.info("Mistral streamed response received")
        return final_text.strip()
    except requests.exceptions.RequestException as e:
        logger.error(f"Mistral request error: {e}")
        return "[Mistral] Error: Ollama server issue"
    except Exception as e:
        logger.error(f"Mistral streaming error: {e}")
        return "[Mistral] Error: Streaming parse issue"

# ---------- 3. Load Qwen LoRA Model ---------- #
BASE_MODEL_PATH = "C:/Users/Kushal/Desktop/try/qwen-base"
ADAPTER_PATH    = "C:/Users/Kushal/Desktop/try/checkpoint-300"

def load_qwen_model():
    global model, tokenizer, model_loaded
    logger.info("Loading Qwen2.5-3B LoRA on CPU")
    try:
        if not os.path.isdir(BASE_MODEL_PATH):
            raise FileNotFoundError(BASE_MODEL_PATH)
        if not os.path.isdir(ADAPTER_PATH):
            raise FileNotFoundError(ADAPTER_PATH)

        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL_PATH, local_files_only=True, trust_remote_code=True
        )
        logger.info("Tokenizer loaded")

        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH,
            local_files_only=True,
            device_map={"": "cpu"},
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        logger.info("Base model loaded on CPU")

        model = PeftModel.from_pretrained(
            base_model,
            ADAPTER_PATH,
            device_map={"": "cpu"}
        )
        logger.info("LoRA adapter merged")

        model_loaded = True
        logger.info("Qwen2.5-LoRA ready")

    except Exception as e:
        logger.error(f"Failed to load Qwen model: {e}")
        model_loaded = False

def qwen_query(prompt):
    if not model_loaded:
        return "[LawGPT] Error: Model not loaded"
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info("LawGPT response generated")
        return text[len(prompt):].strip() if text.startswith(prompt) else text
    except Exception as e:
        logger.error(f"LawGPT generation error: {e}")
        return f"[LawGPT] Error: {e}"

# Load Qwen model at startup
load_qwen_model()

# ---------- 4. API Route ---------- #
@dashboard_bp.route('/api/query', methods=['POST'])
@jwt_required()
def post_query():
    if not request.is_json:
        return jsonify(error="Request must be JSON"), 400

    payload = request.get_json()
    prompt = payload.get("query", "").strip()
    if not prompt:
        return jsonify(error="Query cannot be empty"), 400
    if len(prompt) > 5000:
        return jsonify(error="Query too long"), 400

    logger.info(f"Received query: {prompt[:100]}")

    # Dispatch each model in parallel
    futures = {
        executor.submit(mistral_query, prompt): "opensource",
        executor.submit(qwen_query,   prompt): "lawgpt",
        executor.submit(gemini_query, prompt): "proprietary"
    }

    responses = {}
    for future in as_completed(futures):
        key = futures[future]
        try:
            responses[key] = future.result()
        except Exception as e:
            logger.error(f"Error in {key} future: {e}")
            responses[key] = f"[{key}] Error"

    # Save to DB (fire-and-forget)
    try:
        queries.insert_one({
            "email": get_jwt_identity(),
            "query": prompt,
            "responses": responses,
            "timestamp": datetime.utcnow()
        })
        logger.info("Saved query to database")
    except Exception as e:
        logger.error(f"DB insertion error: {e}")

    logger.info("Returning all responses")
    return jsonify(responses)
