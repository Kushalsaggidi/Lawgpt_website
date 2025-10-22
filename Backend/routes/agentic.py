# Backend/routes/agentic.py - ULTIMATE AGENTIC BACKEND

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from models import users, queries, otp_codes
from utils.security import check_hash, generate_hash, create_jwt, generate_otp
from utils.email import send_otp_email
import json
import google.generativeai as genai
import re
import random
import string
from datetime import datetime, timedelta
from routes.dashboard import run_all_model_queries

agentic_bp = Blueprint('agentic', __name__)

GOOGLE_API_KEY = "AIzaSyDmDIxOen_H2fTfNQgEdndo7WFfyntxgIM"
genai.configure(api_key=GOOGLE_API_KEY)

# -------- COMPREHENSIVE TOOL HANDLERS --------

# ===== AUTHENTICATION & USER MANAGEMENT =====

def handle_login(params, context):
    """Handle user login with intelligent parameter extraction"""
    email = params.get("email") or params.get("username") or params.get("user")
    password = params.get("password") or params.get("pass") or params.get("pwd")
    
    if not email or not password:
        raise Exception("Email and password are required")
    
    user = users.find_one({"email": email})
    if user and check_hash(password, user['password']):
        token = create_access_token(identity=email)
        context["token"] = token
        context["user_email"] = email
        return {
            "success": True, 
            "token": token, 
            "user_email": email, 
            "message": f"✅ Successfully logged in as {email}",
            "user_data": {
                "name": user.get("name", ""),
                "email": email,
                "bio": user.get("bio", "")
            }
        }
    else:
        raise Exception("Invalid email or password")

def handle_signup(params, context):
    """Handle user registration with intelligent parameter extraction"""
    email = params.get("email") or params.get("username") or params.get("user")
    password = params.get("password") or params.get("pass") or params.get("pwd")
    name = params.get("name") or params.get("full_name") or params.get("username") or "User"
    
    if not email or not password:
        raise Exception("Email and password are required")
    
    if users.find_one({"email": email}):
        raise Exception("Email already exists")
    
    if len(password) < 6:
        raise Exception("Password must be at least 6 characters long")
    
    # Create user with comprehensive data
    user_data = {
        "name": name,
        "email": email,
        "password": generate_hash(password),
        "bio": "",
        "created_at": datetime.utcnow(),
        "settings": {
            "theme": "auto",
            "notifications": {"enabled": True}
        },
        "stats": {
            "totalQueries": 0,
            "favoriteModel": "LawGPT",
            "accountAge": "0 days",
            "currentStreak": "0 days",
            "accuracy": 0,
            "responseTime": 0,
            "satisfaction": 0
        }
    }
    
    users.insert_one(user_data)
    
    # Generate and send OTP
    otp = generate_otp()
    otp_codes.insert_one({
        "email": email,
        "otp_code": otp,
        "purpose": "signup",
        "expiry": datetime.utcnow() + timedelta(minutes=10)
    })
    
    try:
        send_otp_email(email, otp)
        return {
            "success": True, 
            "message": f"✅ Account created for {email}. OTP sent to your email for verification.",
            "email": email,
            "requires_otp": True
        }
    except Exception as e:
        return {
            "success": True, 
            "message": f"✅ Account created for {email}. OTP generation failed: {str(e)}",
            "email": email,
            "requires_otp": False
        }

def handle_verify_otp(params, context):
    """Handle OTP verification for signup or login"""
    email = params.get("email") or params.get("user")
    otp = params.get("otp") or params.get("code") or params.get("verification_code")
    purpose = params.get("purpose") or "signup"
    
    if not email or not otp:
        raise Exception("Email and OTP are required")
    
    entry = otp_codes.find_one({
        "email": email,
        "otp_code": otp,
        "purpose": purpose
    })
    
    if entry and entry['expiry'] > datetime.utcnow():
        otp_codes.delete_one({"_id": entry['_id']})
        
        if purpose == "login":
            token = create_jwt(email)
            context["token"] = token
            context["user_email"] = email
            return {
                "success": True, 
                "token": token, 
                "user_email": email, 
                "message": f"✅ OTP verified! Logged in as {email}"
            }
        else:
            return {
                "success": True, 
                "message": f"✅ OTP verified! Account for {email} is now active"
            }
    else:
        raise Exception("Invalid or expired OTP")

