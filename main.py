import sys
import os
import platform
import secrets
import string
import time
from colorama import Fore, Style, init

from cli.interface import display_banner, show_vault, get_password
from core.file_manager import save_file, extract_file, delete_vault_file, list_secured_files
from core.config import VAULT_DIR
from core.relay_manager import boot_stealth_relay
from ai.engine import ComradeAI

# Initialize terminal color engine
init(autoreset=True)

VAULT_HANDLE = None


def secure_wipe(file_path):
    """
    ANTI-FORENSIC SHREDDER:
    Overwrites file in-place with random cryptographic bits before deleting 
    to prevent forensic recovery on storage blocks.
    """
    if os.path.exists(file_path):
        try:
            size = os.path.getsize(file_path)
            if size > 0:
                with open(file_path, "r+b", buffering=0) as f:
                    f.write(secrets.token_bytes(size))
            os.remove(file_path)
        except Exception:
            try:
                os.remove(file_path)
            except Exception:
                pass


def apply_operational_lock():
    """Prevents multiple instances of the application from corrupting the vault."""
    global VAULT_HANDLE
    manifest_path = os.path.join(VAULT_DIR, ".vault_manifest")
    if os.path.exists(manifest_path):
        try:
            VAULT_HANDLE = open(manifest_path, "a")
            if platform.system() != "Windows":
                import fcntl
                fcntl.flock(VAULT_HANDLE, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (ImportError, IOError):
            pass


def release_lock():
    """Releases the system lock on the vault manifest."""
    global VAULT_HANDLE
    if VAULT_HANDLE:
        if platform.system() != "Windows":
            try:
                import fcntl
                fcntl.flock(VAULT_HANDLE, fcntl.LOCK_UN)
            except Exception:
                pass
        try:
            VAULT_HANDLE.close()
        except Exception:
            pass
        VAULT_HANDLE = None


def stream_response(text, delay=0.015):
    """Streams the AI response character-by-character for a tactical terminal feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def launch_gui():
    """Boot sequence for the primary graphical interface."""
    try:
        display_banner()
        print(f"{Fore.CYAN}[SYSTEM]: ENGAGING INTERNAL RELAY ENGINE...")
        relay_process, status = boot_stealth_relay()
        
        if not relay_process:
            print(f"{Fore.YELLOW}[SYSTEM WARNING]: Secure relay failed to start -> {status}")
        else:
            print(f"{Fore.GREEN}[SYSTEM]: Stealth Relay Engine Online.")
            
        from ui.app import ComradeApp
        app = ComradeApp()
        app.mainloop()
    except Exception as e:
        print(f"{Fore.RED}GUI Fatal Error: {e}")


def main():
    apply_operational_lock()
    
    # Parse positional arguments
    args = sys.argv[1:]
    
    # Default trigger: If no arguments provided, launch GUI
    if not args:
        launch_gui()
        return

    command = args[0].lower()

    # ==========================================
    # ROUTE: COMRADE RUN [SUBSYSTEM]
    # ==========================================
    if command == "run":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ SYNTAX ERROR: 'run' requires a subsystem target.")
            print(f"{Fore.YELLOW}Valid targets: {Fore.WHITE}gui, ai, securepass, chat")
            return
            
        subsystem = args[1].lower()
        
        if subsystem == "gui":
            launch_gui()
            
        elif subsystem == "securepass":
            display_banner()
            print(f"{Fore.CYAN}🔐 Accessing Secure Local Credential Vault...")
            try:
                from core.credentials import load_credentials, save_credentials, decrypt_individual_pass, encrypt_individual_pass
                import getpass
                import tkinter as tk
                import shutil
                import json
                
                creds = load_credentials()
                
                if not creds:
                    print(f"{Fore.YELLOW}[!] Credential database is currently empty.")
                else:
                    print(f"\n{Fore.CYAN}=== SECURED ACCOUNTS AVAILABLE ===")
                    accounts = sorted(list(creds.keys()))
                    for idx, account in enumerate(accounts, 1):
                        print(f" {Fore.WHITE}[{idx}] {account}")
                    print(f"{Fore.CYAN}==================================")
                
                prompt_text = f"\n{Fore.YELLOW}Enter item number, [A]dd, [D]elete, [B]ackup, [R]estore, or [C]ancel: {Fore.WHITE}"
                choice = input(prompt_text).strip()
                
                if choice.lower() == 'c' or not choice:
                    return
                    
                # CLI LOGIC: ADD / GENERATE
                elif choice.lower() == 'a':
                    print(f"\n{Fore.CYAN}--- DEPLOY SECURE ASSET ---")
                    acc = input(f"{Fore.WHITE}Account / Service Label: ").strip()
                    if not acc:
                        print(f"{Fore.RED}❌ Aborted. Label required.")
                        return
                    
                    item_key = getpass.getpass(f"{Fore.YELLOW}Dedicated Encryption Key (Hidden): {Fore.WHITE}")
                    if not item_key:
                        print(f"{Fore.RED}❌ Aborted. Encryption key required.")
                        return
                    
                    gen_choice = input(f"{Fore.WHITE}Type [G] to Autogenerate a 20-bit payload, or hit Enter to type your own: ").strip()
                    
                    if gen_choice.lower() == 'g':
                        alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
                        while True:
                            pwd = ''.join(secrets.choice(alphabet) for _ in range(20))
                            if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd) 
                                    and sum(c.isdigit() for c in pwd) >= 2 and any(c in "!@#$%^&*-_=+" for c in pwd)):
                                break
                        print(f"{Fore.GREEN}⚡ High-Entropy Payload Generated.")
                    else:
                        pwd = getpass.getpass(f"{Fore.WHITE}Enter Password Payload (Hidden): ")
                    
                    enc_payload = encrypt_individual_pass(pwd, item_key)
                    if not enc_payload:
                        print(f"{Fore.RED}❌ Crypto calculation failed.")
                        return
                    
                    creds[acc] = enc_payload
                    if save_credentials(creds):
                        print(f"\n{Fore.GREEN}✅ SUCCESS: [{acc}] encrypted and committed to vault.")
                    else:
                        print(f"\n{Fore.RED}❌ SYSTEM ERROR: Failed to commit to disk.")
                    return

                # CLI LOGIC: DELETE / DESTROY
                elif choice.lower() == 'd':
                    print(f"\n{Fore.RED}--- DESTROY SECURE ASSET ---")
                    del_choice = input(f"{Fore.WHITE}Enter the item number to delete: ").strip()
                    try:
                        idx = int(del_choice) - 1
                        accounts = sorted(list(creds.keys()))
                        if 0 <= idx < len(accounts):
                            target_account = accounts[idx]
                            encrypted_payload = creds[target_account]
                            
                            item_key = getpass.getpass(f"{Fore.YELLOW}Verify dedicated key for [{target_account}] to authorize wipe: {Fore.WHITE}")
                            plain_pass = decrypt_individual_pass(encrypted_payload, item_key)
                            
                            if not plain_pass:
                                print(f"{Fore.RED}❌ Access Denied. Cryptographic mismatch. Deletion blocked.")
                                return
                                
                            confirm = input(f"{Fore.RED}WARNING: Permanently wipe [{target_account}]? (y/n): {Fore.WHITE}").strip()
                            if confirm.lower() == 'y':
                                del creds[target_account]
                                if save_credentials(creds):
                                    print(f"\n{Fore.GREEN}✅ SUCCESS: [{target_account}] permanently erased.")
                                else:
                                    print(f"\n{Fore.RED}❌ SYSTEM ERROR: Failed to commit database changes.")
                            else:
                                print(f"\n{Fore.YELLOW}Deletion aborted.")
                        else:
                            print(f"{Fore.RED}❌ Index out of operational bounds.")
                    except ValueError:
                        print(f"{Fore.RED}❌ Invalid input format.")
                    return

                # CLI LOGIC: BACKUP
                elif choice.lower() == 'b':
                    print(f"\n{Fore.CYAN}--- EXPORT ENCRYPTED VAULT ---")
                    dest_path = input(f"{Fore.WHITE}Enter destination directory path (e.g., D:\\Backups): ").strip()
                    if not os.path.exists(dest_path):
                        print(f"{Fore.RED}❌ Path does not exist. Aborting.")
                        return
                    
                    backup_file = os.path.join(dest_path, "comrade_backup.json")
                    try:
                        shutil.copy(".comrade_credentials.json", backup_file)
                        print(f"\n{Fore.GREEN}✅ BACKUP SUCCESS: State exported securely to:\n{backup_file}")
                    except Exception as e:
                        print(f"\n{Fore.RED}❌ BACKUP FAILED: {e}")
                    return

                # CLI LOGIC: RESTORE
                elif choice.lower() == 'r':
                    print(f"\n{Fore.CYAN}--- IMPORT ENCRYPTED VAULT ---")
                    src_path = input(f"{Fore.WHITE}Enter full path to backup file: ").strip()
                    if not os.path.exists(src_path) or not src_path.endswith(".json"):
                        print(f"{Fore.RED}❌ Invalid file or path. Aborting.")
                        return
                    
                    try:
                        with open(src_path, "r") as f:
                            imported_data = json.load(f)
                        
                        creds.update(imported_data)
                        if save_credentials(creds):
                            print(f"\n{Fore.GREEN}✅ RESTORE SUCCESS: Cryptographic elements merged smoothly.")
                        else:
                            print(f"\n{Fore.RED}❌ RESTORE FAILED: Could not commit merged data.")
                    except Exception as e:
                        print(f"\n{Fore.RED}❌ RESTORE FAILED: Corrupted JSON or read error -> {e}")
                    return
                
                # CLI LOGIC: RETRIEVE / DECRYPT
                else:
                    try:
                        idx = int(choice) - 1
                        accounts = sorted(list(creds.keys()))
                        if 0 <= idx < len(accounts):
                            target_account = accounts[idx]
                            encrypted_payload = creds[target_account]
                            
                            item_key = getpass.getpass(f"{Fore.CYAN}Enter dedicated encryption key for [{target_account}]: {Fore.WHITE}")
                            plain_pass = decrypt_individual_pass(encrypted_payload, item_key)
                            
                            if not plain_pass:
                                print(f"{Fore.RED}❌ Access Denied. Cryptographic mismatch or invalid key.")
                                return
                                
                            r = tk.Tk()
                            r.withdraw()
                            r.clipboard_clear()
                            r.clipboard_append(plain_pass)
                            r.update()
                            
                            print(f"\n{Fore.GREEN}✅ Payload for {target_account} decrypted and copied to clipboard.")
                            print(f"{Fore.RED}⚠️ Clipboard will self-destruct in 10 seconds.")
                            
                            time.sleep(10)
                            r.clipboard_clear()
                            r.clipboard_append("")
                            r.update()
                            r.destroy()
                            print(f"{Fore.GREEN}🛡️ Clipboard memory purged.")
                        else:
                            print(f"{Fore.RED}❌ Index out of operational bounds.")
                    except ValueError:
                        print(f"{Fore.RED}❌ Invalid input format.")
            except Exception as e:
                print(f"{Fore.RED}❌ Terminal interaction faulted -> {e}")

        elif subsystem == "ai":
            display_banner()
            print(f"{Fore.CYAN}🤖 COMRADE AI SYSTEM [OFFLINE & SECURE]")
            print(f"{Fore.YELLOW}Type 'exit' or 'quit' to terminate the session.\n")
            
            ai_engine = ComradeAI()
            system_prompt = "You are COMRADE, an advanced cyber-operations AI. Keep answers concise, tactical, and highly technical."
            
            while True:
                try:
                    user_input = input(f"{Fore.CYAN}YOU: {Fore.WHITE}")
                    
                    if user_input.lower() in ['exit', 'quit']:
                        ai_engine.wipe_memory()
                        print(f"{Fore.CYAN}Terminating AI Subsystem & wiping memory...{Fore.RESET}")
                        break
                    
                    sys.stdout.write(f"{Fore.CYAN}Processing...{Fore.RESET}")
                    sys.stdout.flush()
                    
                    response = ai_engine.ask(user_input, system_context=system_prompt)
                    
                    sys.stdout.write("\r" + " " * 20 + "\r")
                    sys.stdout.flush()
                    
                    print(f"{Fore.GREEN}COMRADE: {Fore.WHITE}", end="")
                    stream_response(response)
                    print(f"\n{Fore.CYAN}" + "─" * 60 + "\n")
                    
                except KeyboardInterrupt:
                    ai_engine.wipe_memory()
                    print(f"\n{Fore.CYAN}Session aborted. Memory flushed.{Fore.RESET}")
                    break

        elif subsystem == "chat":
            display_banner()
            print(f"{Fore.CYAN}📡 COMRADE STEALTH RELAY CHAT [PORT 6667]")
            
            import socket
            import threading

            nick = input(f"{Fore.YELLOW}Enter Operator Nickname: {Fore.WHITE}").strip()
            if not nick:
                nick = f"Operator_{secrets.token_hex(2)}"

            channel = input(f"{Fore.YELLOW}Enter Secure Channel [#secure]: {Fore.WHITE}").strip()
            if not channel:
                channel = "#secure"
            if not channel.startswith("#"):
                channel = f"#{channel}"

            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(("127.0.0.1", 6667))

                client.sendall(f"NICK {nick}\r\n".encode("utf-8"))
                client.sendall(f"USER {nick} 0 * :{nick}\r\n".encode("utf-8"))
                client.sendall(f"JOIN {channel}\r\n".encode("utf-8"))

                print(f"{Fore.GREEN}✅ Connected to Relay. Joined {channel} as {nick}.")
                print(f"{Fore.YELLOW}Type your message and press ENTER. Type 'exit' to disconnect.\n")

                stop_event = threading.Event()

                def receive_loop():
                    while not stop_event.is_set():
                        try:
                            data = client.recv(2048).decode("utf-8", errors="ignore")
                            if not data:
                                break
                            lines = data.split("\r\n")
                            for line in lines:
                                if line.startswith("PING"):
                                    client.sendall(f"PONG {line.split()[1]}\r\n".encode("utf-8"))
                                elif "PRIVMSG" in line:
                                    parts = line.split(" PRIVMSG ")
                                    sender = parts[0].split("!")[0][1:]
                                    msg = parts[1].split(" :", 1)[1]
                                    if sender != nick:
                                        print(f"\n{Fore.GREEN}[{channel}] {sender}: {Fore.WHITE}{msg}")
                                        sys.stdout.write(f"{Fore.CYAN}[{nick}] > {Fore.WHITE}")
                                        sys.stdout.flush()
                        except Exception:
                            break

                t = threading.Thread(target=receive_loop, daemon=True)
                t.start()

                while True:
                    msg = input(f"{Fore.CYAN}[{nick}] > {Fore.WHITE}")
                    if msg.lower() in ["exit", "quit", "/quit"]:
                        stop_event.set()
                        client.sendall(b"QUIT :Disconnecting\r\n")
                        client.close()
                        print(f"{Fore.YELLOW}Disconnected from relay.")
                        break
                    if msg.strip():
                        client.sendall(f"PRIVMSG {channel} :{msg}\r\n".encode("utf-8"))

            except Exception as e:
                print(f"{Fore.RED}❌ Relay Connection Failed -> {e}")
                print(f"{Fore.YELLOW}Ensure Ergo daemon is running: .\\ergo.exe run")

        else:
            display_banner()
            print(f"{Fore.RED}❌ Unknown subsystem: {subsystem}")
            print(f"{Fore.YELLOW}Valid targets: {Fore.WHITE}gui, ai, securepass, chat")

    # ==========================================
    # ROUTE: FILE VAULT OPERATIONS
    # ==========================================
    elif command == "secure":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ SYNTAX ERROR: File path required. Example: python main.py secure document.pdf")
            return
            
        display_banner()
        password = get_password("CREATE MASTER KEY FOR THIS ASSET: ")
        try:
            original_path = args[1]
            name = save_file(original_path, password)
            secure_wipe(original_path)
            apply_operational_lock() 
            print(f"\n{Fore.GREEN}✅ Secured as: {name} {Fore.WHITE}(Original File Wiped)")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}")

    elif command == "list":
        display_banner()
        files = list_secured_files()
        if not files:
            print(f"{Fore.YELLOW}[!] Vault is empty.")
        else:
            show_vault(files)

    elif command == "extract":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ SYNTAX ERROR: Vault ID required. Example: python main.py extract a1b2c3d4")
            return
            
        display_banner()
        password = get_password("ENTER MASTER KEY TO UNLOCK ASSET: ")
        try:
            path = extract_file(args[1], password)
        except Exception:
            print(f"{Fore.RED}❌ Denied: Invalid Key.")
            return

        print(f"{Fore.CYAN}🧹 Finalizing extraction: Shredding vault residue...")
        try:
            release_lock()  
            delete_vault_file(args[1], password)
            apply_operational_lock() 
        except Exception as cleanup_error:
            apply_operational_lock() 
            print(f"{Fore.YELLOW}[!] Cleanup Warning: Could not purge footprint safely ({cleanup_error})")
            
        print(f"\n{Fore.GREEN}✅ Restored to: {path}")

    elif command == "remove":
        if len(args) < 2:
            display_banner()
            print(f"{Fore.RED}❌ SYNTAX ERROR: Vault ID required.")
            return
            
        display_banner()
        print(f"{Fore.RED}⚠️ AUTHORIZATION REQUIRED")
        password = get_password("ENTER MASTER KEY TO AUTHORIZE WIPE: ")
        if password:
            try:
                release_lock()
                delete_vault_file(args[1], password)
                apply_operational_lock()
                print(f"\n{Fore.GREEN}🗑️ Asset {args[1]} permanently erased.")
            except Exception as e:
                apply_operational_lock()
                print(f"\n{Fore.RED}❌ Denied: {e}")

    else:
        display_banner()
        print(f"{Fore.RED}❌ ERROR: Command protocol '{command}' not recognized.")
        print(f"\n{Fore.YELLOW}Valid Command Protocols:")
        print(f"  {Fore.WHITE}python main.py run <gui | ai | securepass | chat>")
        print(f"  {Fore.WHITE}python main.py list")
        print(f"  {Fore.WHITE}python main.py secure <file_path>")
        print(f"  {Fore.WHITE}python main.py extract <vault_id>")
        print(f"  {Fore.WHITE}python main.py remove <vault_id>")


if __name__ == "__main__":
    main()