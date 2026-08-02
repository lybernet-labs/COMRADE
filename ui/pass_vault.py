import customtkinter as ctk
from tkinter import messagebox, filedialog
import secrets
import string
import json
from core.credentials import (
    load_credentials, 
    save_credentials, 
    encrypt_individual_pass, 
    decrypt_individual_pass
)

# --- ENTERPRISE SOC COLOR PALETTE ---
BG_MAIN = "#09090B"
BG_SURFACE = "#18181B"
BG_SURFACE_LIGHT = "#27272A"
ACCENT = "#00D4FF"
TEXT_PRIMARY = "#FAFAFA"
TEXT_SECONDARY = "#A1A1AA"
DANGER = "#EF4444"
WARNING = "#FF9800"

class CredentialCard(ctk.CTkFrame):
    """Professional UI tile for each secured password."""
    def __init__(self, master, account_name, reveal_cb, delete_cb):
        super().__init__(master, fg_color=BG_SURFACE_LIGHT, corner_radius=8, height=55)
        self.pack(fill="x", padx=10, pady=6)
        self.pack_propagate(False)

        lbl = ctk.CTkLabel(self, text=account_name, font=("Consolas", 14, "bold"), text_color=TEXT_PRIMARY)
        lbl.pack(side="left", padx=15)

        btn_del = ctk.CTkButton(self, text="DELETE", width=70, height=30, font=("Inter", 11, "bold"),
                                fg_color="transparent", border_width=1, border_color=DANGER, 
                                text_color=DANGER, hover_color="#3F1D1D", corner_radius=15,
                                command=lambda: delete_cb(account_name))
        btn_del.pack(side="right", padx=(5, 15))

        btn_reveal = ctk.CTkButton(self, text="UNVEIL / COPY", width=120, height=30, font=("Inter", 11, "bold"),
                                   fg_color="transparent", border_width=1, border_color=ACCENT, 
                                   text_color=ACCENT, hover_color=BG_SURFACE, corner_radius=15,
                                   command=lambda: reveal_cb(account_name))
        btn_reveal.pack(side="right", padx=5)

