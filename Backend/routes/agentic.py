from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from models import users
from utils.security import check_hash, generate_hash
import json
import google.generativeai as genai
import re
from routes.dashboard import run_all_model_queries

agentic_bp = Blueprint('agentic', __name__)

GOOGLE_API_KEY = "AIzaSyDmDIxOen_H2fTfNQgEdndo7WFfyntxgIM"
genai.configure(api_key=GOOGLE_API_KEY)

# ---------------------------
# TOOL HANDLERS
# ---------------------------

def handle_login(params, context):
    email = params.get("email")
    password = params.get("password")
    user = users.find_one({"email": email})
    if user and check_hash(password, user['password']):
        token = create_access_token(identity=email)
        context["token"] = token
        context["user_email"] = email
        return {"success": True, "token": token, "user_email": email, "message": f"✅ Logged in as {email}"}
    else:
        raise Exception("Invalid email or password")

def handle_signup(params, context):
    email = params.get("email")
    password = params.get("password")
    if users.find_one({"email": email}):
        raise Exception("Email already exists")
    users.insert_one({"email": email, "password": generate_hash(password)})
    token = create_access_token(identity=email)
    context["token"] = token
    context["user_email"] = email
    return {"success": True, "token": token, "user_email": email, "message": f"✅ Signed up and logged in as {email}"}

def handle_search(params, context):
    query = params.get("query")
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to run a search")
    responses = run_all_model_queries(user_email, query)
    return {
        "success": True,
        "query": query,
        "message": f"🔍 Got AI Insights for: {query}",
        "results": responses
    }


def handle_open_profile(params, context):
    return {"success": True, "navigate": "profile", "message": "Opening profile page..."}

def handle_update_profile(params, context):
    field, value = params.get("field"), params.get("value")
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to update profile")
    users.update_one({"email": user_email}, {"$set": {f"profile.{field}": value}})
    return {"success": True, "message": f"Updated {field} to {value}"}

def handle_open_settings(params, context):
    return {"success": True, "navigate": "settings", "message": "Opening settings page..."}

def handle_update_setting(params, context):
    setting = params.get("setting")
    value = params.get("value")
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to change settings")
    users.update_one({"email": user_email}, {"$set": {f"settings.{setting}": value}})
    return {"success": True, "message": f"Changed {setting} to {value}"}

def handle_open_login_page(params, context):
    return {"success": True, "navigate": "login", "message": "Opening login page..."}

def handle_open_signup_page(params, context):
    return {"success": True, "navigate": "signup", "message": "Opening signup page..."}

def handle_signout(params, context):
    context.clear()
    return {"success": True, "navigate": "login", "message": "Signed out"}

def handle_change_password(params, context):
    user_email = context.get("user_email")
    new_password = params.get("new_password")
    if not user_email:
        raise Exception("Must be logged in to change password")
    users.update_one({"email": user_email}, {"$set": {"password": generate_hash(new_password)}})
    return {"success": True, "message": "Password changed successfully"}

# ---------------------------
# TOOL DECLARATION (For Gemini prompt)
# ---------------------------
def get_tool_list():
    tools = {
        "login": {"description": "Log in with email & password.", "parameters": ["email", "password"]},
        "signup": {"description": "Create new account.", "parameters": ["email", "password"]},
        "search": {"description": "Search legal database.", "parameters": ["query"]},
        "open_profile": {"description": "Navigate to profile page.", "parameters": []},
        "update_profile": {"description": "Update a profile field.", "parameters": ["field", "value"]},
        "open_settings": {"description": "Navigate to settings page.", "parameters": []},
        "update_setting": {"description": "Update a setting.", "parameters": ["setting", "value"]},
        "open_login_page": {"description": "Navigate to login page.", "parameters": []},
        "open_signup_page": {"description": "Navigate to signup page.", "parameters": []},
        "signout": {"description": "Sign out & go to login.", "parameters": []},
        "change_password": {"description": "Change account password.", "parameters": ["new_password"]},
    }
    return tools

TOOL_HANDLERS = {
    "login": handle_login,
    "signup": handle_signup,
    "search": handle_search,
    "open_profile": handle_open_profile,
    "update_profile": handle_update_profile,
    "open_settings": handle_open_settings,
    "update_setting": handle_update_setting,
    "open_login_page": handle_open_login_page,
    "open_signup_page": handle_open_signup_page,
    "signout": handle_signout,
    "change_password": handle_change_password,
}

