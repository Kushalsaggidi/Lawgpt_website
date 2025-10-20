from flask import Blueprint, request, jsonify
from models import users, queries
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

def _ensure_user_schema(user_email):
    """Ensure user has proper schema structure"""
    user = users.find_one({"email": user_email})
    if not user:
        return None
    
    # Add missing fields with defaults
    updates = {}
    if "bio" not in user:
        updates["bio"] = ""
    if "created_at" not in user:
        updates["created_at"] = datetime.utcnow()
    if "settings" not in user:
        updates["settings"] = {"theme": "auto", "notifications": {"enabled": True}}
    if "stats" not in user:
        updates["stats"] = {"totalQueries": 0, "favoriteModel": "LawGPT"}
    
    if updates:
        users.update_one({"email": user_email}, {"$set": updates})
        user.update(updates)
    
    return user

def _calculate_account_age(created_at):
    """Calculate account age in days"""
    if not created_at:
        return "0 days"
    
    delta = datetime.utcnow() - created_at
    days = delta.days
    
    if days == 0:
        return "Today"
    elif days == 1:
        return "1 day"
    elif days < 30:
        return f"{days} days"
    elif days < 365:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''}"

def _format_member_since(created_at):
    """Format member since date"""
    if not created_at:
        return "Unknown"
    return created_at.strftime("%B %Y")

@profile_bp.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_email = get_jwt_identity()
    user = _ensure_user_schema(user_email)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Calculate total queries from queries collection
    total_queries = queries.count_documents({"email": user_email})
    
    # Get stats with calculated values
    stats = user.get("stats", {})
    stats["totalQueries"] = total_queries
    stats["accountAge"] = _calculate_account_age(user.get("created_at"))
    stats["currentStreak"] = "7 days"  # Placeholder - could be calculated from query history
    
    return jsonify({
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "bio": user.get("bio", ""),
        "stats": stats,
        "memberSince": _format_member_since(user.get("created_at"))
    })

@profile_bp.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_email = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Prepare updates
    updates = {}
    if "name" in data:
        updates["name"] = data["name"]
    if "bio" in data:
        updates["bio"] = data["bio"]
    
    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Update user
    result = users.update_one({"email": user_email}, {"$set": updates})
    
    if result.modified_count == 0:
        return jsonify({'error': 'No changes made'}), 400
    
    return jsonify({'message': 'Profile updated successfully'})
