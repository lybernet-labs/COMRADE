import ollama
import subprocess
import threading
import time
import os

class ComradeAI:
    def __init__(self, model_name="qwen2.5:1.5b"):
        """
        Initializes the offline AI engine core using local Ollama instances.
        Includes an autonomous background boot sequence.
        """
        self.model_name = model_name
        self.system_prompt = (
            "You are the COMRADE AI Core, an offline, zero-knowledge intelligence assistant "
            "integrated into a secure cyber-operations environment. Provide concise, "
            "accurate, and technically rigorous support. All operations are local-first."
        )
        self.conversation_history = []
        self._initialize_system_context()
        
        # Fire the autonomous setup sequence in a background thread
        threading.Thread(target=self._ignite_local_engine, daemon=True).start()

    def _ignite_local_engine(self):
        """Silently verifies the daemon, starts it if dead, and pulls missing models."""
        print("[SYSTEM]: Booting local AI inference engine...")
        
        # Windows-specific stealth mode for subprocesses (hides cmd popups)
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # 1. Verify Ollama Core Installation
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, check=True, startupinfo=startupinfo)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("[SYSTEM ERROR]: Ollama binary not found. You must install from https://ollama.com")
            return

        # 2. Awaken the Daemon if sleeping
        try:
            ollama.list()
        except Exception:
            print("[SYSTEM]: Daemon offline. Executing silent startup...")
            try:
                subprocess.Popen(
                    ["ollama", "serve"], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL, 
                    startupinfo=startupinfo
                )
                time.sleep(3) # Allow memory allocation buffer
            except Exception as e:
                print(f"[SYSTEM ERROR]: Daemon failed to ignite -> {e}")
                return

        # 3. Verify Model Assets & Pull if Missing (SAFE PARSING FIX)
        try:
            available = ollama.list()
            installed_models = []

            # Handle both list of Model objects (Ollama SDK v0.2+) and raw dicts
            raw_models = getattr(available, 'models', available.get('models', []) if isinstance(available, dict) else [])
            
            for m in raw_models:
                if isinstance(m, dict):
                    name = m.get('model') or m.get('name')
                else:
                    name = getattr(m, 'model', getattr(m, 'name', None))
                
                if name:
                    installed_models.append(str(name))

            if self.model_name not in installed_models and f"{self.model_name}:latest" not in installed_models:
                print(f"[SYSTEM]: Required neural weights '{self.model_name}' missing. Initiating background pull...")
                subprocess.run(
                    ["ollama", "pull", self.model_name], 
                    capture_output=True, 
                    startupinfo=startupinfo
                )
                print(f"[SYSTEM]: Weights '{self.model_name}' secured. Engine operational.")
            else:
                print("[SYSTEM]: AI Engine fully armed and operational.")
        except Exception as e:
            print(f"[SYSTEM ERROR]: Asset verification failed -> {e}")

    def _initialize_system_context(self):
        """Sets up the initial system boundary prompt."""
        self.conversation_history.append({
            'role': 'system',
            'content': self.system_prompt
        })

    def ask(self, prompt, system_context=None):
        """
        The core inference method required by both the GUI and CLI.
        Generates a response from the local model based on user input.
        """
        if system_context:
            self.conversation_history[0]['content'] = system_context

        self.conversation_history.append({'role': 'user', 'content': prompt})
        
        try:
            return self._standard_reply()
        except Exception as e:
            error_msg = (
                "[AI Engine Error]: Connection refused. \n\n"
                "If this is your first time booting, the system is likely downloading the "
                f"neural weights for '{self.model_name}' in the background. Please wait a moment and try again."
            )
            self.conversation_history.pop() # Prevent history corruption
            return error_msg

    def _standard_reply(self):
        """Handles non-streaming generation blocks."""
        response = ollama.chat(
            model=self.model_name,
            messages=self.conversation_history
        )
        
        # Safe extraction for response object
        if isinstance(response, dict):
            reply = response['message']['content']
        else:
            reply = response.message.content

        self.conversation_history.append({'role': 'assistant', 'content': reply})
        return reply

    def wipe_memory(self):
        """Clears the short-term conversation matrix, leaving only the system prompt."""
        self.conversation_history = []
        self._initialize_system_context()