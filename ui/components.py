import customtkinter as ctk

class PasswordDialog(ctk.CTkToplevel):
    """A sleek, modern password dialog reflecting the professional UI guidelines."""
    def __init__(self, master, title="Authentication Required", callback=None):
        super().__init__(master)
        self.title(title)
        self.geometry("340x180")
        self.configure(fg_color="#0A0A0C") # Matches BG_MAIN
        self.attributes("-topmost", True)
        self.callback = callback

        # Modern spacing and typography
        self.label = ctk.CTkLabel(self, text="Enter Master Password", 
                                  font=("Inter", 14, "bold"), text_color="#FFFFFF")
        self.label.pack(pady=(20, 10))

        # Subtly styled entry field
        self.password_entry = ctk.CTkEntry(self, show="*", font=("Inter", 13), 
                                           fg_color="#141417", border_width=1, border_color="#2A2A35",
                                           height=35, corner_radius=4)
        self.password_entry.pack(pady=5, padx=30, fill="x")
        self.password_entry.focus()

        # Flat, primary action button
        self.submit_btn = ctk.CTkButton(self, text="UNLOCK", font=("Inter", 12, "bold"),
                                        fg_color="#00D4FF", hover_color="#00A8CC", text_color="#000000",
                                        height=35, corner_radius=4, command=self.submit)
        self.submit_btn.pack(pady=(15, 10), padx=30, fill="x")
        
        self.bind("<Return>", lambda event: self.submit())

    def submit(self):
        password = self.password_entry.get()
        if self.callback and password.strip():
            self.callback(password)
        self.destroy()