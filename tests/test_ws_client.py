"""WebSocket 客户端测试"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from browserproxy.ws_client import WebSocketClient


class TestWebSocketClient:
    """WebSocket 客户端测试"""

    def test_init_default_values(self):
        """测试默认初始化值"""
        client = WebSocketClient()
        assert client.host == "localhost"
        assert client.port == 8765
        assert client.connected is False

    def test_init_custom_values(self):
        """测试自定义初始化值"""
        client = WebSocketClient(host="127.0.0.1", port=9000)
        assert client.host == "127.0.0.1"
        assert client.port == 9000

    def test_get_url(self):
        """测试获取 WebSocket URL"""
        client = WebSocketClient()
        assert client.url == "ws://localhost:8765"

    def test_get_url_custom(self):
        """测试获取自定义 WebSocket URL"""
        client = WebSocketClient(host="192.168.1.1", port=8080)
        assert client.url == "ws://192.168.1.1:8080"

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_connect_success(self, mock_ws_class):
        """测试连接成功"""
        mock_ws = MagicMock()
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        client.connect()

        assert client.connected is True
        mock_ws.connect.assert_called_once_with("ws://localhost:8765")

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_connect_failure(self, mock_ws_class):
        """测试连接失败"""
        mock_ws = MagicMock()
        mock_ws.connect.side_effect = Exception("Connection refused")
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        with pytest.raises(Exception) as exc_info:
            client.connect()
        assert "Connection refused" in str(exc_info.value)
        assert client.connected is False

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_disconnect(self, mock_ws_class):
        """测试断开连接"""
        mock_ws = MagicMock()
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        client.connect()
        client.disconnect()

        assert client.connected is False
        mock_ws.close.assert_called_once()

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_send_command(self, mock_ws_class):
        """测试发送命令"""
        mock_ws = MagicMock()
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        client.connect()

        command = {
            "id": "req-001",
            "tab_id": 123,
            "action": "click",
            "params": {"selector": "#btn"}
        }

        client.send(command)

        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["id"] == "req-001"
        assert sent_data["action"] == "click"

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_send_when_not_connected(self, mock_ws_class):
        """测试未连接时发送命令"""
        client = WebSocketClient()

        with pytest.raises(ConnectionError) as exc_info:
            client.send({"action": "click"})
        assert "not connected" in str(exc_info.value).lower()

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_receive_response(self, mock_ws_class):
        """测试接收响应"""
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({
            "id": "req-001",
            "success": True,
            "data": None
        })
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        client.connect()

        response = client.receive()

        assert response["id"] == "req-001"
        assert response["success"] is True

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_send_and_receive(self, mock_ws_class):
        """测试发送命令并接收响应"""
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({
            "id": "req-001",
            "success": True,
            "data": {"title": "百度一下"}
        })
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        client.connect()

        command = {
            "id": "req-001",
            "tab_id": 123,
            "action": "get_text",
            "params": {"selector": "title"}
        }

        response = client.send_and_receive(command)

        assert response["success"] is True
        assert response["data"]["title"] == "百度一下"

    @patch('browserproxy.ws_client.websocket.WebSocket')
    def test_receive_event(self, mock_ws_class):
        """测试接收事件推送"""
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({
            "event": "page_loaded",
            "tab_id": 123,
            "url": "https://example.com"
        })
        mock_ws_class.return_value = mock_ws

        client = WebSocketClient()
        client.connect()

        event = client.receive()

        assert event["event"] == "page_loaded"
        assert event["tab_id"] == 123
