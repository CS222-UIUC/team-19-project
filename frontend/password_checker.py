import json
import os
import tkinter as tk
from tkinter import messagebox

JSON_FILE = "password.json"

def check_password(attempt):
    if not os.path.exists(JSON_FILE):
        return False
    with open(JSON_FILE, 'r') as f:
        stored_pwd = json.load(f)["password"]
        return stored_pwd == attempt.lower()

def create_checker_gui():
    def on_check_password():
        attempt = entry.get().strip()
        if not attempt:
            messagebox.showerror("Error", "Please enter a password to check")
            return
        
        if check_password(attempt):
            messagebox.showinfo("Result", "TRUE - Correct password!")
        else:
            messagebox.showinfo("Result", "FALSE - Wrong password")
        entry.delete(0, tk.END)

    root = tk.Tk()
    root.title("Password Checker")
    root.geometry("300x150")
    
    tk.Label(root, text="Enter Password to Check", font=("Arial", 12)).pack(pady=10)
    
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)
    
    tk.Button(root, text="Check Password", command=on_check_password).pack()
    
    root.mainloop()

def terminal_check_password():
    print("Password Checker (type 'exit' to quit)")
    while True:
        try:
            attempt = input("Enter password to check: ").strip()
            if attempt.lower() == 'exit':
                break
            if check_password(attempt):
                print("TRUE - Correct password!")
            else:
                print("FALSE - Wrong password")
        except KeyboardInterrupt:
            break
    print("Exiting password checker")

if __name__ == '__main__':
    # Run either GUI or terminal version
    create_checker_gui()
    # terminal_check_password()