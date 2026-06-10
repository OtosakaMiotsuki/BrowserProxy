"""
BrowserProxy WebSocket 服务端
Python 程序启动服务端，Chrome 扩展连接进来
"""

import asyncio
import json
from typing import Any, Callable, Dict, Optional
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
        self.extension_ws: Optional[websockets.WebSocketServerProtocol] = None
        self._pending_responses: Dict[str, websockets.WebSocketServerProtocol] = {}
        self._message_handler: Optional[Callable] = None

    @property
    def connected(self) -> bool:
        """是否有扩展连接"""
        return self.extension_ws is not None

    def on_message(self, handler: Callable):
        """设置消息处理器"""
        self._message_handler = handler

    async def _handler(self, websocket: websockets.WebSocketServerProtocol):
        """处理新的 WebSocket 连接"""
        try:
            async for message in websocket:
                data = json.loads(message)

                # Chrome 扩展注册
                if data.get("type") == "register":
                    self.extension_ws = websocket
                    logger.info("Chrome 扩展已连接")
                    await websocket.send(json.dumps({"type": "registered", "success": True}))
                    continue

                # 转发消息给处理器
                if self._message_handler:
                    response = await self._message_handler(data)
                    if response:
                        await websocket.send(json.dumps(response))

        except websockets.exceptions.ConnectionClosed:
            logger.info("Chrome 扩展断开连接")
            self.extension_ws = None

    async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """发送命令到 Chrome 扩展

        Args:
            command: 命令字典

        Returns:
            响应字典
        """
        if not self.extension_ws:
            raise ConnectionError("Chrome 扩展未连接")

        # 发送命令
        await self.extension_ws.send(json.dumps(command))

        # 等待响应
        response = await self.extension_ws.recv()
        return json.loads(response)

    async def start(self):
        """启动服务端"""
        logger.info(f"WebSocket 服务端启动: ws://{self.host}:{self.port}")

        async with websockets.serve(self._handler, self.host, self.port):
            logger.info("等待 Chrome 扩展连接...")
            await asyncio.Future()  # 永远运行


class SyncWebSocketServer:
    """同步 WebSocket 服务端包装器"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """初始化

        Args:
            host: 监听地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self._server: Optional[WebSocketServer] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[Any] = None

    @property
    def connected(self) -> bool:
        """是否有扩展连接"""
        return self._server.connected if self._server else False

    def start(self):
        """启动服务端（非阻塞）"""
        import threading

        self._server = WebSocketServer(self.host, self.port)
        self._loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._server.start())

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        logger.info(f"WebSocket 服务端已启动: ws://{self.host}:{self.port}")

    def stop(self):
        """停止服务端"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("WebSocket 服务端已停止")

    def send_and_receive(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """发送命令并接收响应

        Args:
            command: 命令字典

        Returns:
            响应字典
        """
        if not self._server or not self._loop:
            raise ConnectionError("服务端未启动")

        future = asyncio.run_coroutine_threadsafe(
            self._server.send_command(command),
            self._loop
        )
        return future.result(timeout=10)
