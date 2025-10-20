# Backend/routes/agentic.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from models import users, queries
from utils.security import check_hash, generate_hash
import json
import google.generativeai as genai
import re
from datetime import datetime
from routes.dashboard import run_all_model_queries

agentic_bp = Blueprint('agentic', __name__)

GOOGLE_API_KEY = "AIzaSyDmDIxOen_H2fTfNQgEdndo7WFfyntxgIM"
genai.configure(api_key=GOOGLE_API_KEY)

# -------- TOOL HANDLERS --------

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
    if not context.get("user_email"):
        raise Exception("Login required to access profile")
    return {"success": True, "navigate": "profile", "message": "Opening profile page..."}

def handle_update_profile(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to update profile")
    
    # Handle bulk updates
    updates = {}
    
    # Extract individual fields
    if "name" in params:
        updates["name"] = params["name"]
    if "bio" in params:
        updates["bio"] = params["bio"]
    if "field" in params and "value" in params:
        field = params["field"]
        value = params["value"]
        # Map field names
        field_mapping = {
            "name": "name",
            "full_name": "name", 
            "username": "name",
            "bio": "bio",
            "biography": "bio",
            "description": "bio",
            "about": "bio"
        }
        mapped_field = field_mapping.get(field.lower(), field.lower())
        updates[mapped_field] = value
    
    if not updates:
        raise Exception("No valid profile fields to update")
    
    # Update user profile (store at root level)
    users.update_one({"email": user_email}, {"$set": updates})
    
    updated_fields = ", ".join(updates.keys())
    return {"success": True, "message": f"Updated profile fields: {updated_fields}"}

def handle_open_settings(params, context):
    if not context.get("user_email"):
        raise Exception("Login required to access settings")
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
    if not user_email:
        raise Exception("Must be logged in to change password")
    
    # Extract password from various parameter formats
    new_password = (
        params.get("new_password") or 
        params.get("password") or 
        params.get("value") or
        params.get("text")
    )
    
    if not new_password:
        raise Exception("New password is required")
    
    if len(new_password) < 6:
        raise Exception("Password must be at least 6 characters long")
    
    users.update_one({"email": user_email}, {"$set": {"password": generate_hash(new_password)}})
    return {"success": True, "message": f"Password changed successfully to {new_password[:3]}***"}

def handle_open_dashboard(params, context):
    if not context.get("user_email"):
        raise Exception("Login required to access dashboard")
    return {"success": True, "navigate": "dashboard", "message": "Opening dashboard..."}

def handle_open_otp_verification(params, context):
    return {"success": True, "navigate": "otp-verification", "message": "Opening OTP verification page..."}

def handle_generate_random_user(params, context):
    import random
    import string
    
    # Generate random but realistic user details
    first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Quinn", "Sage", "River"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    return {
        "success": True, 
        "generated_user": {
            "email": email,
            "password": password,
            "name": f"{first_name} {last_name}"
        },
        "message": f"Generated user: {email}"
    }

def handle_signup_with_random(params, context):
    # Generate random user first
    random_user = handle_generate_random_user(params, context)
    if not random_user["success"]:
        return random_user
    
    user_data = random_user["generated_user"]
    email = user_data["email"]
    password = user_data["password"]
    
    # Check if user already exists
    if users.find_one({"email": email}):
        return handle_login({"email": email, "password": password}, context)
    
    # Create new user
    users.insert_one({"email": email, "password": generate_hash(password)})
    token = create_access_token(identity=email)
    context["token"] = token
    context["user_email"] = email
    
    return {
        "success": True, 
        "token": token, 
        "user_email": email, 
        "message": f"✅ Created and logged in as {email}",
        "generated_user": user_data
    }

