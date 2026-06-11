"""
BrowserProxy 自定义异常类
"""


class BrowserProxyError(Exception):
    """BrowserProxy 基础异常类"""
    pass


class ConnectionError(BrowserProxyError):
    """连接错误"""
    pass


class ConnectionTimeoutError(ConnectionError):
    """连接超时"""
    pass


class NotConnectedError(ConnectionError):
    """未连接"""
    pass


class ExtensionError(BrowserProxyError):
    """Chrome 扩展错误"""
    pass


class ExtensionNotConnectedError(ExtensionError):
    """Chrome 扩展未连接"""
    pass


class TabError(BrowserProxyError):
    """标签页操作错误"""
    pass


class TabNotFoundError(TabError):
    """标签页不存在"""
    pass


class ElementError(BrowserProxyError):
    """元素操作错误"""
    pass


class ElementNotFoundError(ElementError):
    """元素不存在"""
    pass


class ElementNotVisibleError(ElementError):
    """元素不可见"""
    pass


class ElementNotInteractableError(ElementError):
    """元素不可交互（被遮挡、禁用等）"""
    pass


class WaitTimeoutError(BrowserProxyError):
    """等待超时"""
    pass


class WaitForElementTimeoutError(WaitTimeoutError):
    """等待元素超时"""
    pass


class WaitForUrlTimeoutError(WaitTimeoutError):
    """等待 URL 变化超时"""
    pass


class JavaScriptError(BrowserProxyError):
    """JavaScript 执行错误"""
    pass


class NavigationError(BrowserProxyError):
    """页面导航错误"""
    pass


class IframeError(BrowserProxyError):
    """iframe 操作错误"""
    pass


class IframeNotFoundError(IframeError):
    """iframe 不存在"""
    pass


class CookieError(BrowserProxyError):
    """Cookie 操作错误"""
    pass


class DownloadError(BrowserProxyError):
    """下载错误"""
    pass


class ScreenshotError(BrowserProxyError):
    """截图错误"""
    pass
