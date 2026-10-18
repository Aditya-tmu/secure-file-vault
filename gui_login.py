
import tkinter as tk
from tkinter import ttk, messagebox
from models import verify_user, add_log
from gui_register import RegisterWindow
from gui_forgot_password import ForgotPasswordWindow

class LoginWindow(tk.Tk):
    
    def __init__(self, on_success):
        super().__init__()
        self.title("Secure File Vault - Login")
        self.geometry("350x250")
        self.resizable(False, False)
        
        self.on_success = on_success 

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

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        self.login_button = ttk.Button(button_frame, text="Login", command=self.login)
        self.login_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.register_button = ttk.Button(button_frame, text="Register", command=self.open_register_window)
        self.register_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Forgot password button
        self.forgot_password_button = ttk.Button(main_frame, text="Forgot Password?", command=self.open_forgot_password_window)
        self.forgot_password_button.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Center the window on the screen
        self.eval('tk::PlaceWindow . center')

    def open_register_window(self):
        RegisterWindow(self)

    def open_forgot_password_window(self):
        ForgotPasswordWindow(self)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        if verify_user(username, password):
            add_log(username, "login_success")
            self.destroy() # Close this window...
            self.on_success(username) # ...and open the main app.
        else:
            add_log(username, "login_failed")
            messagebox.showerror("Login Failed", "Invalid username or password.")

if __name__ == '__main__':
    # A little test to see if the window pops up correctly.
    def on_login_success(username):
        print(f"Login successful for {username}! Main app would open now.")

    app = LoginWindow(on_success=on_login_success)
    app.mainloop()
