import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from core.auth import derive_key

# --- YOUR ORIGINAL FILE ENCRYPTION LOGIC ---

def encrypt_data(data: bytes, password: str, salt: bytes) -> bytes:
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_data(encrypted_data: bytes, password: str, salt: bytes) -> bytes:
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

# --- THE NEW STRING WRAPPERS FOR IRC ---

def encrypt_text(plaintext: str, room_key: str) -> str:
    salt = os.urandom(16)
    raw_bytes = plaintext.encode('utf-8')
    encrypted_bytes = encrypt_data(raw_bytes, room_key, salt)
    payload = salt + encrypted_bytes
    return base64.b64encode(payload).decode('utf-8')

def decrypt_text(b64_payload: str, room_key: str) -> str:
    try:
        raw_payload = base64.b64decode(b64_payload)
        salt = raw_payload[:16]
        encrypted_bytes = raw_payload[16:]
        decrypted_bytes = decrypt_data(encrypted_bytes, room_key, salt)
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return "<Decryption Failed: Invalid Key or Corrupt Data>"