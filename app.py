# 1. 注意这里，我们多导入了一个 render_template
from flask import Flask, request, jsonify, render_template
from mcstatus import JavaServer

# 2. 初始化 Flask 应用
app = Flask(__name__)


# 3. 新增一个路由，用于显示我们的主页
@app.route("/")
def index():
    # 这会找到并返回 templates/index.html 文件
    return render_template("index.html")


# 4. 我们之前的 API 路由保持不变
@app.route("/query")
def query_server():
    server_ip = request.args.get('ip')
    if not server_ip:
        return jsonify({"error": "请提供服务器IP地址"}), 400

    try:
        server = JavaServer.lookup(server_ip)
        status = server.status()
        result = {
            "host": server_ip,
            "version": status.version.name,
            "online_players": status.players.online,
            "max_players": status.players.max,
            "latency": round(status.latency),
            "motd": status.description
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"查询失败: {str(e)}"}), 500

# 5. 主程序入口保持不变
if __name__ == '__main__':
    app.run(debug=True, port=5000)

