from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import users
from utils.security import check_hash, generate_hash
import re

agentic_bp = Blueprint('agentic', __name__)

@agentic_bp.route('/api/agentic-command', methods=['POST'])
def handle_agentic_command():
    """
    Handles agentic commands:
    - login email=abc@gmail.com password=123
    - signup email=abc@gmail.com password=123
    - search for article 370
    - login ... and search for ...
    """
    data = request.get_json()
    command = data.get('command', '').strip()
    result = {}

    # Parse login intent
    login_pattern = r'login.*email\s*=?\s*([\w@.+-]+).*pass(?:word)?\s*=?\s*([^\s]+)'
    login_match = re.search(login_pattern, command, re.IGNORECASE)

    # Parse signup intent
    signup_pattern = r'signup.*email\s*=?\s*([\w@.+-]+).*pass(?:word)?\s*=?\s*([^\s]+)'
    signup_match = re.search(signup_pattern, command, re.IGNORECASE)

    # Parse search/dashboard query
    search_pattern = r'search\s*(?:for)?\s*(.+)'
    search_match = re.search(search_pattern, command, re.IGNORECASE)

    # Execute signup
    if signup_match:
        email, password = signup_match.group(1).strip(), signup_match.group(2).strip()
        if users.find_one({"email": email}):
            result['signup'] = {
                "success": False,
                "message": "❌ Email already exists. Please login."
            }
        else:
            users.insert_one({
                "email": email,
                "password": hash_password(password) # securely hash!
            })
            token = create_access_token(identity=email)
            result['signup'] = {
                "success": True,
                "token": token,
                "message": f"✅ Signed up and logged in as {email}"
            }

    # Execute login
    if login_match:
        email, password = login_match.group(1).strip(), login_match.group(2).strip()
        user = users.find_one({"email": email})
        if user and check_hash(password, user['password']):
            token = create_access_token(identity=email)
            result['login'] = {
                "success": True,
                "token": token,
                "message": f"✅ Logged in as {email}"
            }
        else:
            result['login'] = {
                "success": False,
                "message": "❌ Invalid email or password"
            }
            return jsonify(result), 401

    # Execute search/dashboard query (only if logged in or just searching)
    if search_match:
        query_text = search_match.group(1).strip()
        # For full security, verify login/signup success before allowing query
        if 'login' in result and result['login']['success']:
            result['search'] = {
                "success": True,
                "query": query_text,
                "message": f"🔍 Searching for: {query_text}"
            }
        elif 'signup' in result and result['signup']['success']:
            result['search'] = {
                "success": True,
                "query": query_text,
                "message": f"🔍 Searching for: {query_text}"
            }
        elif not login_match and not signup_match:
            # Assume already logged in, or allow anonymous search (your choice)
            result['search'] = {
                "success": True,
                "query": query_text,
                "message": f"🔍 Searching for: {query_text}"
            }
        else:
            result['search'] = {
                "success": False,
                "message": "⚠️ Login/signup required before search"
            }

    if not result:
        result['error'] = "❌ Command not recognized. Try: login email=your@email.com password=yourpass OR signup OR search for ..."

    return jsonify(result), 200
