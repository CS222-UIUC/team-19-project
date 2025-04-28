import json
import os

JSON_FILE = "password.json"

def check_password(attempt):
    """Check if attempt matches stored password (case insensitive)"""
    if not os.path.exists(JSON_FILE):
        return False
    
    with open(JSON_FILE, 'r') as f:
        stored_pwd = json.load(f)["password"]
        return stored_pwd == attempt.lower() 

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
    terminal_check_password()