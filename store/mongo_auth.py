"""
MongoDB Authentication Utility
Handles all user auth operations (register, login, logout) via MongoDB Atlas.
"""

import os
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://fauziakhan7266_db_user:dopamine102712@cluster0.bkm1kgq.mongodb.net/?appName=Cluster0")

_client = None

def get_db():
    """Return a MongoDB database handle (lazy singleton)."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client["aura_store"]


def get_users_collection():
    return get_db()["users"]


# ──────────────────────────────────────────────
#  Register
# ──────────────────────────────────────────────
def register_user(username: str, email: str, password: str) -> dict:
    """
    Create a new user document in MongoDB.
    Returns {'success': True, 'user_id': str} or {'success': False, 'error': str}.
    """
    col = get_users_collection()

    if col.find_one({"username": username}):
        return {"success": False, "error": "Username already taken."}

    if col.find_one({"email": email}):
        return {"success": False, "error": "Email already registered."}

    hashed = make_password(password)   # uses Django's PBKDF2 hasher
    doc = {
        "username": username,
        "email": email,
        "password": hashed,
        "created_at": datetime.utcnow(),
        "is_active": True,
    }
    result = col.insert_one(doc)
    return {"success": True, "user_id": str(result.inserted_id)}


# ──────────────────────────────────────────────
#  Login
# ──────────────────────────────────────────────
def authenticate_user(username: str, password: str) -> dict | None:
    """
    Verify credentials.
    Returns user document (as dict, _id converted to str) or None if invalid.
    """
    col = get_users_collection()
    user = col.find_one({"username": username, "is_active": True})
    if user and check_password(password, user["password"]):
        user["_id"] = str(user["_id"])   # make it JSON-safe
        return user
    return None


# ──────────────────────────────────────────────
#  Fetch by ID
# ──────────────────────────────────────────────
def get_user_by_id(user_id: str) -> dict | None:
    from bson import ObjectId
    col = get_users_collection()
    user = col.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
    return user
