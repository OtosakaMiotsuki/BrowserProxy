"""
BrowserProxy 测试程序
启动 WebSocket 服务端，等待 Chrome 扩展连接
"""

import sys
import time
from loguru import logger
from browserproxy import Browser

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def main():
    """主函数"""
    logger.info("BrowserProxy 测试程序启动")

    # 创建浏览器连接（会启动 WebSocket 服务端）
    browser = Browser(port=8765)

    try:
        # 启动服务并等待扩展连接
        logger.info("正在启动 WebSocket 服务端...")
        logger.info("请在 Chrome 扩展中输入端口号 8765 并点击连接")
        browser.connect(timeout=30)

        # 获取所有标签页
        logger.info("获取标签页列表...")
        tabs = browser.get_tabs()
        logger.info(f"找到 {len(tabs)} 个标签页")

        # 打印每个标签页的详细信息
        print("\n" + "=" * 60)
        print("标签页列表")
        print("=" * 60)

        for i, tab in enumerate(tabs, 1):
            print(f"\n[{i}] 标签页 ID: {tab.tab_id}")
            print(f"    标题: {tab.title}")
            print(f"    URL: {tab.url}")

        print("\n" + "=" * 60)

        # 尝试匹配百度标签页
        logger.info("尝试匹配百度标签页...")
        baidu_tab = browser.match(url_contains="baidu.com", title_contains="百度")

        if baidu_tab:
            logger.info(f"找到百度标签页: {baidu_tab.title} (ID: {baidu_tab.tab_id})")
        else:
            logger.info("未找到百度标签页")

    except TimeoutError as e:
        logger.error(f"等待超时: {e}")
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        browser.disconnect()
        logger.info("程序结束")


if __name__ == "__main__":
    main()
