import pytest
import hashlib

def test_key_consistency():
    """Ensures the same password always produces the same key."""
    password = "secure_password_123"
    salt = b'constant_salt_for_testing'
    
    key_1 = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    key_2 = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    assert key_1 == key_2
    assert len(key_1) == 32 

def test_wrong_password_fails():
    """Logic check: different passwords must produce different keys."""
    key_a = hashlib.pbkdf2_hmac('sha256', b"pass1", b"salt", 1000)
    key_b = hashlib.pbkdf2_hmac('sha256', b"pass2", b"salt", 1000)
    
    assert key_a != key_b
