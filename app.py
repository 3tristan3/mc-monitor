import os
from flask import Flask, render_template, request, jsonify
from mcstatus import JavaServer, BedrockServer

app = Flask(__name__)

@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')

@app.route('/query')
def query_server():
    """
    接收前端请求，查询 Minecraft 服务器状态。
    支持通过 'type' 参数指定 'java' 或 'bedrock'。
    """
    server_ip = request.args.get('ip')
    server_type = request.args.get('type', 'java')  # 默认查询 Java 版

    if not server_ip:
        return jsonify({'error': '必须提供服务器 IP 地址'}), 400

    try:
        if server_type == 'java':
            # --- 查询 Java 版服务器 ---
            # 【修改】使用新的类名 JavaServer
            server = JavaServer.lookup(server_ip, timeout=5)
            status = server.status()
            
            players_sample = []
            if status.players.sample:
                players_sample = [{'name': player.name} for player in status.players.sample]

            response_data = {
                'online': True,
                'version': status.version.name,
                'online_players': status.players.online,
                'max_players': status.players.max,
                'motd': status.description,
                'players_sample': players_sample
            }

        elif server_type == 'bedrock':
            # --- 查询基岩版服务器 ---
            server = BedrockServer.lookup(server_ip, timeout=5)
            status = server.status()
            
            response_data = {
                'online': True,
                'version': status.version.version,
                # 【修改】直接访问 status.players_online
                'online_players': status.players_online,
                # 【修改】直接访问 status.players_max
                'max_players': status.players_max,
                'motd': status.motd,
                'players_sample': [] 
            }

        else:
            return jsonify({'error': '无效的服务器类型'}), 400

        return jsonify(response_data)

    except Exception as e:
        # 【优化】当查询失败时，返回 500 错误码，并确保异常信息是字符串
        return jsonify({'online': False, 'error': f"无法连接到服务器: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

