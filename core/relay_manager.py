import subprocess
import os
import atexit
import time
import platform

def boot_stealth_relay():
    """
    Silently launches the bundled Ergo daemon in the background and 
    binds its lifecycle to the COMRADE application across Windows & Linux.
    """
    # 1. Locate the bin directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bin_dir = os.path.join(base_dir, "bin")
    
    # 2. Cross-Platform Binary Selection
    system = platform.system().lower()
    
    if system == "windows":
        ergo_binary = os.path.join(bin_dir, "ergo.exe")
        # Fallback if binary hasn't been renamed with extension
        if not os.path.exists(ergo_binary):
            ergo_binary = os.path.join(bin_dir, "ergo")
    else:
        # Linux or macOS environment
        ergo_binary = os.path.join(bin_dir, "ergo_linux")
        # Fallback to standard binary name
        if not os.path.exists(ergo_binary):
            ergo_binary = os.path.join(bin_dir, "ergo")

    if not os.path.exists(ergo_binary):
        return None, f"Error: Ergo binary missing from bin/ directory ({ergo_binary})."

    try:
        # 3. OS-Specific Stealth Execution Flags
        kwargs = {
            "cwd": bin_dir,               # Execute from bin/ so it finds ircd.yaml
            "stdout": subprocess.DEVNULL, # Suppress logs
            "stderr": subprocess.DEVNULL  # Suppress errors
        }

        if system == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = startupinfo

        # 4. Launch the background process
        process = subprocess.Popen([ergo_binary, "run"], **kwargs)

        # 5. Tie the server's life to COMRADE. If Python quits, kill the server.
        atexit.register(process.terminate)
        
        # --- MAXIMUM BOOT WINDOW ---
        # Give the daemon 3.0 seconds to fully bind to port 6667
        time.sleep(3.0)
        # ---------------------------
        
        return process, "Success"
        
    except Exception as e:
        return None, f"Failed to start internal relay: {str(e)}"