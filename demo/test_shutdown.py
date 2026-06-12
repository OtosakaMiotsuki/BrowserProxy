"""
测试 WebSocket 服务器关闭是否干净
"""

import sys
import time
from loguru import logger
from browserproxy import Browser, enable_logging

# 启用框架日志
enable_logging(level="INFO")


def main():
    """测试服务器关闭"""
    logger.info("测试 WebSocket 服务器关闭")

    browser = Browser(port=8766)

    try:
        # 启动服务器
        logger.info("启动服务器...")
        browser.connect(timeout=5)
        logger.info("服务器已启动")

        # 等待一下
        time.sleep(1)

        # 获取标签页（如果有扩展连接）
        if browser.connected:
            tabs = browser.get_tabs()
            logger.info(f"获取到 {len(tabs)} 个标签页")
        else:
            logger.info("没有扩展连接，跳过获取标签页")

    except TimeoutError:
        logger.info("等待扩展连接超时，这是正常的")
    except Exception as e:
        logger.error(f"错误: {e}")
    finally:
        # 关闭服务器
        logger.info("正在关闭服务器...")
        browser.disconnect()
        logger.info("服务器已关闭")


if __name__ == "__main__":
    main()
