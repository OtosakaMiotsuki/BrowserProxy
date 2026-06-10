"""WebSocket 客户端模块"""

import json
from typing import Any, Dict, Optional
from loguru import logger
import websocket


class WebSocketClient:
    """WebSocket 客户端，用于连接 Chrome 扩展"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """初始化 WebSocket 客户端

        Args:
            host: WebSocket 服务器地址
            port: WebSocket 服务器端口
        """
        self.host = host
        self.port = port
        self.connected = False
        self._ws: Optional[websocket.WebSocket] = None

    @property
    def url(self) -> str:
        """获取 WebSocket URL"""
        return f"ws://{self.host}:{self.port}"

    def connect(self) -> None:
        """连接到 WebSocket 服务器"""
        try:
            self._ws = websocket.WebSocket()
            self._ws.connect(self.url)
            self.connected = True
            logger.info(f"已连接到 {self.url}")
        except Exception as e:
            self.connected = False
            logger.error(f"连接失败: {e}")
            raise

    def disconnect(self) -> None:
        """断开 WebSocket 连接"""
        if self._ws:
            self._ws.close()
            self._ws = None
        self.connected = False
        logger.info("已断开连接")

    def send(self, command: Dict[str, Any]) -> None:
        """发送命令

        Args:
            command: 命令字典

        Raises:
            ConnectionError: 未连接时抛出
        """
        if not self.connected:
            raise ConnectionError("WebSocket not connected")

        data = json.dumps(command)
        self._ws.send(data)
        logger.debug(f"发送命令: {command.get('action')}")

    def receive(self) -> Dict[str, Any]:
        """接收消息

        Returns:
            接收到的消息字典
        """
        if not self.connected:
            raise ConnectionError("WebSocket not connected")

        data = self._ws.recv()
        message = json.loads(data)
        logger.debug(f"接收消息: {message}")
        return message

    def send_and_receive(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """发送命令并接收响应

        Args:
            command: 命令字典

        Returns:
            响应字典
        """
        self.send(command)
        return self.receive()
