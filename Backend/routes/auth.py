from flask import Blueprint, request, jsonify
from models import users, otp_codes
from utils.security import generate_hash, check_hash, create_jwt, generate_otp
from utils.email import send_otp_email
from datetime import datetime, timedelta
from validators import validate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    try:
        validate_user(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    if users.find_one({"email": data['email']}):
        return jsonify({'error': 'Email already exists'}), 409
    hashed = generate_hash(data['password'])
    users.insert_one({
        "name": data['name'],
        "email": data['email'],
        "password": hashed
    })
    otp = generate_otp()
    otp_codes.insert_one({
        "email": data['email'],
        "otp_code": otp,
        "purpose": "signup",
        "expiry": datetime.utcnow() + timedelta(minutes=10)
    })
    # Send OTP to email
    try:
        send_otp_email(data['email'], otp)
    except Exception as e:
        return jsonify({'error': f'Could not send OTP: {e}'}), 500
    return jsonify({'message': 'Signup successful. OTP sent to your email.'}), 200

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password required.'}), 400
    user = users.find_one({"email": data['email']})
    if not user or not check_hash(data['password'], user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    otp = generate_otp()
    otp_codes.insert_one({
        "email": data['email'],
        "otp_code": otp,
        "purpose": "login",
        "expiry": datetime.utcnow() + timedelta(minutes=10)
    })
    try:
        send_otp_email(data['email'], otp)
    except Exception as e:
        return jsonify({'error': f'Could not send OTP: {e}'}), 500
    # This must always be here!
    return jsonify({'message': 'OTP sent to your email.'}), 200


@auth_bp.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    if 'email' not in data or 'otp' not in data or 'purpose' not in data:
        return jsonify({'error': 'Email, OTP, and purpose ("signup" or "login") required.'}), 400
    entry = otp_codes.find_one({
        "email": data['email'],
        "otp_code": data['otp'],
        "purpose": data['purpose']
    })
    if entry and entry['expiry'] > datetime.utcnow():
        otp_codes.delete_one({"_id": entry['_id']})
        if data['purpose'] == "login":
            token = create_jwt(data['email'])
            return jsonify({'message': 'Login successful', 'token': token, 'success': True}), 200
        return jsonify({'message': 'Signup OTP verified', 'success': True}), 200
    return jsonify({'error': 'Invalid/expired OTP', 'success': False}), 400


@auth_bp.route('/api/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    if 'email' not in data or 'purpose' not in data:
        return jsonify({'error': 'Email and purpose required.'}), 400
    otp = generate_otp()
    otp_codes.insert_one({
        "email": data['email'],
        "otp_code": otp,
        "purpose": data['purpose'],
        "expiry": datetime.utcnow() + timedelta(minutes=10)
    })
    # Send new OTP to email
    try:
        send_otp_email(data['email'], otp)
    except Exception as e:
        return jsonify({'error': f'Could not send OTP: {e}'}), 500
    return jsonify({'message': 'New OTP sent to your email.'}), 200


from flask_jwt_extended import jwt_required, get_jwt_identity

@auth_bp.route('/api/dashboard-data', methods=['GET'])
@jwt_required()
def dashboard_data():
    user_email = get_jwt_identity()
    # Fetch user-specific info, stats, queries, etc
    return jsonify({"msg": f"Welcome {user_email}, this is your dashboard data."})
