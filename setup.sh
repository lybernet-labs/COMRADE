#!/bin/bash

# Exit script if interrupted, but allow error checking
set -e

# Clear terminal screen
clear

# --- COLORS ---
CYAN='\033[0;36m'
WHITE='\033[1;37m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DARKGRAY='\033[1;30m'
NC='\033[0m' # No Color

# --- ASCII BRANDING ---
echo -e "${CYAN}"
echo "====================================================================================="
echo "  ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗"
echo " ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝"
echo " ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║   ██║█████╗  "
echo " ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║   ██║██╔══╝  "
echo " ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗"
echo "  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝"
echo "====================================================================================="
echo -e "${NC}"

echo -e "   Cyber Operations Module for Resilient Authentication, Defense and Encryption"

echo -n "   "
echo -en "${CYAN}comrade-V1.10 ${NC}"
echo -en "| DESIGNED BY "
echo -en "${CYAN}MOHAMMED REHAN ${NC}"
echo -en "{ Github_id :- "
echo -en "${CYAN}zfln-rehan0520 ${NC}"
echo -e "}"

echo -e "\n${CYAN}=====================================================================================${NC}\n"

sleep 0.4

# Typewriter Effect Function
write_typewriter() {
    local text="$1"
    local color="$2"
    local delay=0.015
    
    echo -en "${color}"
    for (( i=0; i<${#text}; i++ )); do
        echo -n "${text:$i:1}"
        sleep $delay
    done
    echo -e "${NC}"
}

write_typewriter "[*] Initiating startup sequence..." "${DARKGRAY}"
sleep 0.4

# 1. Virtual Environment Setup
echo -en "${CYAN}[*] Verifying isolated sandbox (venv)........ ${NC}"
if [ ! -d "./venv" ]; then
    echo -e "${YELLOW}[ BUILDING ]${NC}"
    python3 -m venv venv
else
    echo -e "${WHITE}[ OK ]${NC}"
fi

# Hardcoded path to the isolated virtualenv Python
VENV_PYTHON="./venv/bin/python3"

# 2. Dependencies (Forced into Sandbox)
echo -en "${CYAN}[*] Masking signature & upgrading root....... ${NC}"
$VENV_PYTHON -m pip install --upgrade pip -q > /dev/null 2>&1
echo -e "${WHITE}[ OK ]${NC}"

sleep 0.2

echo -en "${CYAN}[*] Installing cryptographic dependencies.... ${NC}"
if [ -f "./requirements.txt" ]; then
    $VENV_PYTHON -m pip install -r requirements.txt -q > /dev/null 2>&1
    echo -e "${WHITE}[ OK ]${NC}"
else
    echo -e "${RED}[ MISSING ]${NC}"
fi

sleep 0.2

# 3. Ergo Relay Check (Checks for ergo_linux or generic ergo binary)
echo -en "${CYAN}[*] Verifying Stealth Relay Engine........... ${NC}"
if [ -f "./bin/ergo_linux" ] || [ -f "./bin/ergo" ]; then
    # Ensure binary has execution permissions
    [ -f "./bin/ergo_linux" ] && chmod +x ./bin/ergo_linux
    [ -f "./bin/ergo" ] && chmod +x ./bin/ergo
    echo -e "${WHITE}[ OK ]${NC}"
else
    echo -e "${YELLOW}[ MISSING ]${NC}"
fi

# 4. Ollama Integration
write_typewriter "[*] Bypassing operating system restrictions..." "${DARKGRAY}"

echo -en "${CYAN}[*] Synchronizing neural pathways (1.5B)..... ${NC}"
if command -v ollama &> /dev/null; then
    ollama pull qwen2.5:1.5b > /dev/null 2>&1
    echo -e "${WHITE}[ OK ]${NC}"
else
    echo -e "${RED}[ UNAVAILABLE ]${NC}"
fi

sleep 0.5

# 5. Clean Exit (No Auto-Launch)
echo -e "\n${CYAN}[=====================================================================================]${NC}\n"
write_typewriter "[+] DEPLOYMENT COMPLETE. ENVIRONMENT SECURED." "${WHITE}"
echo ""
echo -e "${DARKGRAY}To launch COMRADE, ensure your virtual environment is active and run:${NC}"
echo -en "   GUI Vault Mode : "; echo -e "${YELLOW}python main.py${NC}"
echo -en "   CLI Relay Mode : "; echo -e "${YELLOW}python -m cli.cli_comms${NC}"
echo ""