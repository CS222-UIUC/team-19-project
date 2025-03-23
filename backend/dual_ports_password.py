from flask import Flask, request, jsonify
import threading

# 全局共享变量
password_storage = {
    'password': None,  # 设置的密码
    'submitted': False  # 是否已经提交
}

# 服务1：设置密码
app_set = Flask("set_password")

@app_set.route('/set_password', methods=['POST'])
def set_password():
    data = request.json
    pwd = data.get('password')
    if not isinstance(pwd, str) or len(pwd) != 4 or not all(c in '0123' for c in pwd):
        return jsonify({'status': 'error', 'message': '密码必须是4位，仅包含0~3'}), 400
    password_storage['password'] = pwd
    password_storage['submitted'] = True
    return jsonify({'status': 'ok', 'message': '密码已设置'})


# 服务2：输入密码尝试验证
app_try = Flask("try_password")

@app_try.route('/try_password', methods=['POST'])
def try_password():
    if not password_storage['submitted']:
        return jsonify({'status': 'waiting', 'message': '尚未设置密码，请稍后'}), 400

    data = request.json
    attempt = data.get('password')
    if not isinstance(attempt, str) or len(attempt) != 4 or not all(c in '0123' for c in attempt):
        return jsonify({'status': 'error', 'message': '尝试密码必须是4位，仅包含0~3'}), 400

    if attempt == password_storage['password']:
        return jsonify({'status': 'success', 'message': '密码正确！通过！'})
    else:
        return jsonify({'status': 'fail', 'message': '密码错误，请重试'})


# added password storage as txt
class PasswordStorage:
    def __init__(self, filename="passwords.txt"):
        # Get the path to the Windows desktop
        self.desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        self.file_path = os.path.join(self.desktop_path, filename)

        # Create the file if it doesn't exist
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                file.write("Stored Passwords:\n")

    def store_password(self, password):
        """Append a password to the file."""
        with open(self.file_path, 'a') as file:
            file.write(f"{password}\n")
        print(f"Password '{password}' stored successfully.")

def read_passwords(filename="passwords.txt"):
    # Get the path to the Windows desktop
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    file_path = os.path.join(desktop_path, filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        print("No password file found.")
        return

    # Read and print the contents of the file
    with open(file_path, 'r') as file:
        print("Stored Passwords:")
        for line in file.readlines():
            print(line.strip())


# 多线程启动两个服务
def run_app1():
    app_set.run(port=5000)

def run_app2():
    app_try.run(port=5001)

if __name__ == '__main__':
    # Store dummy passwords
    storage = PasswordStorage()
    storage.store_password("1230")
    storage.store_password("3210")
    storage.store_password("0000")
    read_passwords()

    # main
    t1 = threading.Thread(target=run_app1)
    t2 = threading.Thread(target=run_app2)
    t1.start()
    t2.start()