class SecurePassVault(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("COMRADE | Zero-Knowledge Credential Vault")
        self.geometry("750x600")
        self.configure(fg_color=BG_MAIN)
        self.attributes("-topmost", True)
        
        self.credentials = load_credentials()
        if self.credentials is None:
            self.credentials = {}
            
        self._build_ui()

    def _build_ui(self):
        # Header Controls
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=20)
        
        header_lbl = ctk.CTkLabel(top_frame, text="NATIVE CRYPTO-VAULT", font=("Consolas", 16, "bold"), text_color=ACCENT)
        header_lbl.pack(side="left")
        
        btn_restore = ctk.CTkButton(top_frame, text="RESTORE VAULT", width=110, height=32, font=("Inter", 11, "bold"),
                                    fg_color="transparent", border_width=1, border_color=TEXT_SECONDARY, 
                                    text_color=TEXT_SECONDARY, hover_color=BG_SURFACE_LIGHT, corner_radius=16,
                                    command=self.restore_vault)
        btn_restore.pack(side="right", padx=5)
        
        btn_backup = ctk.CTkButton(top_frame, text="BACKUP VAULT", width=110, height=32, font=("Inter", 11, "bold"),
                                   fg_color="transparent", border_width=1, border_color=ACCENT, 
                                   text_color=ACCENT, hover_color=BG_SURFACE_LIGHT, corner_radius=16,
                                   command=self.backup_vault)
        btn_backup.pack(side="right", padx=5)

        # Secured Account List
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=BG_SURFACE, corner_radius=10, border_width=1, border_color=BG_SURFACE_LIGHT)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Generation Bar
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20)
        
        self.btn_add = ctk.CTkButton(bottom_frame, text="+ GENERATE & ADD NEW CREDENTIAL", font=("Inter", 13, "bold"), 
                                     fg_color="transparent", border_width=1, border_color=ACCENT, text_color=ACCENT, 
                                     hover_color=BG_SURFACE_LIGHT, height=45, corner_radius=22, 
                                     command=self.open_add_window)
        self.btn_add.pack(fill="x", expand=True, padx=20)
        
        self.refresh_list()

    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        if not self.credentials:
            lbl = ctk.CTkLabel(self.list_frame, text="No encrypted credentials found.", text_color=TEXT_SECONDARY, font=("Inter", 14))
            lbl.pack(pady=50)
            return
            
        for account in sorted(self.credentials.keys()):
            CredentialCard(self.list_frame, account, self.action_reveal, self.action_delete)

    # --- ITEM LEVEL AUTHORIZATIONS ---
    def action_reveal(self, account):
        """Authorizes decryption, visually reveals password, and auto-copies."""
        encrypted_payload = self.credentials.get(account)
        dialog = ctk.CTkInputDialog(text=f"Enter dedicated encryption key for [{account}]:", title="Auth Required")
        item_key = dialog.get_input()
        
        if not item_key: return
        
        plain_pass = decrypt_individual_pass(encrypted_payload, item_key)
        
        if not plain_pass:
            messagebox.showerror("Access Denied", "Cryptographic mismatch. Invalid key.", parent=self)
            return

        self.clipboard_clear()
        self.clipboard_append(plain_pass)
        self.update()
        
        self.after(10000, self.wipe_clipboard)
        
        messagebox.showinfo(
            "Payload Decrypted", 
            f"Account: {account}\n\nPassword: {plain_pass}\n\n[Copied to clipboard. Memory auto-wipes in 10 seconds]", 
            parent=self
        )

    def action_delete(self, account):
        """Requires strict authorization before destroying a credential."""
        dialog = ctk.CTkInputDialog(text=f"Verify item key to authorize deletion of [{account}]:", title="Security Override")
        item_key = dialog.get_input()
        
        if not item_key: return
        
        encrypted_payload = self.credentials.get(account)
        plain_pass = decrypt_individual_pass(encrypted_payload, item_key)
        
        if not plain_pass:
            messagebox.showerror("Access Denied", "Cryptographic mismatch. Invalid key. Deletion blocked.", parent=self)
            return
            
        if messagebox.askyesno("Confirm", f"Permanently wipe {account} credential?", parent=self):
            del self.credentials[account]
            if save_credentials(self.credentials):
                self.refresh_list()

    def wipe_clipboard(self):
        """Silent memory wipe."""
        self.clipboard_clear()
        self.clipboard_append("")
        self.update()
        print("[SYSTEM]: Clipboard memory flushed.")

    # --- THE UPGRADED ENTRY WINDOW ---
    def open_add_window(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Deploy Secure Asset")
        popup.geometry("450x540") 
        popup.configure(fg_color=BG_MAIN) # Darker void background
        popup.transient(self)
        popup.grab_set()

        # Header Title
        ctk.CTkLabel(popup, text="NEW ENCRYPTED ENTRY", font=("Consolas", 16, "bold"), text_color=TEXT_PRIMARY).pack(pady=(25, 10))

        # Main Elevated Card Container
        card = ctk.CTkFrame(popup, fg_color=BG_SURFACE, corner_radius=12, border_width=1, border_color=BG_SURFACE_LIGHT)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        # Account Entry (Left-aligned text for structured form feel)
        ctk.CTkLabel(card, text="ACCOUNT / SERVICE", font=("Inter", 11, "bold"), text_color=ACCENT).pack(anchor="w", padx=25, pady=(20, 2))
        account_entry = ctk.CTkEntry(card, font=("Consolas", 13), width=340, height=38, 
                                     fg_color=BG_MAIN, border_width=1, border_color=BG_SURFACE_LIGHT, 
                                     corner_radius=6, placeholder_text="e.g., ProtonMail, AWS Root")
        account_entry.pack(padx=25, pady=(0, 15))

        # Key Entry
        ctk.CTkLabel(card, text="DEDICATED ENCRYPTION KEY", font=("Inter", 11, "bold"), text_color=WARNING).pack(anchor="w", padx=25, pady=(5, 2))
        item_key_entry = ctk.CTkEntry(card, font=("Consolas", 13), width=340, height=38, 
                                      fg_color=BG_MAIN, border_width=1, border_color=BG_SURFACE_LIGHT, 
                                      show="*", corner_radius=6, placeholder_text="Strictly memorize this key")
        item_key_entry.pack(padx=25, pady=(0, 15))

        # Password Entry
        ctk.CTkLabel(card, text="PAYLOAD (PASSWORD)", font=("Inter", 11, "bold"), text_color=ACCENT).pack(anchor="w", padx=25, pady=(5, 2))
        password_entry = ctk.CTkEntry(card, font=("Consolas", 13), width=340, height=38, 
                                      fg_color=BG_MAIN, border_width=1, border_color=BG_SURFACE_LIGHT, 
                                      corner_radius=6, placeholder_text="Enter or generate payload")
        password_entry.pack(padx=25, pady=(0, 20))

        def generate_pass():
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_=+"
            while True:
                pwd = ''.join(secrets.choice(alphabet) for _ in range(20))
                if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd) 
                        and sum(c.isdigit() for c in pwd) >= 2 and any(c in "!@#$%^&*-_=+" for c in pwd)):
                    break
            password_entry.delete(0, 'end')
            password_entry.insert(0, pwd)

        # Secondary CTA: Curved, Hollow outline 
        ctk.CTkButton(card, text="⚡ AUTOGENERATE 20-BIT PAYLOAD", font=("Inter", 11, "bold"), width=340, height=35,
                      fg_color="transparent", border_width=1, border_color=WARNING, text_color=WARNING, 
                      hover_color=BG_MAIN, corner_radius=18, command=generate_pass).pack(padx=25, pady=(0, 15))

        def save_and_close():
            acc = account_entry.get().strip()
            item_key = item_key_entry.get()
            pwd = password_entry.get()
            
            if not acc or not item_key or not pwd:
                messagebox.showerror("Error", "All fields are required.", parent=popup)
                return
                
            enc_payload = encrypt_individual_pass(pwd, item_key)
            if not enc_payload:
                messagebox.showerror("Error", "Crypto calculation failed.", parent=popup)
                return
                
            self.credentials[acc] = enc_payload
            if save_credentials(self.credentials):
                self.refresh_list()
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to commit to disk.", parent=popup)

        # Primary CTA: Curved, Solid fill (Draws the eye directly to the final action)
        ctk.CTkButton(card, text="ENCRYPT & COMMIT", font=("Inter", 12, "bold"), width=340, height=42,
                      fg_color=ACCENT, text_color=BG_MAIN, hover_color="#00A2D6", 
                      corner_radius=21, command=save_and_close).pack(padx=25, pady=(0, 25))

    # --- BACKUP / RESTORE ---
    def backup_vault(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Backup", "*.json")])
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(self.credentials, f, indent=4)
                messagebox.showinfo("Backup", f"Vault encrypted state exported to:\n{path}", parent=self)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self)

    def restore_vault(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Backup", "*.json")])
        if path:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                self.credentials.update(data)
                save_credentials(self.credentials)
                self.refresh_list()
                messagebox.showinfo("Restore", "Backup integrated successfully.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore: {e}", parent=self)