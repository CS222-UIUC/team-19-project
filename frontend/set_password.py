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
    </script>
</body>
</html>


# 输入密码页面的 HTML 


# 首页提供两个入口链接
@app.route('/')
def index():
    return 

'''
# 路由：显示设置密码页面
@app.route('/set')
def set_page():
    return render_template_string(set_password_html)

# 路由：显示输入密码页面
@app.route('/try')
def try_page():
    return render_template_string(try_password_html)

if __name__ == '__main__':
    # 前端服务运行在8000端口
    app.run(port=8000)