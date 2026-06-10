"""Browser 类测试"""

import pytest
from unittest.mock import MagicMock, patch
from browserproxy.browser import Browser
from browserproxy.tab import Tab


class TestBrowser:
    """Browser 类测试"""

    def test_init_default_values(self):
        """测试默认初始化值"""
        browser = Browser()
        assert browser.host == "localhost"
        assert browser.port == 8765

    def test_init_custom_values(self):
        """测试自定义初始化值"""
        browser = Browser(host="192.168.1.1", port=9000)
        assert browser.host == "192.168.1.1"
        assert browser.port == 9000

    def test_tabs_initially_empty(self):
        """测试初始标签页列表为空"""
        browser = Browser()
        assert len(browser.tabs) == 0

    @patch('browserproxy.browser.WebSocketClient')
    def test_connect(self, mock_ws_class):
        """测试连接浏览器"""
        mock_ws = MagicMock()
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()

        mock_ws.connect.assert_called_once()
        assert browser.connected is True

    @patch('browserproxy.browser.WebSocketClient')
    def test_disconnect(self, mock_ws_class):
        """测试断开连接"""
        mock_ws = MagicMock()
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()
        browser.disconnect()

        mock_ws.disconnect.assert_called_once()
        assert browser.connected is False

    @patch('browserproxy.browser.WebSocketClient')
    def test_get_tabs(self, mock_ws_class):
        """测试获取标签页列表"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": [
                {"id": 1, "url": "https://www.baidu.com", "title": "百度一下"},
                {"id": 2, "url": "https://www.google.com", "title": "Google"},
            ]
        }
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()
        tabs = browser.get_tabs()

        assert len(tabs) == 2
        assert isinstance(tabs[0], Tab)
        assert tabs[0].tab_id == 1
        assert tabs[1].tab_id == 2

    @patch('browserproxy.browser.WebSocketClient')
    def test_match_tab(self, mock_ws_class):
        """测试匹配标签页"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": [
                {"id": 1, "url": "https://www.baidu.com", "title": "百度一下"},
                {"id": 2, "url": "https://www.google.com", "title": "Google"},
            ]
        }
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()

        tab = browser.match(url_contains="baidu")

        assert tab is not None
        assert tab.tab_id == 1

    @patch('browserproxy.browser.WebSocketClient')
    def test_match_tab_not_found(self, mock_ws_class):
        """测试匹配标签页未找到"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": [
                {"id": 1, "url": "https://www.baidu.com", "title": "百度一下"},
            ]
        }
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()

        tab = browser.match(url_contains="bilibili")

        assert tab is None

    @patch('browserproxy.browser.WebSocketClient')
    def test_match_tab_multiple_results(self, mock_ws_class):
        """测试多个匹配结果"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": [
                {"id": 1, "url": "https://www.baidu.com", "title": "百度一下"},
                {"id": 2, "url": "https://m.baidu.com", "title": "百度一下"},
            ]
        }
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()

        tabs = browser.match_all(url_contains="baidu")

        assert len(tabs) == 2
        assert tabs[0].tab_id == 1
        assert tabs[1].tab_id == 2

    @patch('browserproxy.browser.WebSocketClient')
    def test_select_tab(self, mock_ws_class):
        """测试选择标签页"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": [
                {"id": 1, "url": "https://www.baidu.com", "title": "百度一下"},
            ]
        }
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()

        tab = browser.select_tab(1)

        assert tab is not None
        assert tab.tab_id == 1

    @patch('browserproxy.browser.WebSocketClient')
    def test_select_tab_not_found(self, mock_ws_class):
        """测试选择不存在的标签页"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": [
                {"id": 1, "url": "https://www.baidu.com", "title": "百度一下"},
            ]
        }
        mock_ws_class.return_value = mock_ws

        browser = Browser()
        browser.connect()

        tab = browser.select_tab(999)

        assert tab is None