def handle_resend_otp(params, context):
    """Handle OTP resend functionality"""
    email = params.get("email") or params.get("user")
    purpose = params.get("purpose") or "signup"
    
    if not email:
        raise Exception("Email is required")
    
    otp = generate_otp()
    otp_codes.insert_one({
        "email": email,
        "otp_code": otp,
        "purpose": purpose,
        "expiry": datetime.utcnow() + timedelta(minutes=10)
    })
    
    try:
        send_otp_email(email, otp)
        return {
            "success": True, 
            "message": f"✅ New OTP sent to {email}"
        }
    except Exception as e:
        raise Exception(f"Failed to send OTP: {str(e)}")

def handle_generate_random_user(params, context):
    """Generate realistic random user data with better uniqueness"""
    first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Quinn", "Sage", "River", "Blake", "Cameron", "Drew", "Emery", "Finley", "Harper", "Kai", "Lane", "Parker", "Reese"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "icloud.com", "live.com"]
    professions = ["Lawyer", "Legal Consultant", "Attorney", "Legal Advisor", "Paralegal", "Legal Researcher", "Corporate Counsel", "Criminal Defense Attorney", "Family Law Attorney", "Immigration Lawyer"]
    specializations = ["Corporate Law", "Criminal Law", "Family Law", "Property Law", "Constitutional Law", "Immigration Law", "Tax Law", "Employment Law", "Intellectual Property", "Environmental Law"]
    
    # Generate unique email by adding random numbers
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    random_suffix = random.randint(100, 9999)
    email = f"{first_name.lower()}.{last_name.lower()}{random_suffix}@{random.choice(domains)}"
    
    # Generate strong password
    password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=12))
    
    profession = random.choice(professions)
    specialization = random.choice(specializations)
    
    return {
        "success": True, 
        "generated_user": {
            "email": email,
            "password": password,
            "name": f"{first_name} {last_name}",
            "bio": f"{profession} specializing in {specialization} with {random.randint(2, 15)} years of experience"
        },
        "message": f"Generated user: {email}"
    }

def handle_signup_with_random(params, context):
    """Create account with randomly generated user details - improved version"""
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        try:
            random_user = handle_generate_random_user(params, context)
            if not random_user["success"]:
                return random_user
            
            user_data = random_user["generated_user"]
            email = user_data["email"]
            password = user_data["password"]
            name = user_data["name"]
            bio = user_data.get("bio", "")
            
            # Check if user already exists
            existing_user = users.find_one({"email": email})
            if existing_user:
                attempt += 1
                continue  # Try with different random data
            
            # Create new user
            user_record = {
                "name": name,
                "email": email,
                "password": generate_hash(password),
                "bio": bio,
                "created_at": datetime.utcnow(),
                "settings": {
                    "theme": "auto",
                    "notifications": {"enabled": True}
                },
                "stats": {
                    "totalQueries": 0,
                    "favoriteModel": "LawGPT",
                    "accountAge": "0 days",
                    "currentStreak": "0 days",
                    "accuracy": 0,
                    "responseTime": 0,
                    "satisfaction": 0
                }
            }
            
            users.insert_one(user_record)
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
            
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                return {
                    "success": False,
                    "error": f"Failed to create random user after {max_attempts} attempts: {str(e)}"
                }
            continue
    
    return {
        "success": False,
        "error": f"Failed to create unique random user after {max_attempts} attempts"
    }

# ===== SEARCH & AI FUNCTIONALITY =====

def handle_search(params, context):
    """Handle AI search with comprehensive query processing"""
    query = params.get("query") or params.get("question") or params.get("search") or params.get("text")
    user_email = context.get("user_email")
    
    if not user_email:
        raise Exception("Must be logged in to run a search")
    
    if not query:
        raise Exception("Search query is required")
    
    if len(query.strip()) < 3:
        raise Exception("Search query must be at least 3 characters long")
    
    try:
        responses = run_all_model_queries(user_email, query)
        return {
            "success": True,
            "query": query,
            "message": f"🔍 Got AI Insights for: {query}",
            "results": responses,
            "search_results": {
                "query": query,
                "responses": responses
            }
        }
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")

