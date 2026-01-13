from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcstatus import JavaServer
import asyncio

app = FastAPI()

class QueryRequest(BaseModel):
    host: str
    port: int = 25565

@app.post("/api/query")
async def query_server(request: QueryRequest):
    try:
        # 1. 异步查询
        server = await asyncio.wait_for(
            JavaServer.lookup(f"{request.host}:{request.port}").async_status(),
            timeout=5.0
        )

        # 2. 兼容性处理：同时尝试 'favicon' 和 'icon' 两个属性名
        # getattr(obj, 'name', default) -> 如果有name属性就返回，否则返回default
        favicon_data = getattr(server, 'favicon', getattr(server, 'icon', None))

        # 3. 兼容性处理：MOTD 
        # 有些版本返回对象，有些返回字符串，有些叫 description
        raw_description = getattr(server, 'description', "A Minecraft Server")
        
        # 4. 构建响应
        return {
            "status": "success",
            "online": True,
            "host": request.host,
            "port": request.port,
            "motd": raw_description,
            "version": server.version.name,
            "players": {
                "online": server.players.online,
                "max": server.players.max,
                # 部分服务器可能没有 sample 字段，做个防空处理
                "sample": server.players.sample if server.players.sample else [] 
            },
            "latency": round(server.latency),
            "favicon": favicon_data
        }

    except asyncio.TimeoutError:
        # 超时不是错误，而是状态
        return {
            "status": "error",
            "online": False,
            "host": request.host,
            "port": request.port,
            "message": "查询超时 (5s)，服务器可能离线或网络堵塞。"
        }
    except Exception as e:
        # 捕获详细错误以便调试
        error_msg = str(e)
        if "getaddrinfo failed" in error_msg:
            error_msg = "无法解析域名，请检查拼写。"
        elif "10061" in error_msg or "refused" in error_msg:
            error_msg = f"连接被拒绝，请检查 IP 和端口 ({request.port}) 是否正确。"
            
        return {
            "status": "error",
            "online": False,
            "host": request.host,
            "port": request.port,
            "message": f"查询失败: {error_msg}"
        }

@app.get("/")
def read_root():
    return {"message": "Minecraft Query API is running!"}
