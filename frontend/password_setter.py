from flask import Flask, request, jsonify
import json
import os
import tkinter as tk
from tkinter import messagebox
from threading import Thread

app = Flask(__name__)
JSON_FILE = "password.json"

# Password validation and file operations (same as before)
def initialize_password_file():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'w') as f:
            json.dump({"password": None}, f)

def get_current_password():
    with open(JSON_FILE, 'r') as f:
        return json.load(f)["password"]

def set_new_password(new_password):
    with open(JSON_FILE, 'w') as f:
        json.dump({"password": new_password}, f)

def is_valid_password(pwd):
    if not isinstance(pwd, str) or len(pwd) < 4:
        return False
    pwd_lower = pwd.lower()
    has_number = any(c in '123' for c in pwd_lower)
    has_letter = any(c in 'abc' for c in pwd_lower)
    valid_chars = all(c in '123abc' for c in pwd_lower)
    return has_number and has_letter and valid_chars

# GUI Functions
def create_setter_gui():
    def on_set_password():
        pwd = entry.get().strip().lower()
        if not pwd:
            messagebox.showerror("Error", "Password cannot be empty")
            return
        
        if not is_valid_password(pwd):
            messagebox.showerror(
                "Invalid Password",
                "Password must:\n"
                "- Be 4+ characters\n"
                "- Contain at least one number (1-3)\n"
                "- Contain at least one letter (a-c)\n"
                "- Only contain: 1,2,3,a,b,c"
            )
            return
        
        set_new_password(pwd)
        messagebox.showinfo("Success", f"Password set to: {pwd}")
        entry.delete(0, tk.END)

    root = tk.Tk()
    root.title("Password Setter")
    root.geometry("400x250")

    tk.Label(root, text="Set New Password", font=("Arial", 14)).pack(pady=10)
    
    tk.Label(root, text="Password Requirements:").pack()
    tk.Label(root, text="- 4+ characters").pack()
    tk.Label(root, text="- At least one number (1-3)").pack()
    tk.Label(root, text="- At least one letter (a-c)").pack()
    tk.Label(root, text="- Only 1,2,3,a,b,c allowed").pack(pady=5)
    
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)
    
    tk.Button(root, text="Set Password", command=on_set_password).pack()
    
    root.mainloop()

# Flask and terminal interfaces (same as before)
@app.route('/set_password', methods=['POST'])
def api_set_password():
    data = request.json
    pwd = data.get('password', '').lower()
    if not is_valid_password(pwd):
        return jsonify({
            'status': 'error', 
            'message': 'Password must: 1) Be 4+ characters, 2) Contain at least one number (1-3) and one letter (a-c), 3) Only contain 1,2,3,a,b,c'
        }), 400
    set_new_password(pwd)
    return jsonify({'status': 'ok', 'message': 'Password set'})

def terminal_set_password():
    initialize_password_file()
    print("Password Setter (type 'exit' to quit)")
    print("Requirements: 4+ characters, at least one number (1-3) and one letter (a-c)")
    while True:
        try:
            pwd = input("Set new password: ").strip().lower()
            if pwd == 'exit':
                break
            if not is_valid_password(pwd):
                print("Invalid password! See requirements above.")
                continue
            set_new_password(pwd)
            print(f"Password set to: {pwd}")
        except KeyboardInterrupt:
            break
    print("Exiting password setter")

if __name__ == '__main__':
    # Start Flask in background
    flask_thread = Thread(target=lambda: app.run(port=5000))
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start GUI in main thread
    create_setter_gui()
    # Or run terminal interface instead: terminal_set_password()