def handle_view_query_history(params, context):
    """View user's query history with intelligent filtering"""
    user_email = context.get("user_email")
    if not user_email: 
        raise Exception("Must be logged in to view query history")
    
    limit = int(params.get("limit", 10))
    offset = int(params.get("offset", 0))
    
    # Get recent queries from database
    recent_queries = list(queries.find(
        {"email": user_email}, 
        {"query": 1, "timestamp": 1, "responses": 1, "_id": 0}
    ).sort("timestamp", -1).skip(offset).limit(limit))
    
    return {
        "success": True,
        "queries": recent_queries,
        "total_count": len(recent_queries),
        "message": f"Found {len(recent_queries)} recent queries"
    }

def handle_clear_query_history(params, context):
    """Clear user's query history"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to clear query history")
    
    result = queries.delete_many({"email": user_email})
    return {
        "success": True,
        "deleted_count": result.deleted_count,
        "message": f"Cleared {result.deleted_count} queries from history"
    }

# ===== NAVIGATION FUNCTIONALITY =====

def handle_open_dashboard(params, context):
    """Navigate to dashboard"""
    if not context.get("user_email"):
        raise Exception("Login required to access dashboard")
    return {"success": True, "navigate": "dashboard", "message": "Opening dashboard..."}

def handle_open_profile(params, context):
    """Navigate to profile page"""
    if not context.get("user_email"):
        raise Exception("Login required to access profile")
    return {"success": True, "navigate": "profile", "message": "Opening profile page..."}

def handle_open_settings(params, context):
    """Navigate to settings page"""
    if not context.get("user_email"):
        raise Exception("Login required to access settings")
    return {"success": True, "navigate": "settings", "message": "Opening settings page..."}

def handle_open_login_page(params, context):
    """Navigate to login page"""
    return {"success": True, "navigate": "login", "message": "Opening login page..."}

def handle_open_signup_page(params, context):
    """Navigate to signup page"""
    return {"success": True, "navigate": "signup", "message": "Opening signup page..."}

def handle_open_otp_verification(params, context):
    """Navigate to OTP verification page"""
    return {"success": True, "navigate": "otp-verification", "message": "Opening OTP verification page..."}

def handle_signout(params, context):
    """Sign out user and clear context"""
    context.clear()
    return {"success": True, "navigate": "login", "message": "Signed out successfully"}

# ===== PROFILE MANAGEMENT =====

def handle_get_profile(params, context):
    """Get current user profile information"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to view profile")
    
    user = users.find_one({"email": user_email})
    if not user:
        raise Exception("User not found")
    
    profile_data = {
        "name": user.get("name", ""),
        "email": user_email,
        "bio": user.get("bio", ""),
        "memberSince": user.get("created_at", ""),
        "stats": user.get("stats", {}),
        "settings": user.get("settings", {})
    }
    
    return {
        "success": True,
        "profile": profile_data,
        "message": "Profile retrieved successfully"
    }

def handle_update_profile_field(params, context):
    """Update a specific profile field with intelligent field mapping"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to update profile")
    
    # Extract field and value with intelligent mapping
    field = params.get("field") or params.get("key") or params.get("type") or params.get("attribute")
    value = params.get("value") or params.get("text") or params.get("content") or params.get("new_value")
    
    if not field or not value:
        raise Exception("Field and value are required")
    
    # Intelligent field mapping
    field_mapping = {
        "name": "name",
        "full_name": "name",
        "username": "name",
        "display_name": "name",
        "bio": "bio",
        "biography": "bio",
        "description": "bio",
        "about": "bio",
        "about_me": "bio",
        "profile_description": "bio"
    }
    
    mapped_field = field_mapping.get(field.lower(), field.lower())
    
    # Update the specific profile field
    result = users.update_one(
        {"email": user_email}, 
        {"$set": {mapped_field: value}}
    )
    
    if result.modified_count == 0:
        raise Exception("Failed to update profile field")
    
    return {
        "success": True,
        "message": f"Updated {mapped_field} to '{value}'"
    }

def handle_update_profile(params, context):
    """Update multiple profile fields at once"""
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
    
    # Update user profile
    result = users.update_one({"email": user_email}, {"$set": updates})
    
    if result.modified_count == 0:
        raise Exception("Failed to update profile")
    
    updated_fields = ", ".join(updates.keys())
    return {"success": True, "message": f"Updated profile fields: {updated_fields}"}

# ===== SETTINGS & PREFERENCES =====

def handle_update_setting(params, context):
    """Update a general setting with intelligent parameter extraction"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to change settings")
    
    setting = params.get("setting") or params.get("key") or params.get("type")
    value = params.get("value") or params.get("new_value") or params.get("text")
    
    if not setting or value is None:
        raise Exception("Setting and value are required")
    
    # Update setting in user preferences
    result = users.update_one(
        {"email": user_email}, 
        {"$set": {f"settings.{setting}": value}}
    )
    
    if result.modified_count == 0:
        raise Exception("Failed to update setting")
    
    return {"success": True, "message": f"Changed {setting} to {value}"}

