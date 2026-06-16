"""
BrowserProxy WebSocket 服务端
Python 程序启动服务端，Chrome 扩展连接进来
支持断线重连和心跳机制
"""

import asyncio
import json
import threading
import time
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
        self.extension_ws: Optional[Any] = None
        self._response_queues: Dict[str, asyncio.Queue] = {}
        self._connected_event = asyncio.Event()
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._server: Optional[Any] = None

        # 心跳和重连
        self._heartbeat_interval = 5  # 秒
        self._last_heartbeat = 0
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._on_disconnect: Optional[Callable] = None
        self._on_reconnect: Optional[Callable] = None

    @property
    def connected(self) -> bool:
        """是否有扩展连接"""
        return self.extension_ws is not None

    @property
    def time_since_last_heartbeat(self) -> float:
        """距离上次心跳的时间（秒）"""
        if self._last_heartbeat == 0:
            return float('inf')
        return time.time() - self._last_heartbeat

    def on_disconnect(self, callback: Callable):
        """注册断开连接回调"""
        self._on_disconnect = callback

    def on_reconnect(self, callback: Callable):
        """注册重新连接回调"""
        self._on_reconnect = callback

    async def _handler(self, websocket: Any):
        """处理新的 WebSocket 连接"""
        try:
            async for message in websocket:
                data = json.loads(message)

                # 心跳响应
                if data.get("type") == "heartbeat":
                    self._last_heartbeat = time.time()
                    await websocket.send(json.dumps({"type": "heartbeat_ack"}))
                    continue

                # Chrome 扩展注册
                if data.get("type") == "register":
                    was_connected = self.extension_ws is not None
                    self.extension_ws = websocket
                    self._connected_event.set()
                    self._last_heartbeat = time.time()

                    logger.info("Chrome 扩展已连接")
                    await websocket.send(json.dumps({"type": "registered", "success": True}))

                    # 如果是重连，触发回调
                    if was_connected and self._on_reconnect:
                        try:
                            self._on_reconnect()
                        except Exception as e:
                            logger.error(f"重连回调执行失败: {e}")
                    continue

                # 处理响应消息
                request_id = data.get("id")
                if request_id and request_id in self._response_queues:
                    await self._response_queues[request_id].put(data)

        except websockets.exceptions.ConnectionClosed:
            logger.info("Chrome 扩展断开连接")
            self.extension_ws = None
            self._connected_event.clear()

            # 触发断开回调
            if self._on_disconnect:
                try:
                    self._on_disconnect()
                except Exception as e:
                    logger.error(f"断开回调执行失败: {e}")

    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self._heartbeat_interval)

                if self.extension_ws and self.time_since_last_heartbeat > self._heartbeat_interval * 3:
                    logger.warning("心跳超时，扩展可能已断开")
                    # 不主动断开，等待扩展重连

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳检测异常: {e}")

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

    async def send_command(self, command: Dict[str, Any], timeout: float = 10) -> Dict[str, Any]:
        """发送命令到 Chrome 扩展

        Args:
            command: 命令字典
            timeout: 超时时间（秒）

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
                response = await asyncio.wait_for(queue.get(), timeout=timeout)
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

        self._server = await websockets.serve(
            self._handler, self.host, self.port,
            max_size=None  # 不限制消息大小，由调用方自行控制
        )
        logger.info("等待 Chrome 扩展连接...")

        # 启动心跳检测
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # 等待关闭信号
        await self._shutdown_event.wait()

        # 停止心跳
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # 关闭服务器
        self._server.close()
        await self._server.wait_closed()
        logger.info("WebSocket 服务端已关闭")

    def shutdown(self):
        """触发关闭信号"""
        self._shutdown_event.set()


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
        if self._server:
            self._server.shutdown()

        if self._thread:
            self._thread.join(timeout=3)

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

    def send_and_receive(self, command: Dict[str, Any], timeout: float = 10) -> Dict[str, Any]:
        """发送命令并接收响应

        Args:
            command: 命令字典
            timeout: 超时时间（秒）

        Returns:
            响应字典
        """
        if not self._server or not self._loop:
            raise ConnectionError("服务端未启动")

        future = asyncio.run_coroutine_threadsafe(
            self._server.send_command(command, timeout),
            self._loop
        )
        return future.result(timeout=timeout + 5)

    def on_disconnect(self, callback: Callable):
        """注册断开连接回调"""
        if self._server:
            self._server.on_disconnect(callback)

    def on_reconnect(self, callback: Callable):
        """注册重新连接回调"""
        if self._server:
            self._server.on_reconnect(callback)
