import os
import logging
import requests
import torch
import json
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from models import queries, users

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

# Response cache for common queries
response_cache = {}
CACHE_SIZE = 100  # Maximum number of cached responses

# Performance monitoring
import time
performance_stats = {
    'total_queries': 0,
    'cache_hits': 0,
    'avg_response_time': 0.0,
    'total_response_time': 0.0
}

def get_cache_key(prompt):
    """Generate a cache key for the prompt"""
    import hashlib
    return hashlib.md5(prompt.encode()).hexdigest()

def get_cached_response(prompt):
    """Get cached response if available"""
    cache_key = get_cache_key(prompt)
    return response_cache.get(cache_key)

def cache_response(prompt, response):
    """Cache the response"""
    cache_key = get_cache_key(prompt)
    
    # If cache is full, remove oldest entry
    if len(response_cache) >= CACHE_SIZE:
        oldest_key = next(iter(response_cache))
        del response_cache[oldest_key]
    
    response_cache[cache_key] = response

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
    logger.info("Loading Qwen2.5-3B LoRA with optimizations")
    try:
        if not os.path.isdir(BASE_MODEL_PATH):
            raise FileNotFoundError(BASE_MODEL_PATH)
        if not os.path.isdir(ADAPTER_PATH):
            raise FileNotFoundError(ADAPTER_PATH)

        # Load tokenizer with optimizations
        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL_PATH, 
            local_files_only=True, 
            trust_remote_code=True,
            use_fast=True  # Use fast tokenizer
        )
        
        # Set pad token if not set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        logger.info("Tokenizer loaded with optimizations")

        # Load base model with optimizations
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH,
            local_files_only=True,
            device_map={"": "cpu"},
            torch_dtype=torch.float16,  # Use float16 for better performance
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            use_cache=True,  # Enable KV cache
            attn_implementation="eager"  # Use eager attention for better CPU performance
        )
        logger.info("Base model loaded on CPU with optimizations")

        # Load LoRA adapter
        model = PeftModel.from_pretrained(
            base_model,
            ADAPTER_PATH,
            device_map={"": "cpu"}
        )
        
        # Set model to eval mode for inference
        model.eval()
        
        # Enable optimizations
        model = torch.compile(model, mode="reduce-overhead")  # Compile for better performance
        
        logger.info("LoRA adapter merged with optimizations")

        model_loaded = True
        logger.info("Qwen2.5-LoRA ready with performance optimizations")

    except Exception as e:
        logger.error(f"Failed to load Qwen model: {e}")
        model_loaded = False

def qwen_query(prompt):
    if not model_loaded:
        return "[LawGPT] Error: Model not loaded"
    
    start_time = time.time()
    performance_stats['total_queries'] += 1
    
    # Check cache first
    cached_response = get_cached_response(prompt)
    if cached_response:
        performance_stats['cache_hits'] += 1
        response_time = time.time() - start_time
        performance_stats['total_response_time'] += response_time
        performance_stats['avg_response_time'] = performance_stats['total_response_time'] / performance_stats['total_queries']
        logger.info(f"LawGPT response served from cache in {response_time:.2f}s")
        return cached_response
    
    try:
        # Optimize input processing
        inputs = tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024,  # Reduced from 2048 for faster processing
            padding=True
        )
        
        # Optimize generation parameters for speed
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,  # Reduced from 512 for faster response
                temperature=0.8,  # Slightly higher for more focused responses
                do_sample=True,
                top_p=0.9,  # Add top_p for better quality
                top_k=50,   # Add top_k for faster sampling
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,  # Enable KV cache
                repetition_penalty=1.1,  # Reduce repetition
                no_repeat_ngram_size=2,  # Avoid repeating n-grams
                early_stopping=True  # Stop early when EOS is generated
            )
        
        # Decode only the new tokens (more efficient)
        input_length = inputs.input_ids.shape[1]
        new_tokens = outputs[0][input_length:]
        text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        # Cache the response
        cache_response(prompt, text.strip())
        
        # Update performance stats
        response_time = time.time() - start_time
        performance_stats['total_response_time'] += response_time
        performance_stats['avg_response_time'] = performance_stats['total_response_time'] / performance_stats['total_queries']
        
        logger.info(f"LawGPT response generated with optimizations and cached in {response_time:.2f}s")
        return text.strip()
        
    except Exception as e:
        response_time = time.time() - start_time
        performance_stats['total_response_time'] += response_time
        performance_stats['avg_response_time'] = performance_stats['total_response_time'] / performance_stats['total_queries']
        logger.error(f"LawGPT generation error: {e}")
        return f"[LawGPT] Error: {e}"

