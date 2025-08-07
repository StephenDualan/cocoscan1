import hashlib
import os

def hash_password(password):
    """Hash a password using SHA-256 with salt"""
    salt = os.urandom(32).hex()
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    try:
        salt, hash_value = hashed_password.split('$')
        hash_obj = hashlib.sha256((password + salt).encode())
        return hash_obj.hexdigest() == hash_value
    except:
        return False

def create_simple_hash(password):
    """Create a simple hash for development (not secure for production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_simple_hash(password, hashed_password):
    """Verify a simple hash for development"""
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password 