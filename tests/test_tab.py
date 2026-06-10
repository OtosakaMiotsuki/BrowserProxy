"""Tab 类测试"""

import pytest
from unittest.mock import MagicMock
from browserproxy.tab import Tab, Element


class TestTab:
    """Tab 类测试"""

    def _create_mock_ws_server(self):
        """创建模拟 WebSocket 服务端"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": None
        }
        return mock_ws

    def test_init(self):
        """测试初始化"""
        mock_ws = self._create_mock_ws_server()
        tab = Tab(tab_id=1, ws_server=mock_ws, url="https://example.com", title="Example")

        assert tab.tab_id == 1
        assert tab.url == "https://example.com"
        assert tab.title == "Example"

    def test_ele_returns_element(self):
        """测试 ele 方法返回 Element 对象"""
        mock_ws = self._create_mock_ws_server()
        tab = Tab(tab_id=1, ws_server=mock_ws)

        element = tab.ele("#btn")

        assert isinstance(element, Element)
        assert element._selector == "#btn"

    def test_get_sends_navigate_command(self):
        """测试 get 方法发送导航命令"""
        mock_ws = self._create_mock_ws_server()
        tab = Tab(tab_id=1, ws_server=mock_ws)

        tab.get("https://example.com")

        mock_ws.send_and_receive.assert_called_once()
        call_args = mock_ws.send_and_receive.call_args[0][0]
        assert call_args["action"] == "navigate"
        assert call_args["params"]["url"] == "https://example.com"

    def test_back_sends_back_command(self):
        """测试 back 方法发送后退命令"""
        mock_ws = self._create_mock_ws_server()
        tab = Tab(tab_id=1, ws_server=mock_ws)

        tab.back()

        mock_ws.send_and_receive.assert_called_once()
        call_args = mock_ws.send_and_receive.call_args[0][0]
        assert call_args["action"] == "back"

    def test_forward_sends_forward_command(self):
        """测试 forward 方法发送前进命令"""
        mock_ws = self._create_mock_ws_server()
        tab = Tab(tab_id=1, ws_server=mock_ws)

        tab.forward()

        mock_ws.send_and_receive.assert_called_once()
        call_args = mock_ws.send_and_receive.call_args[0][0]
        assert call_args["action"] == "forward"

    def test_refresh_sends_refresh_command(self):
        """测试 refresh 方法发送刷新命令"""
        mock_ws = self._create_mock_ws_server()
        tab = Tab(tab_id=1, ws_server=mock_ws)

        tab.refresh()

        mock_ws.send_and_receive.assert_called_once()
        call_args = mock_ws.send_and_receive.call_args[0][0]
        assert call_args["action"] == "refresh"

    def test_run_js_sends_execute_script_command(self):
        """测试 run_js 方法发送执行脚本命令"""
        mock_ws = self._create_mock_ws_server()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": "Example Domain"
        }
        tab = Tab(tab_id=1, ws_server=mock_ws)

        result = tab.run_js("return document.title")

        assert result == "Example Domain"
        call_args = mock_ws.send_and_receive.call_args[0][0]
        assert call_args["action"] == "execute_script"
        assert call_args["params"]["script"] == "return document.title"

    def test_run_js_raises_on_failure(self):
        """测试 run_js 方法在失败时抛出异常"""
        mock_ws = self._create_mock_ws_server()
        mock_ws.send_and_receive.return_value = {
            "success": False,
            "error": "Syntax error"
        }
        tab = Tab(tab_id=1, ws_server=mock_ws)

        with pytest.raises(Exception) as exc_info:
            tab.run_js("invalid code")
        assert "Syntax error" in str(exc_info.value)


class TestElement:
    """Element 类测试"""

    def _create_mock_tab(self):
        """创建模拟 Tab 对象"""
        mock_ws = MagicMock()
        mock_ws.send_and_receive.return_value = {
            "success": True,
            "data": None
        }
        return Tab(tab_id=1, ws_server=mock_ws)

    def test_init(self):
        """测试初始化"""
        tab = self._create_mock_tab()
        element = Element(tab, "#btn")

        assert element._tab == tab
        assert element._selector == "#btn"

    def test_click_sends_click_command(self):
        """测试 click 方法发送点击命令"""
        tab = self._create_mock_tab()
        element = Element(tab, "#btn")

        element.click()

        tab._ws_server.send_and_receive.assert_called_once()
        call_args = tab._ws_server.send_and_receive.call_args[0][0]
        assert call_args["action"] == "click"
        assert call_args["params"]["selector"] == "#btn"

    def test_input_sends_input_command(self):
        """测试 input 方法发送输入命令"""
        tab = self._create_mock_tab()
        element = Element(tab, "#input")

        element.input("hello world")

        tab._ws_server.send_and_receive.assert_called_once()
        call_args = tab._ws_server.send_and_receive.call_args[0][0]
        assert call_args["action"] == "input"
        assert call_args["params"]["selector"] == "#input"
        assert call_args["params"]["text"] == "hello world"

    def test_text_returns_element_text(self):
        """测试 text 属性返回元素文本"""
        tab = self._create_mock_tab()
        tab._ws_server.send_and_receive.return_value = {
            "success": True,
            "data": "Hello World"
        }
        element = Element(tab, ".title")

        result = element.text

        assert result == "Hello World"

    def test_attr_returns_element_attribute(self):
        """测试 attr 方法返回元素属性"""
        tab = self._create_mock_tab()
        tab._ws_server.send_and_receive.return_value = {
            "success": True,
            "data": "https://example.com"
        }
        element = Element(tab, "a")

        result = element.attr("href")

        assert result == "https://example.com"

    def test_exists_returns_true_when_element_exists(self):
        """测试 exists 方法在元素存在时返回 True"""
        tab = self._create_mock_tab()
        tab._ws_server.send_and_receive.return_value = {
            "success": True,
            "data": True
        }
        element = Element(tab, "#btn")

        result = element.exists()

        assert result is True

    def test_exists_returns_false_when_element_not_exists(self):
        """测试 exists 方法在元素不存在时返回 False"""
        tab = self._create_mock_tab()
        tab._ws_server.send_and_receive.return_value = {
            "success": True,
            "data": False
        }
        element = Element(tab, "#nonexistent")

        result = element.exists()

        assert result is False

    def test_text_raises_on_failure(self):
        """测试 text 属性在失败时抛出异常"""
        tab = self._create_mock_tab()
        tab._ws_server.send_and_receive.return_value = {
            "success": False,
            "error": "Element not found"
        }
        element = Element(tab, "#nonexistent")

        with pytest.raises(Exception) as exc_info:
            _ = element.text
        assert "Element not found" in str(exc_info.value)