# ---------------------------
# LLM UTILITIES
# ---------------------------
def extract_agent_steps(llm_text):
    try:
        actions = json.loads(llm_text)
        if isinstance(actions, dict):
            actions = [actions]
        return actions
    except Exception:
        match = re.search(r"(\[\s*\{.*?\}\s*\])", llm_text, re.DOTALL)
        if match:
            try:
                actions = json.loads(match.group(1))
                return actions
            except Exception:
                pass
    return [{"error": f"Could not parse agent steps from: {llm_text}"}]

# ---------------------------
# AGENTIC ORCHESTRATOR
# ---------------------------
class AgenticOrchestrator:
    def __init__(self):
        self.context = {}

    def prompt_for_llm(self, user_input):
        tools = get_tool_list()
        tools_info = "\n".join([
            f'- {name}: {tool["description"]} (params: {tool["parameters"]})'
            for name, tool in tools.items()
        ])
        return (
            f"You are a robust agent for LawGPT. Available tools:\n"
            f"{tools_info}\n"
            f"\n"
            f"If a feature (like profile/settings/change password/search) requires an authenticated user and the user is not logged in, plan a login step before it.\n"
            f"When asked to open any page, always use the navigation tool (e.g., open_login_page, open_signup_page, open_profile, open_settings)."
            f"\nPlan all required steps. Output only a JSON array as a plan."
            f"\nNever wrap your output array in a 'plan' property."
            f"\nNever include parentheses in tool names."
        )

    def flatten_agentic_plan(self, actions):
        flat_actions = []
        for a in actions:
            if isinstance(a, dict) and "plan" in a:
                plan_steps = a["plan"]
                if isinstance(plan_steps, list):
                    flat_actions.extend(plan_steps)
                else:
                    flat_actions.append(plan_steps)
            else:
                flat_actions.append(a)
        return flat_actions

    def agentic_get_tool_name(self, action):
        tool_raw = (
            action.get("tool") or
            action.get("tool_code") or
            action.get("toolName") or
            action.get("tool_name") or
            action.get("command")
        )
        tool = None
        if tool_raw:
            tool = tool_raw.split("(")[0].strip()
        return tool

    def parse_with_llm(self, user_input):
        prompt = self.prompt_for_llm(user_input)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        res = model.generate_content([prompt, f'User input: "{user_input}"'])
        print("LLM RAW OUTPUT:", res.text)
        actions = extract_agent_steps(res.text)
        print("LLM PARSED ACTIONS:", actions)
        return actions

    def execute_plan(self, actions):
        results = []
        actions = self.flatten_agentic_plan(actions)
        for action in actions:
            print("ACTION:", action)
            if not isinstance(action, dict):
                results.append({"error": f"Malformed agentic action: {action}"})
                continue
            if "error" in action:
                results.append(action)
                continue
            tool = self.agentic_get_tool_name(action)
            params = action.get("parameters", {})
            handler = TOOL_HANDLERS.get(tool)
            if handler:
                try:
                    if (
                        tool not in [
                            "login", "signup", "open_login_page", "open_signup_page",
                            "open_profile", "open_settings"
                        ]
                        and not self.context.get("user_email")
                    ):
                        results.append({"tool": "login_required", "message": "You must log in first"})
                        continue
                    result = handler(params, self.context)
                    results.append({
                        "tool": tool,
                        "success": True,
                        "result": result,
                        "reasoning": action.get("reasoning", "")
                    })
                except Exception as e:
                    results.append({
                        "tool": tool,
                        "success": False,
                        "error": str(e)
                    })
            else:
                results.append({"tool": tool, "success": False, "error": "Unknown tool"})
        print("DEBUG RESULTS:", results)
        return results

# ---------------------------
# FLASK ENDPOINT
# ---------------------------
@agentic_bp.route('/api/agentic-command', methods=['POST'])
def handle_agentic_command():
    data = request.get_json()
    user_input = data.get('command', '').strip()
    orchestrator = AgenticOrchestrator()
    try:
        verify_jwt_in_request(optional=True)
        user_email = get_jwt_identity()
        orchestrator.context["user_email"] = user_email
    except Exception:
        orchestrator.context["user_email"] = None
    planned_actions = orchestrator.parse_with_llm(user_input)
    results = orchestrator.execute_plan(planned_actions)
    return jsonify({
        "user_input": user_input,
        "planned_actions": planned_actions,
        "results": results
    })
