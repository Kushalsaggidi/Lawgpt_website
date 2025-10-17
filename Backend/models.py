from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.lawgpt_db

users = db.users
queries = db.queries
otp_codes = db.otp_codes
