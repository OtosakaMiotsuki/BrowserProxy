"""Browser 类模块"""

from typing import List, Optional, Dict, Any
from loguru import logger
from .ws_server import SyncWebSocketServer
from .tab import Tab
from .match import TabMatcher


class Browser:
    """浏览器类，管理连接和标签页"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """初始化浏览器

        Args:
            host: WebSocket 服务器地址
            port: WebSocket 服务器端口
        """
        self.host = host
        self.port = port
        self._ws_server = SyncWebSocketServer(host, port)
        self._tabs: List[Tab] = []
        self.connected = False

    @property
    def tabs(self) -> List[Tab]:
        """获取标签页列表"""
        return self._tabs

    def connect(self, timeout: float = 30) -> None:
        """启动服务并等待 Chrome 扩展连接

        Args:
            timeout: 等待扩展连接的超时时间（秒）

        Raises:
            TimeoutError: 等待超时
        """
        self._ws_server.start()
        logger.info("正在等待 Chrome 扩展连接...")

        # 等待扩展连接
        if not self._ws_server.wait_for_connection(timeout):
            raise TimeoutError("等待 Chrome 扩展连接超时，请确保扩展已安装并输入了正确的端口号")

        self.connected = True
        logger.info("Chrome 扩展已连接！")

    def disconnect(self) -> None:
        """断开连接"""
        self._ws_server.stop()
        self.connected = False
        self._tabs = []
        logger.info("已断开连接")

    def get_tabs(self) -> List[Tab]:
        """获取所有标签页

        Returns:
            标签页列表
        """
        if not self.connected:
            raise ConnectionError("未连接到浏览器扩展")

        response = self._ws_server.send_and_receive({
            "action": "list_tabs"
        })

        if not response.get("success"):
            raise Exception(f"获取标签页失败: {response.get('error')}")

        self._tabs = []
        for tab_data in response.get("data", []):
            tab = Tab(
                tab_id=tab_data["id"],
                ws_server=self._ws_server,
                url=tab_data.get("url", ""),
                title=tab_data.get("title", "")
            )
            self._tabs.append(tab)

        logger.info(f"获取到 {len(self._tabs)} 个标签页")
        return self._tabs

    def match(
        self,
        url_contains: str = "",
        title_contains: str = ""
    ) -> Optional[Tab]:
        """匹配标签页

        Args:
            url_contains: URL 包含的字符串
            title_contains: 标题包含的字符串

        Returns:
            匹配的 Tab 对象，如果没有匹配返回 None
        """
        if not self._tabs:
            self.get_tabs()

        return TabMatcher.match(self._tabs, url_contains, title_contains)

    def match_all(
        self,
        url_contains: str = "",
        title_contains: str = ""
    ) -> List[Tab]:
        """查找所有匹配的标签页

        Args:
            url_contains: URL 包含的字符串
            title_contains: 标题包含的字符串

        Returns:
            匹配的 Tab 列表
        """
        if not self._tabs:
            self.get_tabs()

        return TabMatcher.find_all(self._tabs, url_contains, title_contains)

    def select_tab(self, tab_id: int) -> Optional[Tab]:
        """选择标签页

        Args:
            tab_id: 标签页 ID

        Returns:
            Tab 对象，如果不存在返回 None
        """
        if not self._tabs:
            self.get_tabs()

        for tab in self._tabs:
            if tab.tab_id == tab_id:
                return tab

        logger.warning(f"标签页 {tab_id} 不存在")
        return None