def qwen_query_streaming(prompt):
    """Streaming version of qwen_query for better user experience"""
    if not model_loaded:
        yield f"data: {json.dumps({'error': 'Model not loaded'})}\n\n"
        return
    
    # Check cache first
    cached_response = get_cached_response(prompt)
    if cached_response:
        logger.info("LawGPT streaming response served from cache")
        yield f"data: {json.dumps({'response': cached_response, 'cached': True})}\n\n"
        return
    
    try:
        # Optimize input processing
        inputs = tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=1024,
            padding=True
        )
        
        # Generate with streaming
        with torch.no_grad():
            for output in model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
                repetition_penalty=1.1,
                no_repeat_ngram_size=2,
                early_stopping=True,
                streamer=None  # We'll handle streaming manually
            ):
                # Decode and yield partial response
                input_length = inputs.input_ids.shape[1]
                new_tokens = output[input_length:]
                if len(new_tokens) > 0:
                    partial_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
                    yield f"data: {json.dumps({'response': partial_text, 'partial': True})}\n\n"
        
        # Cache the final response
        final_response = tokenizer.decode(output[input_length:], skip_special_tokens=True).strip()
        cache_response(prompt, final_response)
        
        # Send final response
        yield f"data: {json.dumps({'response': final_response, 'complete': True})}\n\n"
        
    except Exception as e:
        logger.error(f"LawGPT streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

# Load Qwen model at startup
load_qwen_model()

# --- Paste this in dashboard.py ---
from datetime import datetime

def run_all_model_queries(email, prompt):
    # Make sure executor, mistral_query, qwen_query, gemini_query, queries, and logger are imported/available!
    futures = {
        executor.submit(mistral_query, prompt): "opensource",
        executor.submit(qwen_query, prompt): "lawgpt",
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
    
    # Save to DB and update user stats
    try:
        queries.insert_one({
            "email": email,
            "query": prompt,
            "responses": responses,
            "timestamp": datetime.utcnow()
        })
        
        # Update user's query count
        users.update_one(
            {"email": email}, 
            {"$inc": {"stats.totalQueries": 1}}
        )
        
        logger.info("Saved query to database and updated user stats")
    except Exception as e:
        logger.error(f"DB insertion error: {e}")
    logger.info("Returning all responses")
    return responses


# ---------- 4. API Routes ---------- #
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
    email = get_jwt_identity()
    responses = run_all_model_queries(email, prompt)
    return jsonify(responses)

@dashboard_bp.route('/api/query/stream', methods=['POST'])
@jwt_required()
def post_query_stream():
    """Streaming endpoint for LawGPT responses"""
    if not request.is_json:
        return jsonify(error="Request must be JSON"), 400
    payload = request.get_json()
    prompt = payload.get("query", "").strip()
    if not prompt:
        return jsonify(error="Query cannot be empty"), 400
    if len(prompt) > 5000:
        return jsonify(error="Query too long"), 400
    
    def generate():
        try:
            # Stream LawGPT response
            for chunk in qwen_query_streaming(prompt):
                yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@dashboard_bp.route('/api/performance', methods=['GET'])
@jwt_required()
def get_performance_stats():
    """Get performance statistics for LawGPT model"""
    cache_hit_rate = (performance_stats['cache_hits'] / performance_stats['total_queries'] * 100) if performance_stats['total_queries'] > 0 else 0
    
    return jsonify({
        'total_queries': performance_stats['total_queries'],
        'cache_hits': performance_stats['cache_hits'],
        'cache_hit_rate': f"{cache_hit_rate:.1f}%",
        'avg_response_time': f"{performance_stats['avg_response_time']:.2f}s",
        'model_loaded': model_loaded,
        'cache_size': len(response_cache)
    })
