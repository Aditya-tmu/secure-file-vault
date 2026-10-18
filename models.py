import hashlib
from datetime import datetime
from db import users_col, files_col, logs_col
import os
from security import generate_key

def hash_password(password: str) -> (bytes, bytes):
    """
    Hashes a password with PBKDF2.
    """
    return generate_key(password)

def verify_password(password: str, salt: bytes, password_hash: bytes) -> bool:
    """
    Verifies a password against a stored hash and salt.
    """
    key, _ = generate_key(password, salt)
    return key == password_hash

def hash_password_legacy(password: str) -> str:
    """
    Hashes a password with SHA-256 for legacy password verification.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def hash_hobby(hobby: str) -> str:
    """
    Hashes the hobby using SHA-256.
    """
    return hashlib.sha256(hobby.encode()).hexdigest()

def create_user(username: str, password: str, hobby: str) -> bool:
    """
    Adds a new user to the database with a salted and hashed password.
    """
    if users_col.find_one({"username": username}):
        return False

    password_hash, salt = hash_password(password)
    users_col.insert_one({
        "username": username,
        "password_hash": password_hash,
        "salt": salt,
        "hobby_hash": hash_hobby(hobby),
        "created_at": datetime.utcnow()
    })
    return True

def get_user_by_username(username: str) -> dict:
    """
    Fetches a user's data from the database.
    """
    return users_col.find_one({"username": username})

def update_password(username: str, new_password: str):
    """
    Updates a user's password with a new salt and hash.
    """
    new_password_hash, new_salt = hash_password(new_password)
    users_col.update_one(
        {"username": username},
        {"$set": {
            "password_hash": new_password_hash,
            "salt": new_salt
        }}
    )

def verify_user(username: str, password: str) -> bool:
    """
    Verifies a user's password, supporting both legacy and new hashing.
    """
    user = users_col.find_one({"username": username})
    if not user:
        return False

    if "salt" in user:
        # New user with salted password
        return verify_password(password, user["salt"], user["password_hash"])
    else:
        # Legacy user with unsalted SHA-256 password
        return user["password_hash"] == hash_password_legacy(password)

def add_file_metadata(owner: str, file_name: str, file_path: str, sha256_hash: str, salt: bytes = None):
    """
    Stores info about a file in the database.
    """
    files_col.insert_one({
        "owner": owner,
        "file_name": file_name,
        "file_path": file_path,
        "encrypted": False, # Files are not encrypted by default.
        "sha256_hash": sha256_hash,
        "salt": salt,
        "last_modified": datetime.utcnow()
    })

def update_file_status(file_path: str, encrypted: bool, new_hash: str = None, salt: bytes = None):
    """
    Updates a file's encryption status, hash and salt.
    """
    query = {"file_path": file_path}
    update = {
        "$set": {
            "encrypted": encrypted,
            "last_modified": datetime.utcnow()
        }
    }
    if new_hash:
        update["$set"]["sha256_hash"] = new_hash
    if salt:
        update["$set"]["salt"] = salt
        
    files_col.update_one(query, update)

def add_log(user: str, action: str, file_name: str = ""):
    """
    Logs an action, like 'login', 'encrypt', 'logout', etc.
    """
    logs_col.insert_one({
        "user": user,
        "action": action,
        "file_name": file_name,
        "timestamp": datetime.utcnow()
    })

def get_files_for_user(username: str) -> list:
    """
    Fetches all the files owned by a specific user.
    """
    return list(files_col.find({"owner": username}))

def get_logs_for_user(username: str) -> list:
    """
    Fetches all the logs for a specific user, most recent first.
    """
    return list(logs_col.find({"user": username}).sort("timestamp", -1))