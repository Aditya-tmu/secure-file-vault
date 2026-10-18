
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError 
from dotenv import load_dotenv


load_dotenv()

ATLAS_URI = os.getenv("ATLAS_URI")
LOCAL_URI = os.getenv("LOCAL_URI")
DB_NAME = os.getenv("DB_NAME")


db = None
client = None


if ATLAS_URI:
    try:
        client = MongoClient(ATLAS_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping') 
        db = client[DB_NAME]
        print("Online: Atlas connected")
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Atlas connection failed: {e}. Falling back to local MongoDB.")
else:
    print("No ATLAS_URI found. Skipping Atlas connection.")


if db is None:
    try:
        client = MongoClient(LOCAL_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[DB_NAME]
        print("Offline: Local MongoDB connected")
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"FATAL: Could not connect to any database. Bummer. Error: {e}")
        db = None 



if db:
    users_col = db["users"]
    files_col = db["files"]
    logs_col = db["logs"]
else:
    
    users_col = None
    files_col = None
    logs_col = None

def get_db_collections():
    
    return db, users_col, files_col, logs_col
