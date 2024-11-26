import hashlib

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verifies the password by comparing the hashed version of the provided password."""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()
