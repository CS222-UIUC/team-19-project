from flask import Flask, request, jsonify
import threading
import os
import json
import sys

# Global shared variables
password_storage = {
    'password': None,  # The set password
    'submitted': False  # Whether password has been set
}

# Flask Service 1: Set password
app_set = Flask("set_password")

@app_set.route('/set_password', methods=['POST'])
def set_password():
    data = request.json
    pwd = data.get('password')
    if not isinstance(pwd, str) or len(pwd) != 4 or not all(c in '0123' for c in pwd):
        return jsonify({'status': 'error', 'message': 'Password must be 4 digits (0-3)'}), 400
    password_storage['password'] = pwd
    password_storage['submitted'] = True
    return jsonify({'status': 'ok', 'message': 'Password set'})

# Flask Service 2: Try password
app_try = Flask("try_password")

@app_try.route('/try_password', methods=['POST'])
def try_password():
    if not password_storage['submitted']:
        return jsonify({'status': 'waiting', 'message': 'Password not set yet'}), 400

    data = request.json
    attempt = data.get('password')
    if not isinstance(attempt, str) or len(attempt) != 4 or not all(c in '0123' for c in attempt):
        return jsonify({'status': 'error', 'message': 'Attempt must be 4 digits (0-3)'}), 400

    if attempt == password_storage['password']:
        return jsonify({'status': 'success', 'message': 'Correct password!'})
    else:
        return jsonify({'status': 'fail', 'message': 'Wrong password'})

# Terminal-based password setter (new this week)
def terminal_password_setter():
    print("Terminal password setter running (type 'exit' to quit)")
    while True:
        try:
            pwd = input("Enter new password (4 digits, 0-3): ").strip()
            if pwd.lower() == 'exit':
                break
            if len(pwd) != 4 or not all(c in '0123' for c in pwd):
                print("Invalid password format")
                continue
            password_storage['password'] = pwd
            password_storage['submitted'] = True
            print(f"Password set to: {pwd}")
        except KeyboardInterrupt:
            break
    print("Password setter exiting")

# Terminal-based password checker
def terminal_password_checker():
    print("Terminal password checker running (type 'exit' to quit)")
    while True:
        try:
            if not password_storage['submitted']:
                print("Waiting for password to be set...")
                threading.Event().wait(1) 
                continue

            attempt = input("Enter password attempt: ").strip()
            if attempt.lower() == 'exit':
                break
            if len(attempt) != 4 or not all(c in '0123' for c in attempt):
                print("Invalid attempt format")
                continue

            if attempt == password_storage['password']:
                print("TRUE - Correct password!")
            else:
                print("FALSE - Wrong password")
        except KeyboardInterrupt:
            break
    print("Password checker exiting")

# JSON storage class
class PasswordStorage:
    def __init__(self, filename="passwords.json"):
        self.desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        self.file_path = os.path.join(self.desktop_path, filename)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                json.dump({"passwords": []}, file)

    def store_password(self, password):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            data["passwords"].append(password)
            with open(self.file_path, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Password '{password}' stored successfully.")
        except Exception as e:
            print(f"Error storing password: {e}")

def read_passwords(filename="passwords.json"):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    file_path = os.path.join(desktop_path, filename)
    if not os.path.exists(file_path):
        print("No password file found.")
        return
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("Stored Passwords:")
            for pwd in data["passwords"]:
                print(pwd)
    except Exception as e:
        print(f"Error reading passwords: {e}")

def run_app1():
    app_set.run(port=5000)

def run_app2():
    app_try.run(port=5001)

if __name__ == '__main__':
    storage = PasswordStorage()
    storage.store_password("1230")
    storage.store_password("3210")
    storage.store_password("0000")
    read_passwords()

    # Start all services
    flask_thread1 = threading.Thread(target=run_app1, daemon=True)
    flask_thread2 = threading.Thread(target=run_app2, daemon=True)
    setter_thread = threading.Thread(target=terminal_password_setter, daemon=True)
    checker_thread = threading.Thread(target=terminal_password_checker, daemon=True)

    flask_thread1.start()
    flask_thread2.start()
    setter_thread.start()
    checker_thread.start()

    try:
        # Keep main thread alive while others run
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nShutting down all threads...")
        sys.exit(0)
