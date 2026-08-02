import os
import platform

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
   
    base_dir = os.getenv('LOCALAPPDATA', os.getcwd())
    VAULT_DIR = os.path.join(base_dir, 'ComradeVault')
else:
  
    base_dir = os.path.expanduser('~')
    VAULT_DIR = os.path.join(base_dir, '.comrade_vault')

VAULT_EXTENSION = ".dat"

MANIFEST_PATH = os.path.join(VAULT_DIR, "sys_cache.idx")
