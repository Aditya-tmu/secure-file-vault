
import tkinter as tk
from tkinter import ttk
from models import get_logs_for_user

class LogsWindow(tk.Toplevel):
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"Activity Logs for {username}")
        self.geometry("600x400")

        # Styling
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

       
        self.log_tree = ttk.Treeview(main_frame, columns=("action", "file", "timestamp"), show="headings")
        self.log_tree.heading("action", text="Action")
        self.log_tree.heading("file", text="File/Context")
        self.log_tree.heading("timestamp", text="Timestamp")
        
        
        self.log_tree.column("action", width=150, anchor=tk.W)
        self.log_tree.column("file", width=250, anchor=tk.W)
        self.log_tree.column("timestamp", width=180, anchor=tk.W)

        self.log_tree.pack(fill=tk.BOTH, expand=True)

       
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_tree.configure(yscrollcommand=scrollbar.set)

        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

        self.load_logs()

    def load_logs(self):
        
        for i in self.log_tree.get_children():
            self.log_tree.delete(i)
            
        logs = get_logs_for_user(self.username)
        for log in logs:
            self.log_tree.insert("", "end", values=(
                log['action'],
                log['file_name'],
                log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            ))

if __name__ == '__main__':
    
    pass
