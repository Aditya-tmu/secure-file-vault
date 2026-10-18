
import tkinter as tk
from gui_login import LoginWindow
from gui_vault import VaultWindow
import db 

def start_main_app(username):
    
    vault_app = VaultWindow(username)
    vault_app.mainloop()



if __name__ == '__main__':
   
    if db.db is None:
        print("Application cannot start without a database connection.")
    else:
        
        login_app = LoginWindow(on_success=start_main_app)
        login_app.mainloop()
