"""
BrowserProxy - 浏览器自动化工具
通过 Chrome 扩展 + WebSocket 实现对已打开浏览器的操控
"""

from .browser import Browser
from .tab import Tab
from .match import TabMatcher

__version__ = "0.1.0"
__all__ = ["Browser", "Tab", "TabMatcher"]
