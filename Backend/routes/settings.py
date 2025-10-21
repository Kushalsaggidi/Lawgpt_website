from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import users, queries
from utils.security import generate_hash
from datetime import datetime

settings_bp = Blueprint('settings', __name__)


def _ensure_settings(user_doc: dict) -> dict:
    settings = user_doc.get("settings", {}) if user_doc else {}
    if "theme" not in settings:
        settings["theme"] = "auto"
    if "notifications" not in settings:
        settings["notifications"] = {"enabled": True}
    return settings


@settings_bp.route('/api/settings', methods=['GET'])
@jwt_required()
def get_settings():
    try:
        email = get_jwt_identity()
        user = users.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        settings = _ensure_settings(user)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": "Failed to load settings"}), 500


@settings_bp.route('/api/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    try:
        email = get_jwt_identity()
        payload = request.get_json() or {}
        updates = {}

        # Supported top-level settings
        if "theme" in payload:
            if payload["theme"] not in ["light", "dark", "auto"]:
                return jsonify({"error": "Invalid theme"}), 400
            updates["settings.theme"] = payload["theme"]

        # Notifications can be nested object
        if "notifications" in payload and isinstance(payload["notifications"], dict):
            for k, v in payload["notifications"].items():
                updates[f"settings.notifications.{k}"] = bool(v)

        if not updates:
            return jsonify({"error": "No valid settings provided"}), 400

        result = users.update_one({"email": email}, {"$set": updates})
        if result.modified_count == 0:
            return jsonify({"error": "Failed to update settings"}), 500
        
        return jsonify({"message": "Settings updated successfully"})
    except Exception as e:
        return jsonify({"error": "Failed to update settings"}), 500


@settings_bp.route('/api/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        email = get_jwt_identity()
        data = request.get_json() or {}
        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()
        
        if not current_password:
            return jsonify({"error": "Current password is required"}), 400
        
        if len(new_password) < 6:
            return jsonify({"error": "New password must be at least 6 characters long"}), 400
        
        if current_password == new_password:
            return jsonify({"error": "New password must be different from current password"}), 400
        
        # Get user and verify current password
        user = users.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password
        from utils.security import verify_password
        if not verify_password(current_password, user.get("password", "")):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Update password
        result = users.update_one(
            {"email": email}, 
            {"$set": {"password": generate_hash(new_password)}}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Failed to update password"}), 500
        
        return jsonify({"message": "Password changed successfully"})
    except Exception as e:
        return jsonify({"error": "Failed to change password"}), 500


@settings_bp.route('/api/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
    try:
        email = get_jwt_identity()
        data = request.get_json() or {}
        confirmation = data.get("confirmation", "").strip()
        
        if confirmation != "DELETE":
            return jsonify({"error": "Confirmation required. Type 'DELETE' to confirm."}), 400
        
        # Delete user and all their data
        user_result = users.delete_one({"email": email})
        queries_result = queries.delete_many({"email": email})
        
        if user_result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "message": "Account deleted successfully",
            "deleted_queries": queries_result.deleted_count
        })
    except Exception as e:
        return jsonify({"error": "Failed to delete account"}), 500


@settings_bp.route('/api/export-data', methods=['GET'])
@jwt_required()
def export_data():
    email = get_jwt_identity()
    
    # Get user data
    user = users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get user queries
    user_queries = list(queries.find({"email": email}))
    
    # Prepare export data (remove sensitive information)
    export_data = {
        "user_profile": {
            "name": user.get("name", ""),
            "email": user.get("email", ""),
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
    
    return jsonify(export_data)


