import socket
import threading
import uuid
import time

class ComradeComms:
    def __init__(self, server="127.0.0.1", port=6667, channel="#secure", ui_callback=None, encrypt_func=None, decrypt_func=None):
        self.server = server
        self.port = port
        self.channel = channel
        self.ui_callback = ui_callback
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        
        # Unique handle to prevent IRC collisions across multiple local client instances
        self.nickname = f"Node_{uuid.uuid4().hex[:5]}"
        self.secret_key = ""
        self.socket = None
        self.running = False

    def connect(self, secret_key="", nickname=None):
        """Establishes socket connection with optional handle and AES secret key."""
        if nickname and nickname.strip():
            self.nickname = f"{nickname.strip()}_{uuid.uuid4().hex[:3]}"
        
        self.secret_key = secret_key
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.server, self.port))
            self.socket.settimeout(None)  # Reset to blocking for background loop
            
            # Send standard IRC handshake
            self.socket.sendall(f"NICK {self.nickname}\r\n".encode('utf-8'))
            self.socket.sendall(f"USER {self.nickname} 0 * :Comrade Node\r\n".encode('utf-8'))
            
            time.sleep(0.3)
            self.socket.sendall(f"JOIN {self.channel}\r\n".encode('utf-8'))
            
            self.running = True
            threading.Thread(target=self._listen_loop, daemon=True).start()
            return True, "Connected to Stealth Relay"
        except Exception as e:
            self.running = False
            return False, f"Connection Failed: {str(e)}"

    def _listen_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    break
                
                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()  # Keep partial trailing payload line in buffer

                for line in lines:
                    if not line:
                        continue

                    # Server Keepalive Ping/Pong
                    if line.startswith("PING"):
                        ping_payload = line.split()[1] if len(line.split()) > 1 else ""
                        self.socket.sendall(f"PONG {ping_payload}\r\n".encode('utf-8'))
                        continue
                    
                    # Parse PRIVMSG chat payloads
                    if "PRIVMSG" in line:
                        try:
                            parts = line.split("PRIVMSG", 1)
                            raw_sender = parts[0].split("!")[0][1:]  # Extract sender handle
                            
                            # Filter out server headers, numerical codes, or system noise
                            if "." in raw_sender or raw_sender.isdigit():
                                continue

                            # Skip local self-echoes
                            if raw_sender == self.nickname:
                                continue
                                
                            raw_payload = parts[1].split(":", 1)[1]
                            
                            # Attempt decryption
                            if self.decrypt_func and self.secret_key:
                                try:
                                    msg = self.decrypt_func(raw_payload, self.secret_key)
                                except Exception:
                                    # Mismatching key or malformed data payload
                                    continue
                            else:
                                msg = raw_payload
                                
                            if self.ui_callback and msg:
                                self.ui_callback(f"[{raw_sender}]: {msg}")
                        except Exception:
                            continue

            except Exception:
                break
        self.running = False

    def send_message(self, message):
        """Encrypts and broadcasts message payload across local channel."""
        if not self.socket or not self.running:
            return False, "Not connected to relay."
        
        if not message.strip():
            return False, "Empty message."

        # Encrypt before sending
        if self.encrypt_func and self.secret_key:
            try:
                payload = self.encrypt_func(message, self.secret_key)
            except Exception as e:
                return False, f"Encryption failed: {str(e)}"
        else:
            payload = message

        try:
            irc_cmd = f"PRIVMSG {self.channel} :{payload}\r\n"
            self.socket.sendall(irc_cmd.encode('utf-8'))
            
            # Local reflection
            if self.ui_callback:
                self.ui_callback(f"[You]: {message}")
            return True, "Sent"
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        """Disconnects cleanly from Ergo daemon."""
        self.running = False
        if self.socket:
            try:
                self.socket.sendall(b"QUIT :Disconnecting Node\r\n")
                self.socket.close()
            except Exception:
                pass
            self.socket = None