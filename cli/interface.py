import os
from colorama import Fore, Style, init
from core.file_manager import list_secured_files 
import maskpass

init(autoreset=True)

def display_banner():
    """Renders the official COMRADE Cyber-Operations Branding."""
    cyan = Fore.CYAN
    white = Fore.WHITE
    
    print(f"\n{cyan}{'='*85}")
    print(f"{cyan}   ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗")
    print(f"{cyan}  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝")
    print(f"{cyan}  ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║   ██║█████╗  ")
    print(f"{cyan}  ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║   ██║██╔══╝  ")
    print(f"{cyan}  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗")
    print(f"{cyan}   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝")
    print(f"{cyan}{'='*85}")
    
    print(f"{white}   Cyber Operations Module for Resilient Authentication, Defense and Encryption")
    print(f"   {cyan}comrade-V1.10 {white}| DESIGNED BY {cyan}MOHAMMED REHAN {white}{{ Github_id :- {cyan}zfln-rehan0520 {white}}}")
    print(f"{cyan}{'='*85}\n")
    
def show_vault(files=None):
    """Refined Classic Table - Now fetches data automatically if missing"""
    if files is None:
        files = list_secured_files()

    if not files:
        print(f"\n{Fore.RED}  [!] No files found in the vault.")
        return

    print(f"{Fore.WHITE}┌" + "─" * 25 + "┬" + "─" * 45 + "┐")
    print(f"{Fore.WHITE}│ {Style.BRIGHT}Vault ID                {Fore.WHITE}│ {Style.BRIGHT}Original Filename                            {Fore.WHITE}│")
    print(f"{Fore.WHITE}├" + "─" * 25 + "┼" + "─" * 45 + "┤")

    for f in files:
        vault_id = f['vault_name']
        original = f['original_name']
       
        print(f"{Fore.WHITE}│ {Fore.WHITE}{vault_id:<23} {Fore.WHITE}│ {Fore.GREEN}{original:<43} {Fore.WHITE}│")

    print(f"{Fore.WHITE}└" + "─" * 25 + "┴" + "─" * 45 + "┘")
    print(f"\n{Fore.GREEN}● {Fore.WHITE}STATUS: {Fore.GREEN}ENCRYPTION ENGINE NOMINAL\n")

def get_password(prompt_text="ENTER MASTER KEY: "):
    """Securely captures password input and strips hidden trailing characters."""
    styled_prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"
 
    return maskpass.askpass(prompt=styled_prompt, mask="*").strip()
