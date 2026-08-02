import json
import os
import base64
from core.encryption import encrypt_text, decrypt_text

CRED_FILE = ".comrade_credentials.json"

def load_credentials():
    if not os.path.exists(CRED_FILE):
        return {}
    try:
        with open(CRED_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_credentials(credentials_dict):
    try:
        with open(CRED_FILE, "w") as f:
            json.dump(credentials_dict, f, indent=4)
        return True
    except:
        return False

def encrypt_individual_pass(plain_password, item_key):
    try:
        cipher_output = encrypt_text(plain_password, item_key)
        
        # Explicitly tag bytes so we don't accidentally scramble strings later
        if isinstance(cipher_output, bytes):
            return "B64:" + base64.b64encode(cipher_output).decode('utf-8')
            
        return str(cipher_output)
    except Exception as e:
        print(f"[Crypto Error - Encrypt]: {e}")
        return None

def decrypt_individual_pass(cipher_text, item_key):
    try:
        # Only base64 decode if we explicitly tagged it
        if cipher_text.startswith("B64:"):
            cipher_data = base64.b64decode(cipher_text[4:].encode('utf-8'))
        else:
            cipher_data = cipher_text

        plain_output = decrypt_text(cipher_data, item_key)
        
        if not plain_output:
            return None
            
        if isinstance(plain_output, bytes):
            plain_output = plain_output.decode('utf-8')
            
        # STRICT FILTER: If your engine returns a warning string instead of crashing on a wrong key
        if isinstance(plain_output, str):
            lower_out = plain_output.lower()
            if any(err in lower_out for err in ["error", "fail", "invalid", "mac check", "incorrect"]):
                return None
                
        return plain_output
    except Exception as e:
        print(f"[Crypto Error - Decrypt]: {e}")
        return None