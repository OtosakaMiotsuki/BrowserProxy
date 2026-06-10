"""
BrowserProxy WebSocket 服务端
作为 Chrome 扩展和 Python 客户端之间的桥梁
"""

import asyncio
import json
from typing import Dict, Set
from loguru import logger
import websockets


class WebSocketServer:
    """WebSocket 服务端"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """初始化服务端

        Args:
            host: 监听地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self.extension_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.python_clients: Set[websockets.WebSocketServerProtocol] = set()
        self.pending_responses: Dict[str, websockets.WebSocketServerProtocol] = {}

    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        """处理新的 WebSocket 连接"""
        client_type = None

        try:
            # 第一条消息声明身份
            async for message in websocket:
                data = json.loads(message)

                # 身份注册
                if data.get("type") == "register":
                    client_type = data.get("client_type")
                    if client_type == "extension":
                        self.extension_clients.add(websocket)
                        logger.info(f"Chrome 扩展已连接 (共 {len(self.extension_clients)} 个)")
                        await websocket.send(json.dumps({"type": "registered", "success": True}))
                    elif client_type == "python":
                        self.python_clients.add(websocket)
                        logger.info(f"Python 客户端已连接 (共 {len(self.python_clients)} 个)")
                        await websocket.send(json.dumps({"type": "registered", "success": True}))
                    continue

                # 转发消息
                if client_type == "python":
                    # Python -> Extension
                    if self.extension_clients:
                        # 存储待响应的连接
                        request_id = data.get("id")
                        if request_id:
                            self.pending_responses[request_id] = websocket

                        # 转发给所有扩展
                        for ext in self.extension_clients:
                            await ext.send(message)
                            logger.debug(f"转发消息到扩展: {data.get('action')}")
                    else:
                        await websocket.send(json.dumps({
                            "id": data.get("id"),
                            "success": False,
                            "error": "没有连接的 Chrome 扩展"
                        }))

                elif client_type == "extension":
                    # Extension -> Python
                    request_id = data.get("id")
                    if request_id and request_id in self.pending_responses:
                        # 发送给请求方
                        py_client = self.pending_responses.pop(request_id)
                        await py_client.send(message)
                        logger.debug(f"返回响应给 Python: {request_id}")
                    else:
                        # 广播给所有 Python 客户端
                        for py in self.python_clients:
                            await py.send(message)

        except websockets.exceptions.ConnectionClosed:
            logger.info("连接关闭")
        finally:
            # 清理连接
            if client_type == "extension":
                self.extension_clients.discard(websocket)
                logger.info(f"Chrome 扩展断开 (剩余 {len(self.extension_clients)} 个)")
            elif client_type == "python":
                self.python_clients.discard(websocket)
                logger.info(f"Python 客户端断开 (剩余 {len(self.python_clients)} 个)")

    async def start(self):
        """启动服务端"""
        logger.info(f"WebSocket 服务端启动: ws://{self.host}:{self.port}")

        async with websockets.serve(self.handler, self.host, self.port):
            logger.info("等待连接...")
            await asyncio.Future()  # 永远运行


def main():
    """主函数"""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="DEBUG"
    )

    server = WebSocketServer()
    asyncio.run(server.start())


if __name__ == "__main__":
    main()
