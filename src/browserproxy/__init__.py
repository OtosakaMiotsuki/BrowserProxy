"""
BrowserProxy - 浏览器自动化工具
通过 Chrome 扩展 + WebSocket 实现对已打开浏览器的操控
"""

import shutil
from pathlib import Path
from loguru import logger
from .browser import Browser
from .tab import Tab, Element, Elements, VirtualElement
from .match import TabMatcher
from .exceptions import (
    BrowserProxyError,
    ConnectionError as BpConnectionError,
    ConnectionTimeoutError,
    NotConnectedError,
    ExtensionError,
    ExtensionNotConnectedError,
    TabError,
    TabNotFoundError,
    ElementError,
    ElementNotFoundError,
    ElementNotVisibleError,
    ElementNotInteractableError,
    WaitTimeoutError,
    WaitForElementTimeoutError,
    WaitForUrlTimeoutError,
    JavaScriptError,
    NavigationError,
    IframeError,
    IframeNotFoundError,
    CookieError,
    DownloadError,
    ScreenshotError,
)

__version__ = "0.2.0"
__author__ = "Miotsuki"
__email__ = "yuhao_engineer@163.com"
__all__ = [
    "Browser", "Tab", "Element", "Elements", "TabMatcher",
    "install_extension", "get_extension_path", "enable_logging",
    "BrowserProxyError",
    "BpConnectionError", "ConnectionTimeoutError", "NotConnectedError",
    "ExtensionError", "ExtensionNotConnectedError",
    "TabError", "TabNotFoundError",
    "ElementError", "ElementNotFoundError",
    "ElementNotVisibleError", "ElementNotInteractableError",
    "WaitTimeoutError", "WaitForElementTimeoutError", "WaitForUrlTimeoutError",
    "JavaScriptError", "NavigationError",
    "IframeError", "IframeNotFoundError",
    "CookieError", "DownloadError", "ScreenshotError",
]

# 默认静默：移除 loguru 的 stderr handler，框架不主动输出日志
logger.remove()


def install_extension(target_dir: str = None) -> str:
    """安装 Chrome 扩展到指定目录

    Args:
        target_dir: 目标目录，默认为当前目录下的 browserproxy_extension

    Returns:
        扩展目录路径
    """
    # 获取扩展源目录
    package_dir = Path(__file__).parent
    extension_source = package_dir / "extension"

    if not extension_source.exists():
        raise FileNotFoundError(f"扩展目录不存在: {extension_source}")

    # 确定目标目录
    if target_dir is None:
        target_dir = Path.cwd() / "browserproxy_extension"
    else:
        target_dir = Path(target_dir)

    # 复制扩展
    if target_dir.exists():
        shutil.rmtree(target_dir)

    shutil.copytree(extension_source, target_dir)

    print(f"✅ Chrome 扩展已安装到: {target_dir}")
    print("")
    print("安装步骤:")
    print("1. 打开 Chrome 浏览器，访问 chrome://extensions/")
    print("2. 开启右上角的'开发者模式'")
    print("3. 点击'加载已解压的扩展程序'")
    print(f"4. 选择目录: {target_dir}")
    print("")
    print("或者将目录打包成 .zip 文件后拖拽安装")

    return str(target_dir)


def get_extension_path() -> Path:
    """获取扩展源目录路径

    Returns:
        扩展目录路径
    """
    return Path(__file__).parent / "extension"


def enable_logging(level: str = "INFO", fmt: str = None) -> None:
    """启用框架日志输出（默认静默）

    Args:
        level: 日志级别，DEBUG / INFO / WARNING / ERROR
        fmt: 自定义格式，默认: {time:HH:mm:ss} | {level} | {message}
    """
    if fmt is None:
        fmt = "{time:HH:mm:ss} | {level} | {message}"
    logger.add(lambda m: print(m, end=""), level=level, format=fmt)
