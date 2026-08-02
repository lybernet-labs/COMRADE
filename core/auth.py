import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a plain-text password into a 32-byte cryptographic key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000, 
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def generate_salt() -> bytes:
    """Generates a random 16-byte salt."""
    return os.urandom(16)
