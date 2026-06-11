"""Tab 类模块"""

import time
from typing import Any, Dict, List, Optional
from loguru import logger


class Tab:
    """标签页类，执行 DOM 操作和页面操作"""

    def __init__(self, tab_id: int, ws_server: Any, url: str = "", title: str = ""):
        """初始化标签页

        Args:
            tab_id: 标签页 ID
            ws_server: WebSocket 服务端
            url: 标签页 URL
            title: 标签页标题
        """
        self.tab_id = tab_id
        self.url = url
        self.title = title
        self._ws_server = ws_server

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
        return self._ws_server.send_and_receive(command)

    # ========== 元素选择 ==========

    def ele(self, selector: str) -> "Element":
        """获取单个元素

        Args:
            selector: CSS 或 XPath 选择器

        Returns:
            Element 对象
        """
        return Element(self, selector)

    def eles(self, selector: str) -> List["Element"]:
        """获取所有匹配的元素

        Args:
            selector: CSS 或 XPath 选择器

        Returns:
            Element 列表
        """
        return Elements(self, selector)

    # ========== 页面导航 ==========

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

    # ========== 页面内容 ==========

    @property
    def html(self) -> str:
        """获取页面 HTML"""
        logger.debug("获取页面 HTML")
        response = self._send_command("get_page_html")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取页面 HTML 失败: {response.get('error')}")

    @property
    def text(self) -> str:
        """获取页面文本"""
        logger.debug("获取页面文本")
        response = self._send_command("get_page_text")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取页面文本失败: {response.get('error')}")

    @property
    def current_url(self) -> str:
        """获取当前 URL"""
        logger.debug("获取当前 URL")
        response = self._send_command("get_page_url")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取 URL 失败: {response.get('error')}")

    @property
    def current_title(self) -> str:
        """获取当前标题"""
        logger.debug("获取当前标题")
        response = self._send_command("get_page_title")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取标题失败: {response.get('error')}")

    # ========== 页面滚动 ==========

    def scroll_to(self, x: int = 0, y: int = 0) -> None:
        """滚动到指定位置

        Args:
            x: X 坐标
            y: Y 坐标
        """
        logger.debug(f"滚动到 ({x}, {y})")
        self._send_command("scroll_to", {"x": x, "y": y})

    def scroll_by(self, x: int = 0, y: int = 0) -> None:
        """滚动指定距离

        Args:
            x: X 轴滚动距离
            y: Y 轴滚动距离
        """
        logger.debug(f"滚动 ({x}, {y})")
        self._send_command("scroll_by", {"x": x, "y": y})

    def scroll_to_top(self) -> None:
        """滚动到顶部"""
        self.scroll_to(y=0)

    def scroll_to_bottom(self) -> None:
        """滚动到底部"""
        self.scroll_by(y=999999)

    # ========== 等待 ==========

    def wait(self, seconds: float) -> None:
        """等待指定时间

        Args:
            seconds: 等待秒数
        """
        logger.debug(f"等待 {seconds} 秒")
        time.sleep(seconds)

    def wait_for_load(self, timeout: float = 10) -> None:
        """等待页面加载完成

        Args:
            timeout: 超时时间（秒）
        """
        logger.debug(f"等待页面加载 (超时: {timeout}s)")
        self._send_command("wait_for_load", {"timeout": int(timeout * 1000)})

    def wait_for_element(self, selector: str, timeout: float = 10) -> "Element":
        """等待元素出现

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（秒）

        Returns:
            Element 对象
        """
        logger.debug(f"等待元素出现: {selector} (超时: {timeout}s)")
        response = self._send_command("wait_for_element", {
            "selector": selector,
            "timeout": int(timeout * 1000)
        })
        if response.get("success"):
            return Element(self, selector)
        raise Exception(f"等待元素超时: {selector}")

    def wait_for_element_visible(self, selector: str, timeout: float = 10) -> "Element":
        """等待元素可见

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（秒）

        Returns:
            Element 对象
        """
        logger.debug(f"等待元素可见: {selector} (超时: {timeout}s)")
        response = self._send_command("wait_for_element_visible", {
            "selector": selector,
            "timeout": int(timeout * 1000)
        })
        if response.get("success"):
            return Element(self, selector)
        raise Exception(f"等待元素可见超时: {selector}")

    def wait_for_element_hidden(self, selector: str, timeout: float = 10) -> None:
        """等待元素消失

        Args:
            selector: CSS 或 XPath 选择器
            timeout: 超时时间（秒）
        """
        logger.debug(f"等待元素消失: {selector} (超时: {timeout}s)")
        response = self._send_command("wait_for_element_hidden", {
            "selector": selector,
            "timeout": int(timeout * 1000)
        })
        if not response.get("success"):
            raise Exception(f"等待元素消失超时: {selector}")

    def wait_for_text(self, text: str, timeout: float = 10) -> None:
        """等待页面包含指定文本

        Args:
            text: 要等待的文本
            timeout: 超时时间（秒）
        """
        logger.debug(f"等待文本: '{text}' (超时: {timeout}s)")
        response = self._send_command("wait_for_text", {
            "text": text,
            "timeout": int(timeout * 1000)
        })
        if not response.get("success"):
            raise Exception(f"等待文本超时: {text}")

    # ========== 高级元素查找 ==========

    def find_by_text(self, text: str, exact: bool = True) -> List[Dict[str, str]]:
        """按文本查找元素

        Args:
            text: 要查找的文本
            exact: 是否精确匹配

        Returns:
            匹配的元素列表
        """
        logger.debug(f"按文本查找: '{text}' (精确: {exact})")
        response = self._send_command("find_by_text", {"text": text, "exact": exact})
        if response.get("success"):
            return response.get("data", [])
        raise Exception(f"查找失败: {response.get('error')}")

    def find_by_attr(self, attr: str, value: str) -> List[Dict[str, str]]:
        """按属性查找元素

        Args:
            attr: 属性名
            value: 属性值

        Returns:
            匹配的元素列表
        """
        logger.debug(f"按属性查找: [{attr}={value}]")
        response = self._send_command("find_by_attr", {"attr": attr, "value": value})
        if response.get("success"):
            return response.get("data", [])
        raise Exception(f"查找失败: {response.get('error')}")

    # ========== Cookie / Storage ==========

    def get_cookies(self) -> str:
        """获取所有 Cookie

        Returns:
            Cookie 字符串
        """
        logger.debug("获取所有 Cookie")
        response = self._send_command("get_cookies")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取 Cookie 失败: {response.get('error')}")

    def get_cookie(self, name: str) -> Optional[str]:
        """获取指定 Cookie

        Args:
            name: Cookie 名称

        Returns:
            Cookie 值
        """
        logger.debug(f"获取 Cookie: {name}")
        response = self._send_command("get_cookie", {"name": name})
        if response.get("success"):
            return response.get("data")
        raise Exception(f"获取 Cookie 失败: {response.get('error')}")

    def set_cookie(self, name: str, value: str, days: int = 30, path: str = "/") -> None:
        """设置 Cookie

        Args:
            name: Cookie 名称
            value: Cookie 值
            days: 过期天数
            path: 路径
        """
        logger.debug(f"设置 Cookie: {name}={value}")
        self._send_command("set_cookie", {
            "name": name, "value": value, "days": days, "path": path
        })

    def delete_cookie(self, name: str) -> None:
        """删除 Cookie

        Args:
            name: Cookie 名称
        """
        logger.debug(f"删除 Cookie: {name}")
        self._send_command("delete_cookie", {"name": name})

    def get_local_storage(self, key: str = None) -> Any:
        """获取 localStorage

        Args:
            key: 键名，为 None 时获取所有

        Returns:
            值或字典
        """
        logger.debug(f"获取 localStorage: {key or 'all'}")
        response = self._send_command("get_local_storage", {"key": key})
        if response.get("success"):
            return response.get("data")
        raise Exception(f"获取 localStorage 失败: {response.get('error')}")

    def set_local_storage(self, key: str, value: str) -> None:
        """设置 localStorage

        Args:
            key: 键名
            value: 值
        """
        logger.debug(f"设置 localStorage: {key}={value}")
        self._send_command("set_local_storage", {"key": key, "value": value})

    def delete_local_storage(self, key: str) -> None:
        """删除 localStorage

        Args:
            key: 键名
        """
        logger.debug(f"删除 localStorage: {key}")
        self._send_command("delete_local_storage", {"key": key})

    def get_session_storage(self, key: str = None) -> Any:
        """获取 sessionStorage

        Args:
            key: 键名，为 None 时获取所有

        Returns:
            值或字典
        """
        logger.debug(f"获取 sessionStorage: {key or 'all'}")
        response = self._send_command("get_session_storage", {"key": key})
        if response.get("success"):
            return response.get("data")
        raise Exception(f"获取 sessionStorage 失败: {response.get('error')}")

    def set_session_storage(self, key: str, value: str) -> None:
        """设置 sessionStorage

        Args:
            key: 键名
            value: 值
        """
        logger.debug(f"设置 sessionStorage: {key}={value}")
        self._send_command("set_session_storage", {"key": key, "value": value})

    def delete_session_storage(self, key: str) -> None:
        """删除 sessionStorage

        Args:
            key: 键名
        """
        logger.debug(f"删除 sessionStorage: {key}")
        self._send_command("delete_session_storage", {"key": key})

    # ========== JavaScript ==========

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
    """单个元素类"""

    def __init__(self, tab: Tab, selector: str):
        """初始化元素

        Args:
            tab: 所属标签页
            selector: 选择器
        """
        self._tab = tab
        self._selector = selector

    def _send_command(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送命令"""
        cmd_params = {"selector": self._selector}
        if params:
            cmd_params.update(params)
        return self._tab._send_command(action, cmd_params)

    # ========== 基本操作 ==========

    def click(self) -> None:
        """点击元素"""
        logger.debug(f"点击元素: {self._selector}")
        self._send_command("click")

    def input(self, text: str) -> None:
        """输入文本

        Args:
            text: 要输入的文本
        """
        logger.debug(f"输入文本到 {self._selector}: {text}")
        self._send_command("input", {"text": text})

    def clear(self) -> None:
        """清空输入框"""
        logger.debug(f"清空: {self._selector}")
        self._send_command("clear")

    def focus(self) -> None:
        """聚焦元素"""
        logger.debug(f"聚焦: {self._selector}")
        self._send_command("focus")

    def blur(self) -> None:
        """失去焦点"""
        logger.debug(f"失去焦点: {self._selector}")
        self._send_command("blur")

    def hover(self) -> None:
        """悬停元素"""
        logger.debug(f"悬停: {self._selector}")
        self._send_command("hover")

    # ========== 内容获取 ==========

    @property
    def text(self) -> str:
        """获取元素文本"""
        logger.debug(f"获取元素文本: {self._selector}")
        response = self._send_command("get_text")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取文本失败: {response.get('error')}")

    @property
    def html(self) -> str:
        """获取元素 HTML"""
        logger.debug(f"获取元素 HTML: {self._selector}")
        response = self._send_command("get_html")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取 HTML 失败: {response.get('error')}")

    @property
    def outer_html(self) -> str:
        """获取元素外部 HTML"""
        logger.debug(f"获取元素外部 HTML: {self._selector}")
        response = self._send_command("get_outer_html")
        if response.get("success"):
            return response.get("data", "")
        raise Exception(f"获取外部 HTML 失败: {response.get('error')}")

    def attr(self, name: str) -> Optional[str]:
        """获取元素属性

        Args:
            name: 属性名

        Returns:
            属性值
        """
        logger.debug(f"获取元素属性: {self._selector}.{name}")
        response = self._send_command("get_attr", {"attr": name})
        if response.get("success"):
            return response.get("data")
        raise Exception(f"获取属性失败: {response.get('error')}")

    # ========== 状态检查 ==========

    def exists(self) -> bool:
        """检查元素是否存在

        Returns:
            元素是否存在
        """
        logger.debug(f"检查元素是否存在: {self._selector}")
        response = self._send_command("exists")
        if response.get("success"):
            return response.get("data", False)
        raise Exception(f"检查元素失败: {response.get('error')}")

    def is_visible(self) -> bool:
        """检查元素是否可见

        Returns:
            元素是否可见
        """
        logger.debug(f"检查元素是否可见: {self._selector}")
        response = self._send_command("is_visible")
        if response.get("success"):
            return response.get("data", False)
        raise Exception(f"检查可见性失败: {response.get('error')}")

    # ========== 位置和滚动 ==========

    @property
    def rect(self) -> Dict[str, float]:
        """获取元素位置和大小

        Returns:
            包含 x, y, width, height, top, left, bottom, right 的字典
        """
        logger.debug(f"获取元素位置: {self._selector}")
        response = self._send_command("get_element_rect")
        if response.get("success"):
            return response.get("data", {})
        raise Exception(f"获取位置失败: {response.get('error')}")

    def scroll_to(self) -> None:
        """滚动到元素位置"""
        logger.debug(f"滚动到元素: {self._selector}")
        self._send_command("scroll_to_element")

    # ========== 表单操作 ==========

    def select(self, value: str) -> None:
        """选择下拉框选项

        Args:
            value: 选项值
        """
        logger.debug(f"选择选项: {self._selector} = {value}")
        self._send_command("select_option", {"value": value})

    def check(self) -> None:
        """勾选复选框"""
        logger.debug(f"勾选: {self._selector}")
        self._send_command("check")

    def uncheck(self) -> None:
        """取消勾选复选框"""
        logger.debug(f"取消勾选: {self._selector}")
        self._send_command("uncheck")

    # ========== 键盘操作 ==========

    def press_key(self, key: str, modifiers: List[str] = None) -> None:
        """按下按键

        Args:
            key: 按键名称（如 "Enter", "Tab", "Escape"）
            modifiers: 修饰键列表（如 ["ctrl", "shift"]）
        """
        logger.debug(f"按键: {key} (修饰键: {modifiers or []})")
        self._send_command("press_key", {"key": key, "modifiers": modifiers or []})

    def press_enter(self) -> None:
        """按下回车键"""
        self.press_key("Enter")

    def press_tab(self) -> None:
        """按下 Tab 键"""
        self.press_key("Tab")

    def press_escape(self) -> None:
        """按下 Escape 键"""
        self.press_key("Escape")

    def press_backspace(self) -> None:
        """按下 Backspace 键"""
        self.press_key("Backspace")

    def press_delete(self) -> None:
        """按下 Delete 键"""
        self.press_key("Delete")

    def press_home(self) -> None:
        """按下 Home 键"""
        self.press_key("Home")

    def press_end(self) -> None:
        """按下 End 键"""
        self.press_key("End")

    def press_page_up(self) -> None:
        """按下 Page Up 键"""
        self.press_key("PageUp")

    def press_page_down(self) -> None:
        """按下 Page Down 键"""
        self.press_key("PageDown")

    def press_arrow_up(self) -> None:
        """按下上箭头"""
        self.press_key("ArrowUp")

    def press_arrow_down(self) -> None:
        """按下下箭头"""
        self.press_key("ArrowDown")

    def press_arrow_left(self) -> None:
        """按下左箭头"""
        self.press_key("ArrowLeft")

    def press_arrow_right(self) -> None:
        """按下右箭头"""
        self.press_key("ArrowRight")

    def press_ctrl_a(self) -> None:
        """全选 (Ctrl+A)"""
        self.press_key("a", ["ctrl"])

    def press_ctrl_c(self) -> None:
        """复制 (Ctrl+C)"""
        self.press_key("c", ["ctrl"])

    def press_ctrl_v(self) -> None:
        """粘贴 (Ctrl+V)"""
        self.press_key("v", ["ctrl"])

    def press_ctrl_x(self) -> None:
        """剪切 (Ctrl+X)"""
        self.press_key("x", ["ctrl"])

    def press_ctrl_z(self) -> None:
        """撤销 (Ctrl+Z)"""
        self.press_key("z", ["ctrl"])

    def press_ctrl_s(self) -> None:
        """保存 (Ctrl+S)"""
        self.press_key("s", ["ctrl"])

    # ========== DOM 遍历 ==========

    @property
    def parent(self) -> Optional["Element"]:
        """获取父元素（返回新 Element 需要知道选择器）"""
        logger.debug(f"获取父元素: {self._selector}")
        response = self._send_command("get_element_parent")
        if response.get("success"):
            data = response.get("data")
            if data:
                # 创建一个虚拟元素
                return VirtualElement(self._tab, data)
            return None
        raise Exception(f"获取父元素失败: {response.get('error')}")

    @property
    def children(self) -> List["VirtualElement"]:
        """获取子元素列表"""
        logger.debug(f"获取子元素: {self._selector}")
        response = self._send_command("get_element_children")
        if response.get("success"):
            data = response.get("data", [])
            return [VirtualElement(self._tab, item) for item in data]
        raise Exception(f"获取子元素失败: {response.get('error')}")


class Elements:
    """多个元素类"""

    def __init__(self, tab: Tab, selector: str):
        """初始化

        Args:
            tab: 所属标签页
            selector: 选择器
        """
        self._tab = tab
        self._selector = selector
        self._elements: List[Element] = []

    def _load_elements(self) -> None:
        """加载元素列表"""
        if not self._elements:
            response = self._tab._send_command("get_elements", {"selector": self._selector})
            if response.get("success"):
                count = response.get("data", [])
                # 创建多个 Element 对象
                self._elements = [Element(self._tab, self._selector) for _ in range(len(count))]

    def __len__(self) -> int:
        """获取元素数量"""
        self._load_elements()
        return len(self._elements)

    def __getitem__(self, index: int) -> Element:
        """获取指定索引的元素"""
        self._load_elements()
        return self._elements[index]

    def __iter__(self):
        """迭代元素"""
        self._load_elements()
        return iter(self._elements)

    @property
    def count(self) -> int:
        """获取元素数量"""
        self._load_elements()
        return len(self._elements)

    def first(self) -> Element:
        """获取第一个元素"""
        self._load_elements()
        if self._elements:
            return self._elements[0]
        raise Exception(f"没有找到元素: {self._selector}")

    def last(self) -> Element:
        """获取最后一个元素"""
        self._load_elements()
        if self._elements:
            return self._elements[-1]
        raise Exception(f"没有找到元素: {self._selector}")


class VirtualElement:
    """虚拟元素类（用于 DOM 遍历返回的结果）"""

    def __init__(self, tab: Tab, data: Dict[str, Any]):
        """初始化

        Args:
            tab: 所属标签页
            data: 元素数据
        """
        self._tab = tab
        self._data = data

    @property
    def tag_name(self) -> str:
        """获取标签名"""
        return self._data.get("tagName", "")

    @property
    def text(self) -> str:
        """获取文本内容"""
        return self._data.get("text", "")

    @property
    def html(self) -> str:
        """获取 HTML"""
        return self._data.get("html", "")

    def __repr__(self) -> str:
        return f"<VirtualElement tag={self.tag_name} text={self.text[:30]}>"
