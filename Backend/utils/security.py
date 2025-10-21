from bson.binary import Binary

import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta
import random


def generate_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_hash(password, hash_val):
    # Works whether hash_val is bytes or bson.binary.Binary
    if isinstance(hash_val, Binary):
        hash_val = bytes(hash_val)
    return bcrypt.checkpw(password.encode('utf-8'), hash_val)

def verify_password(password, hash_val):
    """Alias for check_hash for better readability"""
    return check_hash(password, hash_val)


def create_jwt(email):
    return create_access_token(identity=email, expires_delta=timedelta(hours=24))

def generate_otp():
    return str(random.randint(100000, 999999))
