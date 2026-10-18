
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import threading
import db 
from models import get_files_for_user, add_file_metadata, update_file_status, add_log
from security import generate_key, encrypt_file, decrypt_file, calculate_sha256
from gui_logs import LogsWindow

LOCK_TIMEOUT_MS = 10 * 60 * 1000  # 10 minutes, for the auto-locker.

class VaultWindow(tk.Tk):
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"Secure Vault - Welcome, {username}")
        self.geometry("800x500")

        
        
        self.password_cache = None 
        self.after_id = None 
        
        
        self.db_conn, self.users_col, self.files_col, self.logs_col = db.get_db_collections()


        # Styling
        style = ttk.Style(self)
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Main layout
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill=tk.X, side=tk.TOP)

        self.file_tree = ttk.Treeview(self, columns=("name", "encrypted", "modified", "hash"), show="headings")
        self.file_tree.heading("name", text="File Name")
        self.file_tree.heading("encrypted", text="Status")
        self.file_tree.heading("modified", text="Last Modified")
        self.file_tree.heading("hash", text="SHA-256 Hash")
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Buttons
        button_frame = ttk.Frame(self, padding=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="Add File", command=self.add_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Encrypt", command=self.encrypt_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Decrypt", command=self.decrypt_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Verify Integrity", command=self.verify_integrity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Logs", command=self.view_logs).pack(side=tk.RIGHT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Key>", self.reset_lock_timer)
        self.bind("<MouseWheel>", self.reset_lock_timer)
        self.bind("<Button-1>", self.reset_lock_timer)

        self.refresh_files()
        self.reset_lock_timer()

    def get_password(self):
        
        if self.password_cache is None:
            self.password_cache = simpledialog.askstring("Password", "Enter your vault password:", show='*')
        return self.password_cache

    def add_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        sha256_hash = calculate_sha256(file_path)

        add_file_metadata(self.username, file_name, file_path, sha256_hash)
        add_log(self.username, "add_file", file_name)
        self.refresh_files()

    def get_selected_file(self):
       
        selected_item = self.file_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file first.")
            return None, None
        
        # The item's IID is the file's _id as a string
        from bson.objectid import ObjectId
        file_id_str = self.file_tree.item(selected_item)['text']
        
        file_data = self.files_col.find_one({"_id": ObjectId(file_id_str)})
        
        return file_data, selected_item

    def encrypt_selected(self):
        file_data, _ = self.get_selected_file()
        if not file_data or file_data['encrypted']:
            messagebox.showinfo("Info", "File is already encrypted or not selected.")
            return

        password = self.get_password()
        if not password:
            return

        def _encrypt():
            try:
                encrypted_path = file_data['file_path'] + ".enc"
                salt = encrypt_file(file_data['file_path'], encrypted_path, password)
                new_hash = calculate_sha256(encrypted_path)
                
                update_file_status(file_data['file_path'], encrypted=True, new_hash=new_hash, salt=salt)
                self.files_col.update_one({"_id": file_data['_id']}, {"$set": {"file_path": encrypted_path}})

                add_log(self.username, "encrypt_file", file_data['file_name'])
                self.refresh_files()
                messagebox.showinfo("Success", "File encrypted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Encryption failed: {e}")

        threading.Thread(target=_encrypt).start()

    def decrypt_selected(self):
        file_data, _ = self.get_selected_file()
        if not file_data or not file_data['encrypted']:
            messagebox.showinfo("Info", "File is not encrypted or not selected.")
            return

        password = self.get_password()
        if not password:
            return

        def _decrypt():
            try:
                decrypted_path = file_data['file_path'].replace(".enc", "")
                salt = file_data['salt']
                
                if decrypt_file(file_data['file_path'], decrypted_path, password, salt):
                    new_hash = calculate_sha256(decrypted_path)
                    update_file_status(file_data['file_path'], encrypted=False, new_hash=new_hash, salt=None)
                    self.files_col.update_one({"_id": file_data['_id']}, {"$set": {"file_path": decrypted_path}})

                    add_log(self.username, "decrypt_file", file_data['file_name'])
                    self.refresh_files()
                    messagebox.showinfo("Success", "File decrypted successfully.")
                else:
                    messagebox.showerror("Decryption Failed", "Wrong password or corrupted file.")
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {e}")

        threading.Thread(target=_decrypt).start()

    def verify_integrity(self):
        file_data, _ = self.get_selected_file()
        if not file_data:
            return

        try:
            current_hash = calculate_sha256(file_data['file_path'])
            if current_hash == file_data['sha256_hash']:
                messagebox.showinfo("Integrity Check", "OK: File hash matches the one in the database.")
            else:
                messagebox.showwarning("Integrity Check", "FAIL: File has been modified or corrupted!")
            add_log(self.username, "verify_integrity", file_data['file_name'])
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found. It may have been moved or deleted.")

    def refresh_files(self):
        """Clears the file list and reloads it from the database."""
        for i in self.file_tree.get_children():
            self.file_tree.delete(i)
            
        files = get_files_for_user(self.username)
        for f in files:
            status = "Encrypted" if f.get('encrypted') else "Decrypted"
            # Use the file's _id as the item's IID
            self.file_tree.insert("", "end", iid=str(f['_id']), text=str(f['_id']), values=(
                f['file_name'], 
                status,
                f['last_modified'].strftime('%Y-%m-%d %H:%M'),
                f['sha256_hash'][:16] + "..." if f['sha256_hash'] else ""
            ))

    def view_logs(self):
        LogsWindow(self.username)

    def lock_vault(self):
        
        self.withdraw()
        add_log(self.username, "auto_lock")
        
        # We need to import LoginWindow here to avoid circular import
        from gui_login import LoginWindow
        unlock_window = LoginWindow(on_success=self.unlock_vault)
        unlock_window.mainloop()

    def unlock_vault(self, username):
        
        if username == self.username:
            self.deiconify() # Re-show the vault window
            self.reset_lock_timer()
        else:
            messagebox.showerror("Unlock Failed", "You must unlock with the same user.")
            self.lock_vault()

    def reset_lock_timer(self, event=None):
        
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(LOCK_TIMEOUT_MS, self.lock_vault)

    def on_close(self):
        
        add_log(self.username, "logout")
        if self.after_id:
            self.after_cancel(self.after_id)
        self.destroy()

if __name__ == '__main__':
    
    pass
