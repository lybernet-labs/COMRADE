import sys
import os
import time
from datetime import datetime
from rich.console import Console
from rich.theme import Theme

# Import your existing engine and network sidecar
from network.comrade_irc import ComradeComms
from core.relay_manager import boot_stealth_relay
from core.encryption import encrypt_text, decrypt_text

# --- ENTERPRISE SOC TERMINAL THEME ---
custom_theme = Theme({
    "sys": "bold #00D4FF",      # Your ACCENT Cyan
    "error": "bold #EF4444",    # Your DANGER Red
    "time": "dim white",
    "me": "bold #00D4FF",       # Accent for local operator
    "other": "bold #A1A1AA"     # Secondary text for incoming nodes
})
console = Console(theme=custom_theme)

def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def terminal_ui_callback(message):
    """
    Safely injects formatted rich text into the terminal while preserving the input line.
    """
    # Wipe the current input line
    sys.stdout.write('\r\033[K') 
    
    time_str = f"[{get_timestamp()}]"
    
    # Apply SOC styling based on message origin
    if message.startswith("[System Error]"):
        console.print(f"[time]{time_str}[/time] [error]{message}[/error]")
    elif message.startswith("[System"):
        console.print(f"[time]{time_str}[/time] [sys]{message}[/sys]")
    elif message.startswith("[You]:"):
        text = message.replace("[You]:", "").strip()
        console.print(f"[time]{time_str}[/time] [me]YOU:[/me] {text}")
    else:
        # Incoming message formatting
        parts = message.split("]:", 1)
        if len(parts) == 2:
            user = parts[0].replace("[", "").strip()
            text = parts[1].strip()
            console.print(f"[time]{time_str}[/time] [other]{user}:[/other] {text}")
        else:
            console.print(f"[time]{time_str}[/time] {message}")

    # Reprint the input prompt cleanly
    if not message.startswith("[You]:") and not "[System Error]" in message:
        console.print("[sys]PAYLOAD >[/sys] ", end="")
        sys.stdout.flush()

def boot_secure_cli():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # --- ENTERPRISE ASCII BANNER ---
    banner = """[bold #00D4FF]
=========================================================================================
  ██████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ██████╗ ███████╗
 ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗██╔══██╗██╔════╝
 ██║     ██║   ██║██╔████╔██║██████╔╝███████║██║  ██║█████╗  
 ██║     ██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║  ██║██╔══╝  
 ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║██████╔╝███████╗
  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
=========================================================================================[/]
 [bold white]Cyber Operations Module for Resilient Authentication, Defense and Encryption[/]
 [bold #00D4FF]comrade-V1.10[/] [bold white]| DESIGNED BY MOHAMMED REHAN { Github_id :- zfln-rehan0520 }[/]
[bold #00D4FF]=========================================================================================[/]
"""
    console.print(banner)
    
    console.print(f"[[time]{get_timestamp()}[/time]] [sys]INITIALIZING ZERO-KNOWLEDGE PROTOCOL...[/sys]\n")

    # --- NEW: IGNITE STEALTH RELAY ---
    console.print(f"[[time]{get_timestamp()}[/time]] [sys]ENGAGING INTERNAL RELAY ENGINE...[/sys]")
    relay_process, status = boot_stealth_relay()
    
    if not relay_process:
        console.print(f"[[time]{get_timestamp()}[/time]] [error]CRITICAL FAILURE: {status}[/error]")
        sys.exit(1)
    # ---------------------------------

    # Gather Auth Data using Rich
    room_key = console.input("[sys]Enter Room Secret Key:[/sys] ")
    nickname = console.input("[sys]Enter Operator Alias:[/sys] ")

    # Initialize the exact same network sidecar you use in the GUI
    comms = ComradeComms(
        server="127.0.0.1",   
        port=6667,            
        channel="#secure",
        ui_callback=terminal_ui_callback,
        encrypt_func=encrypt_text, 
        decrypt_func=decrypt_text  
    )

    # Dial Out
    console.print(f"\n[[time]{get_timestamp()}[/time]] [sys]CONTACTING RELAY...[/sys]")
    success = comms.connect(nickname=nickname)
    
    if not success:
        console.print(f"[[time]{get_timestamp()}[/time]] [error]TARGET MACHINE REFUSED CONNECTION.[/error]")
        sys.exit(1)

    console.print(f"[[time]{get_timestamp()}[/time]] [sys]SECURE LINK ESTABLISHED.[/sys]")
    console.print(f"[[time]{get_timestamp()}[/time]] [sys]TYPE '/exit' TO SEVER CONNECTION AND GO DARK.[/sys]\n")
    console.print("[dim]" + "━" * 60 + "[/dim]")

    # Main CLI Input Loop
    time.sleep(0.5) 
    
    try:
        while True:
            # Print the rich prompt manually, then use standard input to capture
            console.print("[sys]PAYLOAD >[/sys] ", end="")
            msg = input()
            
            if msg.strip().lower() == '/exit':
                break
                
            if msg.strip() and comms.running:
                comms.send_message(msg, room_key)
                
    except KeyboardInterrupt:
        console.print(f"\n[[time]{get_timestamp()}[/time]] [error]FORCE QUIT DETECTED.[/error]")

    # Teardown
    comms.disconnect()
    console.print(f"\n[[time]{get_timestamp()}[/time]] [sys]CONNECTION SEVERED. GOING DARK.[/sys]")
    console.print("[dim]" + "━" * 60 + "[/dim]")


# This is the vital trigger block that actually runs the code!
if __name__ == "__main__":
    boot_secure_cli()