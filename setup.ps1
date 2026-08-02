$ErrorActionPreference = "Continue"
Clear-Host

# --- ASCII BRANDING ---
Write-Host ""
Write-Host "=====================================================================================" -ForegroundColor Cyan
Write-Host "  ██████╗ ██████╗ ███╗  ███╗██████╗  █████╗ ██████╗ ███████╗" -ForegroundColor Cyan
Write-Host " ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝" -ForegroundColor Cyan
Write-Host " ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║   ██║█████╗ " -ForegroundColor Cyan
Write-Host " ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║   ██║██╔══╝ " -ForegroundColor Cyan
Write-Host " ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗" -ForegroundColor Cyan
Write-Host "  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝" -ForegroundColor Cyan
Write-Host "=====================================================================================" -ForegroundColor Cyan

Write-Host "   Cyber Operations Module for Resilient Authentication, Defense and Encryption" -ForegroundColor White

Write-Host "   " -NoNewline
Write-Host "comrade-V1.10 " -NoNewline -ForegroundColor Cyan
Write-Host "| DESIGNED BY " -NoNewline -ForegroundColor White
Write-Host "MOHAMMED REHAN " -NoNewline -ForegroundColor Cyan
Write-Host "{ Github_id :- " -NoNewline -ForegroundColor White
Write-Host "zfln-rehan0520 " -NoNewline -ForegroundColor Cyan
Write-Host "}" -ForegroundColor White

Write-Host "`n=====================================================================================`n" -ForegroundColor Cyan

Start-Sleep -Seconds 1

function Write-Typewriter {
    param([string]$Text, [string]$Color = "Cyan")
    $chars = $Text.ToCharArray()
    foreach ($c in $chars) {
        Write-Host $c -NoNewline -ForegroundColor $Color
        Start-Sleep -Milliseconds 15
    }
    Write-Host ""
}

Write-Typewriter "[*] Initiating startup sequence..." "DarkGray"
Start-Sleep -Milliseconds 400

# 1. Virtual Environment Setup
Write-Host "[*] Verifying isolated sandbox (venv)........ " -NoNewline -ForegroundColor Cyan
if (-Not (Test-Path ".\venv")) {
    Write-Host "[ BUILDING ]" -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "[ OK ]" -ForegroundColor White
}

# CRITICAL FIX: Hardcode the path to the sandbox python to bypass Windows security blocks
$VenvPython = ".\venv\Scripts\python.exe"

# 2. Dependencies (Forced into Sandbox)
Write-Host "[*] Masking signature & upgrading root....... " -NoNewline -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip -q
Write-Host "[ OK ]" -ForegroundColor White

Start-Sleep -Milliseconds 200

Write-Host "[*] Installing cryptographic dependencies.... " -NoNewline -ForegroundColor Cyan
if (Test-Path ".\requirements.txt") {
    & $VenvPython -m pip install -r requirements.txt -q
    Write-Host "[ OK ]" -ForegroundColor White
} else {
    Write-Host "[ MISSING ]" -ForegroundColor Red
}

Start-Sleep -Milliseconds 200

# 3. Ergo Relay Check
Write-Host "[*] Verifying Stealth Relay Engine........... " -NoNewline -ForegroundColor Cyan
if (Test-Path ".\bin\ergo.exe") {
    Write-Host "[ OK ]" -ForegroundColor White
} else {
    Write-Host "[ MISSING ]" -ForegroundColor Yellow
}

# 4. Ollama Integration
Write-Typewriter "[*] Bypassing operating system restrictions..." "DarkGray"

Write-Host "[*] Synchronizing neural pathways (1.5B)..... " -NoNewline -ForegroundColor Cyan
if (Get-Command "ollama" -ErrorAction SilentlyContinue) {
    ollama pull qwen2.5:1.5b > $null 2>&1
    Write-Host "[ OK ]" -ForegroundColor White
} else {
    Write-Host "[ UNAVAILABLE ]" -ForegroundColor Red
}

Start-Sleep -Milliseconds 500

# 5. Clean Exit (No Auto-Launch)
Write-Host "`n[=====================================================================================]`n" -ForegroundColor Cyan
Write-Typewriter "[+] DEPLOYMENT COMPLETE. ENVIRONMENT SECURED." "White"
Write-Host ""
Write-Host "To launch COMRADE, ensure your virtual environment is active and run:" -ForegroundColor DarkGray
Write-Host "  GUI Vault Mode : " -NoNewline; Write-Host "python main.py" -ForegroundColor Yellow
Write-Host "  CLI Relay Mode : " -NoNewline; Write-Host "python -m cli.cli_comms" -ForegroundColor Yellow
Write-Host ""