"""Tab 类模块"""

from typing import Any, Dict, Optional
from loguru import logger


class Tab:
    """标签页类，执行 DOM 操作"""

    def __init__(self, tab_id: int, ws_client: Any, url: str = "", title: str = ""):
        """初始化标签页

        Args:
            tab_id: 标签页 ID
            ws_client: WebSocket 客户端
            url: 标签页 URL
            title: 标签页标题
        """
        self.tab_id = tab_id
        self.url = url
        self.title = title
        self._ws_client = ws_client

    def _send_command(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送命令到标签页

        Args:
            action: 操作类型
            params: 参数

        Returns:
            响应结果
        """
        command = {
            "tab_id": self.tab_id,
            "action": action,
            "params": params or {}
        }
        return self._ws_client.send_and_receive(command)

    def ele(self, selector: str) -> "Element":
        """获取元素

        Args:
            selector: CSS 或 XPath 选择器

        Returns:
            Element 对象
        """
        return Element(self, selector)

    def get(self, url: str) -> None:
        """跳转到指定 URL

        Args:
            url: 目标 URL
        """
        logger.debug(f"跳转到 {url}")
        self._send_command("navigate", {"url": url})

    def back(self) -> None:
        """后退"""
        logger.debug("后退")
        self._send_command("back")

    def forward(self) -> None:
        """前进"""
        logger.debug("前进")
        self._send_command("forward")

    def refresh(self) -> None:
        """刷新页面"""
        logger.debug("刷新页面")
        self._send_command("refresh")

    def run_js(self, script: str) -> Any:
        """执行 JavaScript 代码

        Args:
            script: JS 代码

        Returns:
            执行结果
        """
        logger.debug(f"执行 JS: {script[:50]}...")
        response = self._send_command("execute_script", {"script": script})
        if response.get("success"):
            return response.get("data")
        raise Exception(f"JS 执行失败: {response.get('error')}")


class Element:
    """元素类"""

    def __init__(self, tab: Tab, selector: str):
        """初始化元素

        Args:
            tab: 所属标签页
            selector: 选择器
        """
        self._tab = tab
        self._selector = selector

    def click(self) -> None:
        """点击元素"""
        logger.debug(f"点击元素: {self._selector}")
        self._tab._send_command("click", {"selector": self._selector})

    def input(self, text: str) -> None:
        """输入文本

        Args:
            text: 要输入的文本
        """
        logger.debug(f"输入文本到 {self._selector}: {text}")
        self._tab._send_command("input", {"selector": self._selector, "text": text})

    @property
    def text(self) -> str:
        """获取元素文本"""
        logger.debug(f"获取元素文本: {self._selector}")
        response = self._tab._send_command("get_text", {"selector": self._selector})
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取文本失败: {response.get('error')}")

    def attr(self, name: str) -> Optional[str]:
        """获取元素属性

        Args:
            name: 属性名

        Returns:
            属性值
        """
        logger.debug(f"获取元素属性: {self._selector}.{name}")
        response = self._tab._send_command("get_attr", {
            "selector": self._selector,
            "attr": name
        })
        if response.get("success"):
            return response.get("data")
        raise Exception(f"获取属性失败: {response.get('error')}")

    def exists(self) -> bool:
        """检查元素是否存在

        Returns:
            元素是否存在
        """
        logger.debug(f"检查元素是否存在: {self._selector}")
        response = self._tab._send_command("exists", {"selector": self._selector})
        if response.get("success"):
            return response.get("data", False)
        raise Exception(f"检查元素失败: {response.get('error')}")
