import os
import json
import platform
import secrets
import ctypes
import subprocess

from core.encryption import encrypt_data, decrypt_data
from core.auth import generate_salt
from core.config import VAULT_DIR, VAULT_EXTENSION, MANIFEST_PATH

def secure_wipe(path):
    """
    ANTI-FORENSIC SHREDDER:
    Physically overwrites the file with random bits before deletion.
    """
    if os.path.exists(path):
        try:
            unlock_for_writing(path)
            size = os.path.getsize(path)
            # CHANGED: "wb" -> "r+b" (Overwrites existing bytes in-place without premature truncation)
            with open(path, "r+b", buffering=0) as f:
                f.write(secrets.token_bytes(size))
            os.remove(path)
        except Exception:
            try:
                os.remove(path)
            except Exception:
                pass

def hide_vault_folder(path):
    """
    STEALTH MODULE (Ghost Mode):
    Windows: Sets Hidden (0x02) + System (0x04) attributes.
    Linux/Mac: Sets permissions to 700 (Owner-only).
    """
    if not os.path.exists(path):
        return

    abs_path = os.path.abspath(path)

    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x02 | 0x04)
            subprocess.run(['attrib', '+s', '+h', abs_path, '/s', '/d'], 
                           check=False, capture_output=True)
        except Exception:
            pass
    else:
        try:
            os.chmod(abs_path, 0o700)
        except Exception:
            pass

def unlock_for_writing(path):
    """Removes 'System' and 'Hidden' protections to allow modification."""
    if not os.path.exists(path):
        return

    abs_path = os.path.abspath(path)

    if platform.system() == "Windows":
        try:
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 0x80) 
            subprocess.run(['attrib', '-s', '-h', abs_path, '/s', '/d'], 
                           check=False, capture_output=True)
        except Exception:
            pass
    else:
        try:
            os.chmod(abs_path, 0o700)
        except Exception:
            pass

def load_manifest():
    """Safely loads and returns the manifest dictionary."""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}

def save_manifest(manifest):
    """Safely commits the manifest dictionary to disk with stealth permissions."""
    try:
        unlock_for_writing(MANIFEST_PATH)
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4)
        hide_vault_folder(MANIFEST_PATH)
        return True
    except Exception as e:
        print(f"[CORE ERROR] Manifest save failed: {e}")
        return False

def save_file(file_path, password):
    """Encrypts, moves to Hidden folder, and shreds original."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR, mode=0o700, exist_ok=True)
    
    hide_vault_folder(VAULT_DIR)
    abs_original_path = os.path.abspath(file_path)

    with open(file_path, 'rb') as f:
        data = f.read()

    salt = generate_salt()
    encrypted_content = encrypt_data(data, password, salt)
    
    vault_filename = f"idx_{os.urandom(4).hex()}{VAULT_EXTENSION}"
    vault_path = os.path.join(VAULT_DIR, vault_filename)

    with open(vault_path, 'wb') as f:
        f.write(salt + encrypted_content)

    hide_vault_folder(vault_path)

    manifest = load_manifest()
    manifest[vault_filename] = abs_original_path 
    save_manifest(manifest)
    
    secure_wipe(file_path)
    return vault_filename

def extract_file(vault_id, password):
    """Decrypts and restores the file to its original absolute path."""
    manifest = load_manifest()
    
    # Allow matching with or without standard extension
    target_key = vault_id
    if target_key not in manifest and not target_key.endswith(VAULT_EXTENSION):
        target_key = f"{vault_id}{VAULT_EXTENSION}"
        
    if target_key not in manifest:
        raise Exception("Asset signature not found in manifest.")

    vault_path = os.path.join(VAULT_DIR, target_key)
    if not os.path.exists(vault_path):
        raise FileNotFoundError("Vault payload missing from disk.")

    with open(vault_path, 'rb') as f:
        salt = f.read(16)
        encrypted_content = f.read()

    decrypted_data = decrypt_data(encrypted_content, password, salt)
    
    target_path = manifest[target_key]
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    with open(target_path, 'wb') as f:
        f.write(decrypted_data)
    
    secure_wipe(vault_path)
    
    del manifest[target_key]
    save_manifest(manifest)

    return target_path

def delete_vault_file(vault_id, password):
    """Authorized deletion: requires password to shred a vault asset."""
    if not password:
        raise Exception("Authorization required.")

    manifest = load_manifest()
    
    target_key = vault_id
    if target_key not in manifest and not target_key.endswith(VAULT_EXTENSION):
        target_key = f"{vault_id}{VAULT_EXTENSION}"

    if target_key not in manifest:
        raise Exception("Target not found in manifest.")
        
    vault_path = os.path.join(VAULT_DIR, target_key)
    
    # Verify key by attempting decryption before destroying
    if os.path.exists(vault_path):
        with open(vault_path, 'rb') as f:
            salt = f.read(16)
            encrypted_content = f.read()
        decrypt_data(encrypted_content, password, salt)
        secure_wipe(vault_path)
    
    del manifest[target_key]
    save_manifest(manifest)
    return True

def list_secured_files():
    """Reads real vault items directly from the system manifest."""
    try:
        manifest = load_manifest()
        cleaned_assets = []

        for vault_file, orig_path in manifest.items():
            # Ensure physical payload exists in vault
            v_path = os.path.join(VAULT_DIR, vault_file)
            if os.path.exists(v_path):
                cleaned_assets.append({
                    'vault_name': str(vault_file),
                    'original_name': str(os.path.basename(orig_path))
                })

        return cleaned_assets
    except Exception as e:
        print(f"[CORE ERROR] Vault list parsing failed: {e}")
        return []