from flask import Flask, request, jsonify
import json
import os
import re

app = Flask(__name__)
JSON_FILE = "password.json"

def initialize_password_file():
    """Create JSON file with empty password if it doesn't exist"""
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'w') as f:
            json.dump({"password": None}, f)

def get_current_password():
    """Read the current password from JSON file"""
    with open(JSON_FILE, 'r') as f:
        return json.load(f)["password"]

def set_new_password(new_password):
    """Update the password in JSON file"""
    with open(JSON_FILE, 'w') as f:
        json.dump({"password": new_password}, f)

def is_valid_password(pwd):
    """Check if password meets requirements:
    - 4+ characters
    - Contains at least one number (1-3)
    - Contains at least one letter (a-c)
    - Only contains 1,2,3,a,b,c (case insensitive)
    """
    if not isinstance(pwd, str) or len(pwd) < 4:
        return False
    
    pwd_lower = pwd.lower()
    has_number = any(c in '123' for c in pwd_lower)
    has_letter = any(c in 'abc' for c in pwd_lower)
    valid_chars = all(c in '123abc' for c in pwd_lower)
    
    return has_number and has_letter and valid_chars

@app.route('/set_password', methods=['POST'])
def api_set_password():
    data = request.json
    pwd = data.get('password', '').lower()  # Convert to lowercase
    
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
                print("Invalid password! Must be:")
                print("- 4+ characters")
                print("- Contains at least one number (1-3) and one letter (a-c)")
                print("- Only contains characters: 1,2,3,a,b,c")
                continue
            
            set_new_password(pwd)
            print(f"Password set to: {pwd}")
        except KeyboardInterrupt:
            break
    print("Exiting password setter")

if __name__ == '__main__':
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(port=5000))
    flask_thread.daemon = True
    flask_thread.start()
    terminal_set_password()