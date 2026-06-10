"""
BrowserProxy WebSocket 服务端
Python 程序启动服务端，Chrome 扩展连接进来
"""

import asyncio
import json
import threading
from typing import Any, Dict, Optional
from loguru import logger
import websockets
from collections import defaultdict


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
        self.extension_ws: Optional[Any] = None
        self._response_queues: Dict[str, asyncio.Queue] = {}
        self._connected_event = asyncio.Event()
        self._lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        """是否有扩展连接"""
        return self.extension_ws is not None

    async def _handler(self, websocket: Any):
        """处理新的 WebSocket 连接"""
        try:
            async for message in websocket:
                data = json.loads(message)

                # Chrome 扩展注册
                if data.get("type") == "register":
                    self.extension_ws = websocket
                    self._connected_event.set()
                    logger.info("Chrome 扩展已连接")
                    await websocket.send(json.dumps({"type": "registered", "success": True}))
                    continue

                # 处理响应消息
                request_id = data.get("id")
                if request_id and request_id in self._response_queues:
                    await self._response_queues[request_id].put(data)

        except websockets.exceptions.ConnectionClosed:
            logger.info("Chrome 扩展断开连接")
            self.extension_ws = None
            self._connected_event.clear()

    async def wait_for_connection(self, timeout: float = 30) -> bool:
        """等待扩展连接

        Args:
            timeout: 超时时间（秒）

        Returns:
            是否连接成功
        """
        try:
            await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """发送命令到 Chrome 扩展

        Args:
            command: 命令字典

        Returns:
            响应字典
        """
        if not self.extension_ws:
            raise ConnectionError("Chrome 扩展未连接")

        # 生成请求 ID
        request_id = command.get("id", str(id(command)))
        command["id"] = request_id

        # 创建响应队列
        queue = asyncio.Queue()
        async with self._lock:
            self._response_queues[request_id] = queue

        try:
            # 发送命令
            await self.extension_ws.send(json.dumps(command))

            # 等待响应（带超时）
            try:
                response = await asyncio.wait_for(queue.get(), timeout=10)
                return response
            except asyncio.TimeoutError:
                raise TimeoutError(f"命令执行超时: {command.get('action')}")
        finally:
            # 清理队列
            async with self._lock:
                self._response_queues.pop(request_id, None)

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
        self._thread: Optional[threading.Thread] = None
        self._started_event = threading.Event()

    @property
    def connected(self) -> bool:
        """是否有扩展连接"""
        return self._server.connected if self._server else False

    def start(self):
        """启动服务端（非阻塞）"""
        self._server = WebSocketServer(self.host, self.port)
        self._loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(self._loop)
            self._started_event.set()
            self._loop.run_until_complete(self._server.start())

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        self._started_event.wait()
        logger.info(f"WebSocket 服务端已启动: ws://{self.host}:{self.port}")

    def stop(self):
        """停止服务端"""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("WebSocket 服务端已停止")

    def wait_for_connection(self, timeout: float = 30) -> bool:
        """等待扩展连接

        Args:
            timeout: 超时时间（秒）

        Returns:
            是否连接成功
        """
        if not self._server or not self._loop:
            raise ConnectionError("服务端未启动")

        future = asyncio.run_coroutine_threadsafe(
            self._server.wait_for_connection(timeout),
            self._loop
        )
        return future.result(timeout=timeout + 1)

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
        return future.result(timeout=15)
