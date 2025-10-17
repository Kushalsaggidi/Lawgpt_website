from flask import Blueprint, request, jsonify
from models import users
from flask_jwt_extended import jwt_required, get_jwt_identity

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = users.find_one({"email": get_jwt_identity()})
    return jsonify({
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "bio": user.get("bio", ""),
        "stats": user.get("stats", {})
    })

@profile_bp.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    data = request.get_json()
    users.update_one({"email": get_jwt_identity()}, {"$set": {"name": data['name'], "bio": data['bio']}})
    return jsonify({'message': 'Profile updated'})
