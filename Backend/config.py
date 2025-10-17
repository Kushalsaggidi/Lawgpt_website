import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/lawgpt_db")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_super_secret_flask_key")
