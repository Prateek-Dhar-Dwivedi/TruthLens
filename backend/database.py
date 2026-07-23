from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

db = client["truthlens"]
users_collection = db["users"]
saved_collection = db["saved_checks"]
history_collection = db["history"]