def handle_view_query_history(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to view query history")
    
    # Get recent queries from database
    recent_queries = list(queries.find(
        {"email": user_email}, 
        {"query": 1, "timestamp": 1, "_id": 0}
    ).sort("timestamp", -1).limit(10))
    
    return {
        "success": True,
        "queries": recent_queries,
        "message": f"Found {len(recent_queries)} recent queries"
    }

def handle_clear_query_history(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to clear query history")
    
    result = queries.delete_many({"email": user_email})
    return {
        "success": True,
        "deleted_count": result.deleted_count,
        "message": f"Cleared {result.deleted_count} queries from history"
    }

def handle_update_profile_field(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to update profile")
    
    # Extract field and value from various parameter formats
    field = params.get("field") or params.get("key") or params.get("type")
    value = params.get("value") or params.get("text") or params.get("content")
    
    if not field or not value:
        raise Exception("Field and value are required")
    
    # Map common field names
    field_mapping = {
        "name": "name",
        "full_name": "name",
        "username": "name",
        "bio": "bio",
        "biography": "bio",
        "description": "bio",
        "about": "bio"
    }
    
    mapped_field = field_mapping.get(field.lower(), field.lower())
    
    # Update the specific profile field (store at root level, not nested)
    users.update_one(
        {"email": user_email}, 
        {"$set": {mapped_field: value}}
    )
    
    return {
        "success": True,
        "message": f"Updated {mapped_field} to '{value}'"
    }

def handle_get_profile(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to view profile")
    
    user = users.find_one({"email": user_email}, {"profile": 1, "email": 1})
    profile = user.get("profile", {}) if user else {}
    
    return {
        "success": True,
        "profile": profile,
        "email": user_email,
        "message": "Profile retrieved successfully"
    }

def handle_update_theme(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to change theme")
    
    # Extract theme from various parameter formats
    theme = (
        params.get("theme") or 
        params.get("value") or 
        params.get("mode") or
        params.get("text")
    )
    
    if not theme:
        raise Exception("Theme is required")
    
    # Normalize theme values
    theme_mapping = {
        "light": "light",
        "dark": "dark", 
        "auto": "auto",
        "automatic": "auto",
        "system": "auto",
        "day": "light",
        "night": "dark"
    }
    
    normalized_theme = theme_mapping.get(theme.lower(), theme.lower())
    
    if normalized_theme not in ["light", "dark", "auto"]:
        raise Exception("Theme must be 'light', 'dark', or 'auto'")
    
    # Update theme in user settings
    users.update_one(
        {"email": user_email}, 
        {"$set": {"settings.theme": normalized_theme}}
    )
    
    return {
        "success": True,
        "message": f"Theme changed to {normalized_theme}",
        "theme": normalized_theme
    }

def handle_update_notification_setting(params, context):
    user_email = context.get("user_email")
    setting = params.get("setting")
    value = params.get("value")
    
    if not setting or value is None:
        raise Exception("Setting and value are required")
    
    # Update notification setting
    users.update_one(
        {"email": user_email}, 
        {"$set": {f"settings.notifications.{setting}": bool(value)}}
    )
    
    return {
        "success": True,
        "message": f"Updated {setting} to {value}"
    }

def handle_delete_account(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to delete account")
    
    # Delete user and all their data
    users.delete_one({"email": user_email})
    queries.delete_many({"email": user_email})
    
    # Clear context
    context.clear()
    
    return {
        "success": True,
        "message": "Account deleted successfully",
        "navigate": "login"
    }

def handle_export_data(params, context):
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to export data")
    
    # Get all user data
    user = users.find_one({"email": user_email})
    user_queries = list(queries.find({"email": user_email}))
    
    export_data = {
        "user_profile": user,
        "query_history": user_queries,
        "exported_at": datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "data": export_data,
        "message": "Data exported successfully"
    }

def handle_help(params, context):
    tools = get_tool_list()
    help_text = "Available commands:\n\n"
    
    for tool_name, tool_info in tools.items():
        help_text += f"• {tool_name}: {tool_info['description']}\n"
        if tool_info['parameters']:
            help_text += f"  Parameters: {', '.join(tool_info['parameters'])}\n"
        help_text += "\n"
    
    return {
        "success": True,
        "help_text": help_text,
        "message": "Here are all available commands"
    }

# New: Add more handlers here as project grows

# -------- TOOL DECLARATION --------

def get_tool_list():
    tools = {
        # Authentication & User Management
        "login": {"description": "Log in with email & password.", "parameters": ["email", "password"]},
        "signup": {"description": "Create new account.", "parameters": ["email", "password"]},
        "signup_with_random": {"description": "Create account with randomly generated user details.", "parameters": []},
        "generate_random_user": {"description": "Generate random but realistic user details.", "parameters": []},
        "signout": {"description": "Sign out & go to login.", "parameters": []},
        "change_password": {"description": "Change account password.", "parameters": ["new_password"]},
        "delete_account": {"description": "Delete user account and all data.", "parameters": []},
        
        # Navigation
        "open_login_page": {"description": "Navigate to login page.", "parameters": []},
        "open_signup_page": {"description": "Navigate to signup page.", "parameters": []},
        "open_dashboard": {"description": "Navigate to dashboard page.", "parameters": []},
        "open_profile": {"description": "Navigate to profile page.", "parameters": []},
        "open_settings": {"description": "Navigate to settings page.", "parameters": []},
        "open_otp_verification": {"description": "Navigate to OTP verification page.", "parameters": []},
        
        # Search & Queries
        "search": {"description": "Search legal database and display results in dashboard.", "parameters": ["query"]},
        "view_query_history": {"description": "View recent query history.", "parameters": []},
        "clear_query_history": {"description": "Clear all query history.", "parameters": []},
        
        # Profile Management
        "get_profile": {"description": "Get current user profile information.", "parameters": []},
        "update_profile_field": {"description": "Update a specific profile field.", "parameters": ["field", "value"]},
        "update_profile": {"description": "Update multiple profile fields.", "parameters": ["field", "value"]},
        
        # Settings & Preferences
        "update_setting": {"description": "Update a general setting.", "parameters": ["setting", "value"]},
        "update_theme": {"description": "Change app theme (light/dark/auto).", "parameters": ["theme"]},
        "update_notification_setting": {"description": "Update notification preferences.", "parameters": ["setting", "value"]},
        
        # Data Management
        "export_data": {"description": "Export all user data.", "parameters": []},
        
        # Help & Support
        "help": {"description": "Show all available commands and their usage.", "parameters": []},
    }
    return tools

TOOL_HANDLERS = {
    # Authentication & User Management
    "login": handle_login,
    "signup": handle_signup,
    "signup_with_random": handle_signup_with_random,
    "generate_random_user": handle_generate_random_user,
    "signout": handle_signout,
    "change_password": handle_change_password,
    "delete_account": handle_delete_account,
    
    # Navigation
    "open_login_page": handle_open_login_page,
    "open_signup_page": handle_open_signup_page,
    "open_dashboard": handle_open_dashboard,
    "open_profile": handle_open_profile,
    "open_settings": handle_open_settings,
    "open_otp_verification": handle_open_otp_verification,
    
    # Search & Queries
    "search": handle_search,
    "view_query_history": handle_view_query_history,
    "clear_query_history": handle_clear_query_history,
    
    # Profile Management
    "get_profile": handle_get_profile,
    "update_profile_field": handle_update_profile_field,
    "update_profile": handle_update_profile,
    
    # Settings & Preferences
    "update_setting": handle_update_setting,
    "update_theme": handle_update_theme,
    "update_notification_setting": handle_update_notification_setting,
    
    # Data Management
    "export_data": handle_export_data,
    
    # Help & Support
    "help": handle_help,
}

# -------- LLM & AGENTIC ORCHESTRATOR --------

def extract_agent_steps(llm_text):
    try:
        actions = json.loads(llm_text)
        if isinstance(actions, dict):
            actions = [actions]
        return actions
    except Exception:
        match = re.search(r"(\[\s*{.*?}\s*\])", llm_text, re.DOTALL)
        if match:
            try:
                actions = json.loads(match.group(1))
                return actions
            except Exception:
                pass
        return [{"error": f"Could not parse agent steps from: {llm_text}"}]

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
            f"You are a comprehensive agentic assistant for LawGPT - a legal AI platform. You can handle every aspect of the application through natural language commands.\n\n"
            f"Available tools:\n"
            f"{tools_info}\n\n"
            f"IMPORTANT RULES:\n"
            f"1. AUTHENTICATION: If any action requires login (search, profile, settings, etc.) and user is not logged in, first use 'signup_with_random' or 'login'.\n"
            f"2. NAVIGATION: Always navigate to the correct page before performing actions on that page.\n"
            f"3. SEARCH: When user asks to search, use the 'search' tool - it will automatically display results in the dashboard.\n"
            f"4. MULTI-STEP: Break complex requests into logical steps and execute them in order.\n"
            f"5. RANDOM USERS: If user asks to 'sign up with random details' or similar, use 'signup_with_random'.\n"
            f"6. PROFILE UPDATES: Use 'update_profile_field' for individual fields or 'update_profile' for multiple fields.\n"
            f"7. THEME CHANGES: Use 'update_theme' with values 'light', 'dark', or 'auto'.\n"
            f"8. ERROR HANDLING: If a tool fails, try alternative approaches or inform the user.\n"
            f"9. VOICE COMMANDS: All commands work with both voice and text input.\n"
            f"10. HELP: If user asks for help or available commands, use the 'help' tool.\n"
            f"11. SMART PARAMETER EXTRACTION: Extract values from natural language. For passwords, extract the actual password text. For themes, map 'dark mode' to 'dark', 'light mode' to 'light'.\n"
            f"12. CHAINED ACTIONS: For commands like 'open settings and change password to xyz123', break into separate actions.\n\n"
            f"EXAMPLES:\n"
            f"- 'search for article 370' → [{{\"tool\": \"search\", \"parameters\": {{\"query\": \"article 370\"}}}}]\n"
            f"- 'sign up and search for section 498A' → [{{\"tool\": \"signup_with_random\", \"parameters\": {{}}}}, {{\"tool\": \"search\", \"parameters\": {{\"query\": \"section 498A\"}}}}]\n"
            f"- 'change my theme to dark mode' → [{{\"tool\": \"update_theme\", \"parameters\": {{\"theme\": \"dark\"}}}}]\n"
            f"- 'open settings and change my password to newpass123' → [{{\"tool\": \"open_settings\", \"parameters\": {{}}}}, {{\"tool\": \"change_password\", \"parameters\": {{\"new_password\": \"newpass123\"}}}}]\n"
            f"- 'update my name to John Doe and bio to Legal Professional' → [{{\"tool\": \"update_profile_field\", \"parameters\": {{\"field\": \"name\", \"value\": \"John Doe\"}}}}, {{\"tool\": \"update_profile_field\", \"parameters\": {{\"field\": \"bio\", \"value\": \"Legal Professional\"}}}}]\n"
            f"- 'show my query history' → [{{\"tool\": \"view_query_history\", \"parameters\": {{}}}}]\n"
            f"- 'delete my account' → [{{\"tool\": \"delete_account\", \"parameters\": {{}}}}]\n\n"
            f"Output only a JSON array of actions. Never wrap in 'plan' property. Never include parentheses in tool names.\n"
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

# -------- FLASK ENDPOINT --------

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
