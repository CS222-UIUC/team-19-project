from flask import Flask, render_template_string

app = Flask(__name__)

# 设置密码页面的 HTML
set_password_html = 
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>设置密码</title>
</head>
<body>
    <h1>设置密码</h1>
    <form id="setForm">
        <label for="password">请输入4位密码(仅包含0~3):</label>
        <input type="text" id="password" name="password" maxlength="4" pattern="[0-3]{4}" required>
        <button type="submit">设置密码</button>
    </form>
    <div id="result"></div>
    
    <script>
    // 拦截表单提交事件
    document.getElementById("setForm").addEventListener("submit", function(event) {
        event.preventDefault();
        var password = document.getElementById("password").value;
        fetch("http://localhost:5000/set_password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({password: password})
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("result").innerText = JSON.stringify(data);
        })
        .catch(error => {
            document.getElementById("result").innerText = "错误：" + error;
        });
    });

    document.getElementById("tryForm").addEventListener("submit", function(event) {
        event.preventDefault();
        var password = document.getElementById("password").value;
        fetch("http://localhost:8000/check_password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({password: password})
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("result").innerText = 
                data.status === 'success' ? 
                (data.result ? "✅ Correct!" : "❌ Wrong!") : 
                "Error: " + data.message;
        })
        .catch(error => {
            document.getElementById("result").innerText = "Error: " + error;
        });
    });
    </script>
</body>
</html>


# 输入密码页面的 HTML 


app = Flask(__name__)

# Web-only password storage
web_password_storage = {'password': '', 'submitted': False}

# Your existing HTML routes (unchanged)
@app.route('/')
def index():
    return "Welcome! Use /set to set a password or /try to check one."

@app.route('/set')
def set_page():
    return render_template_string(set_password_html)

@app.route('/try')
def try_page():
    return render_template_string(try_password_html)

# New: Handle password setting from web
@app.route('/set_password', methods=['POST'])
def set_password():
    data = request.get_json()
    pwd = data.get('password', '')
    
    if len(pwd) == 4 and all(c in '0123' for c in pwd):
        web_password_storage['password'] = pwd  # <-- Store in web storage
        web_password_storage['submitted'] = True
        return {'status': 'success', 'message': f'Password set to: {pwd}'}
    else:
        return {'status': 'error', 'message': 'Invalid password format'}, 400

# New: Handle password checking from web
@app.route('/check_password', methods=['POST'])
def check_password():
    if not web_password_storage['submitted']:
        return {'status': 'error', 'message': 'No password set yet'}, 400
    
    data = request.get_json()
    attempt = data.get('password', '')
    
    if len(attempt) != 4 or not all(c in '0123' for c in attempt):
        return {'status': 'error', 'message': 'Invalid attempt format'}, 400
    
    if attempt == web_password_storage['password']:
        return {'status': 'success', 'result': True}
    else:
        return {'status': 'success', 'result': False}

if __name__ == '__main__':
    # Run web interface on port 8000
    app.run(port=8000)
