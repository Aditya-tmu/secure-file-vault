
import tkinter as tk
from tkinter import ttk, messagebox
import re
from models import create_user, add_log

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

class RegisterWindow(tk.Toplevel):
    
    def __init__(self, master):
        super().__init__(master)
        self.title("Register New User")
        self.geometry("350x350")
        self.resizable(False, False)

        # Styling
        style = ttk.Style(self)
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TEntry", font=("Helvetica", 10), padding=5)

        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Username
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Password
        ttk.Label(main_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=3, column=0, columnspan=2, sticky="ew")

        # Eye button for password visibility
        self.show_password_var = tk.BooleanVar(value=False)
        style.map("Toolbutton", background=[("active", "lightgray")])
        self.eye_button = ttk.Checkbutton(main_frame, text="👁", variable=self.show_password_var, command=self.toggle_password_visibility, style="Toolbutton")
        self.eye_button.grid(row=3, column=2, sticky="w")

        # Hobby
        ttk.Label(main_frame, text="Hobby (for password recovery):").grid(row=4, column=0, sticky="w", pady=(10, 5))
        self.hobby_entry = ttk.Entry(main_frame)
        self.hobby_entry.grid(row=5, column=0, columnspan=2, sticky="ew")
        
        # Password strength meter
        self.strength_label = ttk.Label(main_frame, text="")
        self.strength_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(2, 10))
        self.password_entry.bind("<KeyRelease>", self.check_strength)

        # Register button
        self.register_button = ttk.Button(main_frame, text="Register", command=self.register)
        self.register_button.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.transient(master)
        self.grab_set()
        master.wait_window(self)

    def toggle_password_visibility(self):
        """Toggles the password visibility."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def check_strength(self, event=None):
        
        password = self.password_entry.get()
        if not password:
            self.strength_label.config(text="", foreground="black")
        elif len(password) < 8:
            self.strength_label.config(text="Too short", foreground="red")
        elif PASSWORD_REGEX.match(password):
            self.strength_label.config(text="Strong", foreground="green")
        else:
            self.strength_label.config(text="Weak (needs upper, lower, digit, special char)", foreground="orange")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hobby = self.hobby_entry.get()

        if not username or not password or not hobby:
            messagebox.showerror("Error", "Please fill in all fields.", parent=self)
            return

        if not PASSWORD_REGEX.match(password):
            messagebox.showerror("Registration Failed", "Password is too weak. Must be 8+ chars with uppercase, lowercase, a number, and a special character.", parent=self)
            return

        if create_user(username, password, hobby):
            add_log(username, "register_success")
            messagebox.showinfo("Success", "User registered successfully! You can now log in.", parent=self)
            self.destroy()
        else:
            messagebox.showerror("Registration Failed", "Username already exists.", parent=self)