def handle_update_theme(params, context):
    """Update app theme with intelligent theme mapping"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to change theme")
    
    # Extract theme from various parameter formats
    theme = (
        params.get("theme") or 
        params.get("value") or 
        params.get("mode") or
        params.get("text") or
        params.get("color_scheme")
    )
    
    if not theme:
        raise Exception("Theme is required")
    
    # Intelligent theme mapping
    theme_mapping = {
        "light": "light",
        "dark": "dark", 
        "auto": "auto",
        "automatic": "auto",
        "system": "auto",
        "day": "light",
        "night": "dark",
        "light_mode": "light",
        "dark_mode": "dark",
        "auto_mode": "auto"
    }
    
    normalized_theme = theme_mapping.get(theme.lower(), theme.lower())
    
    if normalized_theme not in ["light", "dark", "auto"]:
        raise Exception("Theme must be 'light', 'dark', or 'auto'")
    
    # Update theme in user settings
    result = users.update_one(
        {"email": user_email}, 
        {"$set": {"settings.theme": normalized_theme}}
    )
    
    if result.modified_count == 0:
        raise Exception("Failed to update theme")
    
    return {
        "success": True,
        "message": f"Theme changed to {normalized_theme}",
        "theme": normalized_theme
    }

def handle_update_notification_setting(params, context):
    """Update notification preferences with intelligent parameter extraction"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to change notification settings")
    
    setting = params.get("setting") or params.get("key") or params.get("type")
    value = params.get("value") or params.get("enabled") or params.get("status")
    
    if not setting or value is None:
        raise Exception("Setting and value are required")
    
    # Convert string values to boolean
    if isinstance(value, str):
        value = value.lower() in ["true", "1", "yes", "on", "enabled"]
    
    # Update notification setting
    result = users.update_one(
        {"email": user_email}, 
        {"$set": {f"settings.notifications.{setting}": bool(value)}}
    )
    
    if result.modified_count == 0:
        raise Exception("Failed to update notification setting")
    
    return {
        "success": True,
        "message": f"Updated notification {setting} to {value}"
    }

def handle_change_password(params, context):
    """Change user password with intelligent parameter extraction"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to change password")
    
    # Extract password from various parameter formats
    new_password = (
        params.get("new_password") or 
        params.get("password") or 
        params.get("value") or
        params.get("text") or
        params.get("new_pass")
    )
    
    if not new_password:
        raise Exception("New password is required")
    
    if len(new_password) < 6:
        raise Exception("Password must be at least 6 characters long")
    
    # Update password
    result = users.update_one(
        {"email": user_email}, 
        {"$set": {"password": generate_hash(new_password)}}
    )
    
    if result.modified_count == 0:
        raise Exception("Failed to update password")
    
    return {"success": True, "message": f"Password changed successfully"}

# ===== DATA MANAGEMENT =====

def handle_export_data(params, context):
    """Export all user data with comprehensive information"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to export data")
    
    # Get all user data
    user = users.find_one({"email": user_email})
    user_queries = list(queries.find({"email": user_email}))
    
    export_data = {
        "user_profile": {
            "name": user.get("name", ""),
            "email": user_email,
            "bio": user.get("bio", ""),
            "created_at": user.get("created_at"),
            "settings": user.get("settings", {}),
            "stats": user.get("stats", {})
        },
        "query_history": [
            {
                "query": q.get("query", ""),
                "timestamp": q.get("timestamp"),
                "responses": q.get("responses", {})
            }
            for q in user_queries
        ],
        "exported_at": datetime.utcnow().isoformat(),
        "total_queries": len(user_queries)
    }
    
    return {
        "success": True,
        "data": export_data,
        "message": "Data exported successfully"
    }

