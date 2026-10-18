
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import os
SALT_SIZE = 16
ITERATIONS = 390000

def generate_key(password: str, salt: bytes = None) -> (bytes, bytes):
    
    if salt is None:
        salt = os.urandom(SALT_SIZE)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_file(input_path: str, output_path: str, password: str) -> bytes:
    
    key, salt = generate_key(password)
    f = Fernet(key)
    with open(input_path, "rb") as file:
        file_data = file.read()
    
    encrypted_data = f.encrypt(file_data)
    
    with open(output_path, "wb") as file:
        file.write(encrypted_data)
    
    os.remove(input_path) # Delete original file
    return salt

def decrypt_file(input_path: str, output_path: str, password: str, salt: bytes) -> bool:
    
    key, _ = generate_key(password, salt)
    f = Fernet(key)
    with open(input_path, "rb") as file:
        encrypted_data = file.read()
    
    try:
        decrypted_data = f.decrypt(encrypted_data)
        with open(output_path, "wb") as file:
            file.write(decrypted_data)
        
        os.remove(input_path) # Delete encrypted file
        return True
    except Exception:
        return False


def calculate_sha256(file_path: str) -> str:
    
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks, so we don't eat all the RAM.
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
