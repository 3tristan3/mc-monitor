from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcstatus import JavaServer  # <---【重大修正】这里是关键！将 MinecraftServer 改为 JavaServer
import asyncio

# 初始化 FastAPI 应用
app = FastAPI()

# 定义请求体的数据模型
class QueryRequest(BaseModel):
    host: str
    port: int = 25565

# 定义API端点
@app.post("/api/query")
async def query_server(request: QueryRequest):
    """
    接收服务器地址和端口，异步查询服务器状态。
    """
    try:
        # 【重大修正】使用 JavaServer.lookup
        server = await asyncio.wait_for(
            JavaServer.lookup(f"{request.host}:{request.port}").async_status(),
            timeout=5.0
        )

        # 构建一个完美的JSON响应
        return {
            "status": "success",
            "online": True,
            "host": request.host,
            "port": request.port,
            "motd": server.description,
            "version": server.version.name,
            "players": {
                "online": server.players.online,
                "max": server.players.max
            },
            "latency": round(server.latency),
            "favicon": server.favicon
        }

    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Query timed out. The server might be slow or offline.")
    except Exception as e:
        # 捕获所有其他可能的异常
        return {
            "status": "error",
            "online": False,
            "host": request.host,
            "port": request.port,
            "message": f"Server is offline or does not exist. Error: {e}"
        }

# 本地测试用的根路由
@app.get("/")
def read_root():
    return {"message": "Minecraft Query API is running!"}