def handle_delete_account(params, context):
    """Delete user account and all associated data"""
    user_email = context.get("user_email")
    if not user_email:
        raise Exception("Must be logged in to delete account")
    
    # Delete user and all their data
    user_result = users.delete_one({"email": user_email})
    queries_result = queries.delete_many({"email": user_email})
    
    if user_result.deleted_count == 0:
        raise Exception("User not found")
    
    # Clear context
    context.clear()
    
    return {
        "success": True,
        "message": "Account deleted successfully",
        "deleted_queries": queries_result.deleted_count,
        "navigate": "login"
    }

# ===== HELP & SUPPORT =====

def handle_help(params, context):
    """Provide comprehensive help information"""
    tools = get_tool_list()
    help_text = "🤖 LawGPT Agentic Assistant - Available Commands:\n\n"
    
    # Group tools by category
    categories = {
        "🔐 Authentication": ["login", "signup", "signup_with_random", "verify_otp", "resend_otp", "signout"],
        "🧭 Navigation": ["open_dashboard", "open_profile", "open_settings", "open_login_page", "open_signup_page", "open_otp_verification"],
        "🔍 Search & AI": ["search", "view_query_history", "clear_query_history"],
        "👤 Profile": ["get_profile", "update_profile_field", "update_profile"],
        "⚙️ Settings": ["update_setting", "update_theme", "update_notification_setting", "change_password"],
        "📊 Data": ["export_data", "delete_account"],
        "❓ Help": ["help"]
    }
    
    for category, tool_names in categories.items():
        help_text += f"{category}\n"
        for tool_name in tool_names:
            if tool_name in tools:
                tool_info = tools[tool_name]
                help_text += f"  • {tool_name}: {tool_info['description']}\n"
        if tool_info['parameters']:
                    help_text += f"    Parameters: {', '.join(tool_info['parameters'])}\n"
        help_text += "\n"
    
    help_text += "💡 Examples:\n"
    help_text += "  • 'sign up with random details and search for article 370'\n"
    help_text += "  • 'change my theme to dark mode'\n"
    help_text += "  • 'update my name to John Doe and bio to Legal Expert'\n"
    help_text += "  • 'show my query history'\n"
    help_text += "  • 'export my data'\n"
    
    return {
        "success": True,
        "help_text": help_text,
        "message": "Here are all available commands and examples"
    }

# New: Add more handlers here as project grows

# -------- TOOL DECLARATION --------

