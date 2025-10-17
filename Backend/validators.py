# validators.py

def validate_user(data):
    required_fields = ['name', 'email', 'password']
    for field in required_fields:
        if field not in data or not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"Missing or invalid field: {field}")

def validate_otp_code(data):
    required_fields = ['email', 'otp_code', 'expiry']
    if 'email' not in data or not isinstance(data['email'], str) or not data['email'].strip():
        raise ValueError("Missing or invalid field: email")
    if 'otp_code' not in data or not isinstance(data['otp_code'], str) or not data['otp_code'].strip():
        raise ValueError("Missing or invalid field: otp_code")
    if 'expiry' not in data:
        raise ValueError("Missing field: expiry")

def validate_query(data):
    required_fields = ['email', 'query', 'responses', 'timestamp']
    if 'email' not in data or not isinstance(data['email'], str) or not data['email'].strip():
        raise ValueError("Missing or invalid field: email")
    if 'query' not in data or not isinstance(data['query'], str) or not data['query'].strip():
        raise ValueError("Missing or invalid field: query")
    if 'responses' not in data or not isinstance(data['responses'], dict):
        raise ValueError("Missing or invalid field: responses")
    if 'timestamp' not in data:
        raise ValueError("Missing field: timestamp")
