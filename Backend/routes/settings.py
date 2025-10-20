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
    email = get_jwt_identity()
    user = users.find_one({"email": email})
    settings = _ensure_settings(user)
    return jsonify(settings)


@settings_bp.route('/api/settings', methods=['PUT'])
@jwt_required()
def update_settings():
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
        return jsonify({"message": "No valid settings provided"}), 400

    users.update_one({"email": email}, {"$set": updates})
    return jsonify({"message": "Settings updated"})


@settings_bp.route('/api/change-password', methods=['POST'])
@jwt_required()
def change_password():
    email = get_jwt_identity()
    data = request.get_json() or {}
    new_password = data.get("new_password", "").strip()
    if len(new_password) < 6:
        return jsonify({"error": "Password too short"}), 400
    users.update_one({"email": email}, {"$set": {"password": generate_hash(new_password)}})
    return jsonify({"message": "Password changed"})


@settings_bp.route('/api/delete-account', methods=['POST'])
@jwt_required()
def delete_account():
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


