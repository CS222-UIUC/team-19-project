import tkinter as tk
from tkinter import messagebox
import threading
import json
import os
from flask import Flask, request, jsonify

## ip used when testing in demo
## app.run(host="10.186.9.140", port=5000)

# ------------------ Flask Server Part ------------------ #
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_checkpassword():
    print("Received upload request from:", request.remote_addr)
    try:
        data = request.get_json()
        if not data or "password" not in data:
            return "Invalid JSON data", 400
        with open("checkpassword.json", "w") as f:
            json.dump(data, f)
        return "✅ checkpassword.json uploaded successfully", 200
    except Exception as e:
        return f"❌ Error: {e}", 500

@app.route("/compare", methods=["GET"])
def compare_passwords_api():
    try:
        if not os.path.exists("password.json") or not os.path.exists("checkpassword.json"):
            return jsonify({"status": "error", "message": "Missing file"}), 400
        with open("password.json", "r") as f:
            original = json.load(f).get("password", "")
        with open("checkpassword.json", "r") as f:
            check = json.load(f).get("password", "")
        if original == check:
            return jsonify({"status": "match"}), 200
        else:
            return jsonify({"status": "mismatch"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# ------------------ Tkinter GUI Part ------------------ #
class MiddlewareGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Middleware")
        self.root.geometry("400x300")

        self.label = tk.Label(root, text="Middleware Password Comparison", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        self.text_box = tk.Text(root, height=6, width=50)
        self.text_box.pack(pady=5)

        self.compare_button = tk.Button(root, text="Compare Passwords", command=self.compare_passwords,
                                        bg="#4CAF50", fg="white", font=("Arial", 10))
        self.compare_button.pack(pady=10)

        self.refresh_button = tk.Button(root, text="Reload checkpassword.json", command=self.refresh,
                                        bg="#2196F3", fg="white", font=("Arial", 10))
        self.refresh_button.pack()

        self.refresh()

    def refresh(self):
        self.text_box.config(state="normal")
        self.text_box.delete(1.0, tk.END)

        original = check = "Not found"

        # 获取当前目录和 backend 路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))

        # 优先加载 frontend 路径下的 password.json
        password_path = os.path.join(current_dir, "password.json")
        if not os.path.exists(password_path):
            # 如果不存在，尝试从 ../backend 加载
            alt_path = os.path.join(backend_dir, "password.json")
            if os.path.exists(alt_path):
                password_path = alt_path

        # 读取原始密码
        if os.path.exists(password_path):
            with open(password_path, "r") as f:
                original = json.load(f).get("password", "N/A")

        # 读取 checkpassword.json（默认在当前路径）
        check_path = os.path.join(current_dir, "checkpassword.json")
        if os.path.exists(check_path):
            with open(check_path, "r") as f:
                check = json.load(f).get("password", "N/A")

        self.text_box.insert(tk.END, f"Original Password: {original}\n")
        self.text_box.insert(tk.END, f"Check Password: {check}\n")
        self.text_box.config(state="disabled")


    def compare_passwords(self):
        # 获取当前目录和 backend 路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))

        # 优先找 frontend 下的 password.json
        password_path = os.path.join(current_dir, "password.json")
        if not os.path.exists(password_path):
            alt_path = os.path.join(backend_dir, "password.json")
            if os.path.exists(alt_path):
                password_path = alt_path

        check_path = os.path.join(current_dir, "checkpassword.json")
        if not os.path.exists(check_path):
            alt_check_path = os.path.join(backend_dir, "checkpassword.json")
            if os.path.exists(alt_check_path):
                check_path = alt_check_path

        # 如果两个文件路径仍未找到
        if not os.path.exists(password_path) or not os.path.exists(check_path):
            messagebox.showerror("Error", "Missing file(s)")
            return

        with open(password_path, "r") as f:
            original = json.load(f).get("password", "")
        with open(check_path, "r") as f:
            check = json.load(f).get("password", "")

        if original == check:
            messagebox.showinfo("Match", "✅ Passwords MATCH")
        else:
            messagebox.showerror("Mismatch", "❌ Passwords DO NOT match")

# ------------------ Main Start ------------------ #
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()  # 启动 Flask 后台服务

    root = tk.Tk()
    app_gui = MiddlewareGUI(root)
    root.mainloop()
