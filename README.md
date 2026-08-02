<div align="center">

```text

   ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗
  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝
  ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║   ██║█████╗  
  ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║   ██║██╔══╝  
  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗
   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
=====================================================================================
   Cyber Operations Module for Resilient Authentication, Defense and Encryption
   comrade-V1.20 | DESIGNED BY MOHAMMED REHAN { Github_id :- zfln-rehan0520 }
=====================================================================================
```

  ![Version](https://img.shields.io/badge/version-1.10-ff8c00?style=for-the-badge)
  ![License](https://img.shields.io/badge/license-Apache--2.0-white?style=for-the-badge)
  ![Python](https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&logo=python)
  ![Security](https://img.shields.io/badge/encryption-AES--256--GCM-00ffff?style=for-the-badge)
  ![Audit](https://img.shields.io/badge/audit-100%25%20PASS-brightgreen?style=for-the-badge)

  <p align="center">
    COMRADE is a high-security, local-first cyber-operations platform engineered for developers, security researchers, and privacy advocates. 
    By leveraging AES-256-GCM authenticated encryption, zero-knowledge credential storage, offline AI intelligence, and a sidecar IRC relay daemon, 
    COMRADE ensures your sensitive assets and communications remain mathematically inaccessible to unauthorized entities.
  </p>
</div>

---

## 🛠️ Core Features

* **Zero-Knowledge Vault Architecture**: Encryption and decryption occur strictly in memory via AES-256-GCM and Scrypt KDF. Master keys reside solely in volatile RAM and are never written to disk.
* **Kernel Stealth (Ghost Mode)**: On Windows, utilizes `SetFileAttributesW` to flag the stealth vault as a **System Protected** component—invisible even if "Show Hidden Files" is enabled.
* **Anti-Forensic Wiping**: Implements a secure-erase protocol where source assets are overwritten in-place with high-entropy cryptographic random bytes (`secrets.token_bytes`) before physical deletion.
* **Offline AI Intelligence Assistant**: Driven locally via Ollama (`qwen2.5:1.5b`), enabling private context reasoning, code audits, and operational assistance without sending telemetry out of network boundaries.
* **Stealth Sidecar IRC Relay**: Built-in end-to-end encrypted chat interface connecting locally to an Ergo IRC daemon (`127.0.0.1:6667`) for private channel communications.
* **Zero-Knowledge Password Manager**: Encrypted local credential database featuring high-entropy 20-bit password generation, encrypted JSON backups, and self-destructing 10-second clipboard memory.
* **Operational Integrity & Process Locks**: Employs cross-platform file locks (`fcntl` on Linux/macOS, handles on Windows) to prevent concurrent instances from corrupting vault manifests.

---

## 📁 Project Structure

```text
COMRADE/
├── ai/                         # Offline Neural Inference Engine (Ollama API Adapter)
├── bin/                        # Binary Executables & Auxiliary Helpers
├── cli/                        # Terminal Interface Layer & Custom ASCII Banners
├── comrade.egg-info/           # Python Package Metadata & Distribution Info
├── core/                       # Cryptographic Engine (AES-256-GCM, Scrypt KDF, Credentials)
├── network/                    # Stealth Networking Protocols & Transport Layer
├── test/                       # Verification Suite (Auth, Cryptography & System Tests)
├── ui/                         # Graphical Dashboard Layer (CustomTkinter GUI)
├── .comrade_credentials.enc    # Encrypted Credential Vault Payload
├── .comrade_credentials.json   # Local Credential Storage Manifest
├── .gitignore                  # Multi-Platform Git Exclusion Rules
├── LICENSE                     # Project License Terms
├── audit.py                    # Pre-flight Diagnostic & System Health Suite
├── main.py                     # System Entry Point, CLI Router & Dispatcher
├── requirements.txt            # Global Python Dependencies
├── setup.ps1                   # Automated Setup Script (Windows PowerShell)
├── setup.py                    # Package Build & Installation Script
└── setup.sh                    # Automated Setup Script (Linux / macOS Shell)
```

-----
## 🌍 Multi-Platform Deployment & Usage

COMRADE is engineered to adapt its security layer based on the host Operating System.
# 🛠️ COMRADE :: Operational Command Cheat Sheet
 clone the Repo :
 ```text
 git clone https://github.com/lybernet-labs/COMRADE.git
 ```
---

## 🚀 Environment Activation Commands

### Windows (PowerShell)
```powershell
cd COMRADE
py -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
.\setup.ps1
```
### Linux (Terminal)
```text
cd COMRADE
chmod +x setup.sh && ./setup.sh
source venv/bin/activate
```
---
Windows GUI & CLI cmd
----
GUI  
```text
python main.py
```
--- 
CLI 
---
Direct Vault Management
```text
# ===  List All Encrypted Assets in Vault ===
python main.py list

# ===  Secure File & Shred Source ===
python main.py secure "C:\Users\pc\Documents\confidential.pdf"

# ===  Extract & Decrypt Asset ===
python main.py extract idx_a1b2c3d4

# ===  Anti-Forensic Wipe / Permanent Purge ===
python main.py remove idx_a1b2c3d4
```
---
Interactive Subsystems
```
# ===  Offline Local AI Assistant ===
python main.py run ai

# ===  Terminal Password / Credential Manager ===
python main.py run securepass

# ===  Stealth IRC Chat Client ===
python main.py run chat
```
---
Diagnostics & Background Services
```
# ===  Run Automated Diagnostic & Audit Suite ===
python audit.py

# ===  Start Stealth IRC Relay Server (Ergo Daemon) ===
cd bin\ergo-2.19.0-windows-x86_64
.\ergo.exe run

# ===  Download Local AI Neural Weights (Ollama) ===
ollama pull qwen2.5:1.5b
```
---
Linux GUI & CLI cmd
---
GUI
```
python3 main.py
```
---
Interactive Subsystems
```
# === List All Encrypted Assets in Vault ===
python3 main.py list
# === Offline Local AI Assistant ===
python3 main.py run ai

# === Terminal Password / Credential Manager ===
python3 main.py run securepass

# === Stealth IRC Chat Client ===
python3 main.py run chat
```
---
Direct Vault Management
```
# ===  Secure File & Shred Source ===
python3 main.py secure "/home/user/documents/confidential.pdf"

# ===  Extract & Decrypt Asset ===
python3 main.py extract idx_a1b2c3d4

# ===  Anti-Forensic Wipe / Permanent Purge ===
python3 main.py remove idx_a1b2c3d4
```
---
Diagnostics & Background Services
```
# ===  Run Automated Diagnostic & Audit Suite ===
python3 audit.py

# ===  Start Stealth IRC Relay Server (Ergo Daemon) ===
cd bin/ergo-2.19.0-linux-x86_64
./ergo run

# === Download Local AI Neural Weights (Ollama) ===
ollama pull qwen2.5:1.5b
```
---

### 👤 Author
[Mohammed Rehan](https://github.com/zfln-rehan0520)

<h5>Disclaimer: This tool is intended for professional security operations and educational purposes only. Use responsibly!</h5>
