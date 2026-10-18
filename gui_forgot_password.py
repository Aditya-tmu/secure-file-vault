
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re
from models import get_user_by_username, update_password, add_log, hash_hobby


PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

class ForgotPasswordWindow(tk.Toplevel):
   
    def __init__(self, master):
        super().__init__(master)
        self.title("Forgot Password")
        self.geometry("350x200")
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

        # Hobby
        ttk.Label(main_frame, text="Hobby (for password recovery):").grid(row=2, column=0, sticky="w", pady=(10, 5))
        self.hobby_entry = ttk.Entry(main_frame)
        self.hobby_entry.grid(row=3, column=0, columnspan=2, sticky="ew")

        # Reset Password button
        self.reset_button = ttk.Button(main_frame, text="Reset Password", command=self.reset_password)
        self.reset_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.transient(master)
        self.grab_set()
        master.wait_window(self)

    def reset_password(self):
        
        username = self.username_entry.get()
        hobby = self.hobby_entry.get()

        if not username or not hobby:
            messagebox.showerror("Error", "Please fill in all fields.", parent=self)
            return

        user_data = get_user_by_username(username)
        if not user_data:
            messagebox.showerror("Error", "Username not found.", parent=self)
            return

        if user_data.get("hobby_hash") == hash_hobby(hobby):
            new_password = simpledialog.askstring("New Password", "Enter your new password:", show="*", parent=self)
            if not new_password:
                return
            
            if not PASSWORD_REGEX.match(new_password):
                messagebox.showerror("Password Reset Failed", "New password is too weak.", parent=self)
                return

            update_password(username, new_password)
            add_log(username, "password_reset_success")
            messagebox.showinfo("Success", "Password updated successfully! You can now log in with your new password.", parent=self)
            self.destroy()
        else:
            add_log(username, "password_reset_failed")
            messagebox.showerror("Error", "Incorrect hobby. Password reset failed.", parent=self)
