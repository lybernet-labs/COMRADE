import os
import sys
import json
import socket
import inspect
import threading
import subprocess
import importlib.util
from datetime import datetime

# --- COLOR SYSTEM FOR TERMINAL REPORT ---
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

class ComradeAuditor:
    def __init__(self):
        self.root_dir = os.getcwd()
        self.findings = []
        self.passed = 0
        self.warnings = 0
        self.critical = 0

    def log_result(self, category, check_name, status, message, fix_hint=""):
        if status == "PASS":
            self.passed += 1
            print(f"[{GREEN}PASS{RESET}] {BOLD}{category}{RESET} :: {check_name}")
            if message:
                print(f"       └── {message}")
        elif status == "WARN":
            self.warnings += 1
            print(f"[{YELLOW}WARN{RESET}] {BOLD}{category}{RESET} :: {check_name}")
            print(f"       └── {YELLOW}{message}{RESET}")
            if fix_hint:
                print(f"       └── {CYAN}Recommendation:{RESET} {fix_hint}")
        elif status == "FAIL":
            self.critical += 1
            print(f"[{RED}FAIL{RESET}] {BOLD}{category}{RESET} :: {check_name}")
            print(f"       └── {RED}{message}{RESET}")
            if fix_hint:
                print(f"       └── {CYAN}Fix Action:{RESET} {fix_hint}")

    def audit_environment(self):
        print(f"\n{BOLD}{'='*20} 1. ENVIRONMENT & RUNTIME AUDIT {'='*20}{RESET}")
        
        # Python Version
        py_ver = sys.version.split()[0]
        if sys.version_info >= (3, 10):
            self.log_result("ENVIRONMENT", "Python Runtime", "PASS", f"Running Python {py_ver}")
        else:
            self.log_result("ENVIRONMENT", "Python Runtime", "WARN", f"Python {py_ver} detected. 3.10+ recommended for CustomTkinter stability.")

        # Dependencies Check
        dependencies = ["customtkinter", "ollama"]
        for dep in dependencies:
            spec = importlib.util.find_spec(dep)
            if spec is not None:
                self.log_result("DEPENDENCY", f"Module '{dep}'", "PASS", "Module installed in active venv.")
            else:
                self.log_result("DEPENDENCY", f"Module '{dep}'", "FAIL", f"Missing python package '{dep}'.", f"Run: pip install {dep}")

        # Local Ollama binary check
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(["ollama", "--version"], capture_output=True, check=True, startupinfo=startupinfo)
            self.log_result("SUBPROCESS", "Ollama CLI Binary", "PASS", "Ollama engine binary detected on PATH.")
        except Exception:
            self.log_result("SUBPROCESS", "Ollama CLI Binary", "WARN", "Ollama binary not found on system PATH.", "Install Ollama from https://ollama.com if offline AI feature is required.")

    def audit_vault_security(self):
        print(f"\n{BOLD}{'='*20} 2. CRYPTOGRAPHY & VAULT STORAGE AUDIT {'='*20}{RESET}")
        
        vault_dir = os.path.join(self.root_dir, "vault")
        manifest_file = os.path.join(vault_dir, "manifest.json")

        if os.path.exists(vault_dir):
            self.log_result("STORAGE", "Vault Directory", "PASS", f"Located at {vault_dir}")
        else:
            self.log_result("STORAGE", "Vault Directory", "PASS", "Vault directory initialized on first file save.")

        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Check for plaintext disclosure risk
                self.log_result("SECURITY", "Manifest Data Structure", "WARN", 
                                f"Manifest stores {len(data)} entry mappings in readable JSON format.",
                                "Encrypt 'manifest.json' payload using master key derived salt to prevent local path inspection.")
            except json.JSONDecodeError:
                self.log_result("SECURITY", "Manifest Data Structure", "FAIL", "Manifest JSON file is corrupted or improperly formatted.", "Reset file content to {}")
        else:
            self.log_result("SECURITY", "Manifest Data Structure", "PASS", "No existing manifest file; fresh environment state.")

    def audit_code_safety(self):
        print(f"\n{BOLD}{'='*20} 3. SOURCE CODE SECURITY & THREADING AUDIT {'='*20}{RESET}")
        
        target_files = {
            "ui/app.py": os.path.join(self.root_dir, "ui", "app.py"),
            "core/file_manager.py": os.path.join(self.root_dir, "core", "file_manager.py"),
            "ai/engine.py": os.path.join(self.root_dir, "ai", "engine.py")
        }

        for label, file_path in target_files.items():
            if not os.path.exists(file_path):
                self.log_result("CODE INTEGRITY", label, "FAIL", f"File missing from expected directory path: {file_path}")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Specific static checks for known bugs/vulnerabilities
            if label == "ui/app.py":
                if 'weight="medium"' in code:
                    self.log_result("UI ENGINE", "Tkinter Font Weight", "FAIL", "Found weight='medium' causing Tkinter font warnings.", "Replace 'medium' with 'bold' or 'normal'")
                else:
                    self.log_result("UI ENGINE", "Tkinter Font Weight", "PASS", "No illegal weight values detected.")

                if 'global_comrade_ai' in code and '_ai_boot_in_progress' in code:
                    self.log_result("THREADING", "AI Engine Singleton", "PASS", "Singleton pattern & boot lock logic present.")
                else:
                    self.log_result("THREADING", "AI Engine Singleton", "WARN", "Missing AI engine singleton locks.", "Ensure ComradeAI is not instantiated repeatedly on background refreshes.")

            if label == "core/file_manager.py":
                if 'open(path, "wb"' in code or "open(path, 'wb'" in code:
                    self.log_result("SHREDDER", "Anti-Forensic File Mode", "WARN", "File shredder uses 'wb' mode which truncates size before byte overwrite.", "Change file mode in secure_wipe() to 'r+b'")
                else:
                    self.log_result("SHREDDER", "Anti-Forensic File Mode", "PASS", "File shredder uses in-place byte overwrite.")

            if label == "ai/engine.py":
                if "m['name']" in code:
                    self.log_result("AI CORE", "Ollama API Schema Parser", "FAIL", "Found direct m['name'] dictionary indexing.", "Use getattr(m, 'model', m.get('name')) to handle modern Ollama SDK objects.")
                else:
                    self.log_result("AI CORE", "Ollama API Schema Parser", "PASS", "Safe attribute/dictionary extraction logic present.")

    def audit_network_ports(self):
        print(f"\n{BOLD}{'='*20} 4. NETWORK & RELAY PORT AUDIT {'='*20}{RESET}")
        
        target_port = 6667
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        res = s.connect_ex(("127.0.0.1", target_port))
        s.close()

        if res == 0:
            self.log_result("NETWORK", f"IRC Relay Port ({target_port})", "PASS", "Relay port is ACTIVE and accepting connections.")
        else:
            self.log_result("NETWORK", f"IRC Relay Port ({target_port})", "WARN", f"Port {target_port} is not bound locally.", "Start local IRC sidecar server (e.g. Ergo) if Chat Room functionality is needed.")

    def run_all(self):
        print(f"\n{BOLD}{CYAN}{'='*15} COMRADE SYSTEM DIAGNOSTIC & AUDIT ENGINE {'='*15}{RESET}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Root Path: {self.root_dir}\n")

        self.audit_environment()
        self.audit_vault_security()
        self.audit_code_safety()
        self.audit_network_ports()

        print(f"\n{BOLD}{'='*20} AUDIT SUMMARY REPORT {'='*20}{RESET}")
        print(f"[{GREEN}PASS{RESET}] Checks Passed : {BOLD}{self.passed}{RESET}")
        print(f"[{YELLOW}WARN{RESET}] Warnings      : {BOLD}{self.warnings}{RESET}")
        print(f"[{RED}FAIL{RESET}] Critical Issues: {BOLD}{self.critical}{RESET}")
        
        if self.critical == 0 and self.warnings == 0:
            print(f"\n{GREEN}{BOLD}RESULT: SYSTEM HEALTHY & FULLY OPERATIONAL.{RESET}\n")
        elif self.critical == 0:
            print(f"\n{YELLOW}{BOLD}RESULT: SYSTEM OPERATIONAL WITH MINOR WARNINGS.{RESET}\n")
        else:
            print(f"\n{RED}{BOLD}RESULT: ACTION REQUIRED TO FIX CRITICAL CODE/RUNTIME ISSUES.{RESET}\n")

if __name__ == "__main__":
    auditor = ComradeAuditor()
    auditor.run_all()