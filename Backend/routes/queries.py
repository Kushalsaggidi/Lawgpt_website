from flask import Blueprint, jsonify
from models import queries
from flask_jwt_extended import jwt_required, get_jwt_identity

queries_bp = Blueprint('queries', __name__)

@queries_bp.route('/api/queries', methods=['GET'])
@jwt_required()
def get_queries():
    user_email = get_jwt_identity()
    items = list(queries.find({"email": user_email}))
    out = [{"query": item["query"], "responses": item["responses"], "timestamp": item["timestamp"]} for item in items]
    return jsonify(out)