def get_tool_list():
    """Comprehensive tool list with all LawGPT features"""
    tools = {
        # ===== AUTHENTICATION & USER MANAGEMENT =====
        "login": {
            "description": "Log in with email & password. Supports various parameter formats.",
            "parameters": ["email", "password"]
        },
        "signup": {
            "description": "Create new account with email, password, and name. Sends OTP for verification.",
            "parameters": ["email", "password", "name"]
        },
        "signup_with_random": {
            "description": "Create account with randomly generated realistic user details. Perfect for testing.",
            "parameters": []
        },
        "generate_random_user": {
            "description": "Generate random but realistic user details for testing purposes.",
            "parameters": []
        },
        "verify_otp": {
            "description": "Verify OTP code for signup or login verification.",
            "parameters": ["email", "otp", "purpose"]
        },
        "resend_otp": {
            "description": "Resend OTP code to user's email.",
            "parameters": ["email", "purpose"]
        },
        "signout": {
            "description": "Sign out user and clear session. Navigates to login page.",
            "parameters": []
        },
        "change_password": {
            "description": "Change user account password. Supports various parameter formats.",
            "parameters": ["new_password"]
        },
        "delete_account": {
            "description": "Delete user account and all associated data permanently.",
            "parameters": []
        },
        
        # ===== NAVIGATION =====
        "open_login_page": {
            "description": "Navigate to login page.",
            "parameters": []
        },
        "open_signup_page": {
            "description": "Navigate to signup page.",
            "parameters": []
        },
        "open_dashboard": {
            "description": "Navigate to dashboard page. Requires authentication.",
            "parameters": []
        },
        "open_profile": {
            "description": "Navigate to profile page. Requires authentication.",
            "parameters": []
        },
        "open_settings": {
            "description": "Navigate to settings page. Requires authentication.",
            "parameters": []
        },
        "open_otp_verification": {
            "description": "Navigate to OTP verification page.",
            "parameters": []
        },
        
        # ===== SEARCH & AI FUNCTIONALITY =====
        "search": {
            "description": "Search legal database using multiple AI models. Displays results in dashboard.",
            "parameters": ["query"]
        },
        "view_query_history": {
            "description": "View recent query history with optional pagination.",
            "parameters": ["limit", "offset"]
        },
        "clear_query_history": {
            "description": "Clear all query history for the current user.",
            "parameters": []
        },
        
        # ===== PROFILE MANAGEMENT =====
        "get_profile": {
            "description": "Get current user profile information including stats and settings.",
            "parameters": []
        },
        "update_profile_field": {
            "description": "Update a specific profile field (name, bio, etc.) with intelligent field mapping.",
            "parameters": ["field", "value"]
        },
        "update_profile": {
            "description": "Update multiple profile fields at once.",
            "parameters": ["name", "bio"]
        },
        
        # ===== SETTINGS & PREFERENCES =====
        "update_setting": {
            "description": "Update a general user setting with intelligent parameter extraction.",
            "parameters": ["setting", "value"]
        },
        "update_theme": {
            "description": "Change app theme (light/dark/auto) with intelligent theme mapping.",
            "parameters": ["theme"]
        },
        "update_notification_setting": {
            "description": "Update notification preferences with intelligent parameter extraction.",
            "parameters": ["setting", "value"]
        },
        
        # ===== DATA MANAGEMENT =====
        "export_data": {
            "description": "Export all user data including profile, queries, and settings.",
            "parameters": []
        },
        
        # ===== HELP & SUPPORT =====
        "help": {
            "description": "Show comprehensive help with all available commands, examples, and usage.",
            "parameters": []
        },
    }
    return tools

TOOL_HANDLERS = {
    # ===== AUTHENTICATION & USER MANAGEMENT =====
    "login": handle_login,
    "signup": handle_signup,
    "signup_with_random": handle_signup_with_random,
    "generate_random_user": handle_generate_random_user,
    "verify_otp": handle_verify_otp,
    "resend_otp": handle_resend_otp,
    "signout": handle_signout,
    "change_password": handle_change_password,
    "delete_account": handle_delete_account,
    
    # ===== NAVIGATION =====
    "open_login_page": handle_open_login_page,
    "open_signup_page": handle_open_signup_page,
    "open_dashboard": handle_open_dashboard,
    "open_profile": handle_open_profile,
    "open_settings": handle_open_settings,
    "open_otp_verification": handle_open_otp_verification,
    
    # ===== SEARCH & AI FUNCTIONALITY =====
    "search": handle_search,
    "view_query_history": handle_view_query_history,
    "clear_query_history": handle_clear_query_history,
    
    # ===== PROFILE MANAGEMENT =====
    "get_profile": handle_get_profile,
    "update_profile_field": handle_update_profile_field,
    "update_profile": handle_update_profile,
    
    # ===== SETTINGS & PREFERENCES =====
    "update_setting": handle_update_setting,
    "update_theme": handle_update_theme,
    "update_notification_setting": handle_update_notification_setting,
    
    # ===== DATA MANAGEMENT =====
    "export_data": handle_export_data,
    
    # ===== HELP & SUPPORT =====
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
            f"🤖 You are the ULTIMATE agentic assistant for LawGPT - a comprehensive legal AI platform. You can handle EVERY aspect of the application through natural language commands with intelligent understanding.\n\n"
            f"🔧 AVAILABLE TOOLS ({len(tools)} total):\n"
            f"{tools_info}\n\n"
            f"🧠 INTELLIGENT PROCESSING RULES:\n"
            f"1. 🔐 AUTHENTICATION: If any action requires login (search, profile, settings, etc.) and user is not logged in, first use 'signup_with_random' or 'login'.\n"
            f"2. 🧭 NAVIGATION: Always navigate to the correct page before performing actions on that page.\n"
            f"3. 🔍 SEARCH: When user asks to search, use the 'search' tool - it will automatically display results in the dashboard.\n"
            f"4. 🔄 MULTI-STEP: Break complex requests into logical steps and execute them in order.\n"
            f"5. 🎲 RANDOM USERS: If user asks to 'sign up with random details' or similar, use 'signup_with_random'.\n"
            f"6. 👤 PROFILE UPDATES: Use 'update_profile_field' for individual fields or 'update_profile' for multiple fields.\n"
            f"7. 🎨 THEME CHANGES: Use 'update_theme' with values 'light', 'dark', or 'auto'.\n"
            f"8. ❌ ERROR HANDLING: If a tool fails, try alternative approaches or inform the user.\n"
            f"9. 🎤 VOICE COMMANDS: All commands work with both voice and text input.\n"
            f"10. ❓ HELP: If user asks for help or available commands, use the 'help' tool.\n"
            f"11. 🧠 SMART PARAMETER EXTRACTION: Extract values from natural language. For passwords, extract the actual password text. For themes, map 'dark mode' to 'dark', 'light mode' to 'light'.\n"
            f"12. ⛓️ CHAINED ACTIONS: For commands like 'open settings and change password to xyz123', break into separate actions.\n"
            f"13. 🔍 INTELLIGENT SEARCH: Understand legal queries and extract the core legal question.\n"
            f"14. 👤 PROFILE INTELLIGENCE: Map various field names (name, full_name, username, bio, biography, description, about) to correct database fields.\n"
            f"15. ⚙️ SETTINGS INTELLIGENCE: Understand theme preferences (dark mode, light mode, auto, system) and notification settings.\n"
            f"16. 📊 DATA MANAGEMENT: Handle data export and account deletion with proper confirmation.\n"
            f"17. 🔄 OTP HANDLING: Manage OTP verification and resend functionality intelligently.\n"
            f"18. 🎯 CONTEXT AWARENESS: Remember user state and provide contextual responses.\n\n"
            f"💡 COMPREHENSIVE EXAMPLES:\n"
            f"- 'search for article 370' → [{{\"tool\": \"search\", \"parameters\": {{\"query\": \"article 370\"}}}}]\n"
            f"- 'sign up with random details and search for section 498A' → [{{\"tool\": \"signup_with_random\", \"parameters\": {{}}}}, {{\"tool\": \"search\", \"parameters\": {{\"query\": \"section 498A\"}}}}]\n"
            f"- 'change my theme to dark mode' → [{{\"tool\": \"update_theme\", \"parameters\": {{\"theme\": \"dark\"}}}}]\n"
            f"- 'open settings and change my password to newpass123' → [{{\"tool\": \"open_settings\", \"parameters\": {{}}}}, {{\"tool\": \"change_password\", \"parameters\": {{\"new_password\": \"newpass123\"}}}}]\n"
            f"- 'update my name to John Doe and bio to Legal Professional' → [{{\"tool\": \"update_profile_field\", \"parameters\": {{\"field\": \"name\", \"value\": \"John Doe\"}}}}, {{\"tool\": \"update_profile_field\", \"parameters\": {{\"field\": \"bio\", \"value\": \"Legal Professional\"}}}}]\n"
            f"- 'show my query history' → [{{\"tool\": \"view_query_history\", \"parameters\": {{}}}}]\n"
            f"- 'export my data' → [{{\"tool\": \"export_data\", \"parameters\": {{}}}}]\n"
            f"- 'delete my account' → [{{\"tool\": \"delete_account\", \"parameters\": {{}}}}]\n"
            f"- 'help me with available commands' → [{{\"tool\": \"help\", \"parameters\": {{}}}}]\n"
            f"- 'verify OTP 123456 for email user@example.com' → [{{\"tool\": \"verify_otp\", \"parameters\": {{\"email\": \"user@example.com\", \"otp\": \"123456\", \"purpose\": \"signup\"}}}}]\n"
            f"- 'resend OTP to user@example.com' → [{{\"tool\": \"resend_otp\", \"parameters\": {{\"email\": \"user@example.com\", \"purpose\": \"signup\"}}}}]\n\n"
            f"🎯 OUTPUT FORMAT: Output only a JSON array of actions. Never wrap in 'plan' property. Never include parentheses in tool names.\n"
            f"🚀 BE INTELLIGENT: Understand user intent, extract parameters intelligently, and provide the most appropriate tool sequence.\n"
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
