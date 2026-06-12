"""
百度搜索示例程序
演示如何使用 BrowserProxy 自动化操作浏览器
"""

import sys
import time
from loguru import logger
from browserproxy import Browser, enable_logging

# 启用框架日志
enable_logging(level="INFO")


def main():
    """主函数"""
    logger.info("百度搜索助手启动")

    # 创建浏览器连接
    browser = Browser()

    try:
        # 连接到 Chrome 扩展
        logger.info("正在连接到浏览器...")
        browser.connect()
        logger.info("连接成功！")

        # 获取所有标签页
        logger.info("获取标签页列表...")
        tabs = browser.get_tabs()
        logger.info(f"找到 {len(tabs)} 个标签页")

        # 匹配百度标签页
        logger.info("查找百度标签页...")
        tab = browser.match(url_contains="baidu.com", title_contains="百度")

        if tab is None:
            logger.error("未找到百度标签页，请先在浏览器中打开百度")
            return

        logger.info(f"找到百度标签页: {tab.title} (ID: {tab.tab_id})")

        # 注入 Content Script
        logger.info("注入 Content Script...")
        browser._ws_client.send_and_receive({
            "action": "inject_content_script",
            "tab_id": tab.tab_id
        })

        # 等待注入完成
        time.sleep(0.5)

        # 输入搜索关键词
        search_keyword = "BrowserProxy 自动化"
        logger.info(f"输入搜索关键词: {search_keyword}")

        # 查找搜索框并输入
        search_input = tab.ele("#kw")  # 百度搜索框的 ID
        search_input.input(search_keyword)

        # 点击搜索按钮
        logger.info("点击搜索按钮...")
        search_button = tab.ele("#su")  # 百度搜索按钮的 ID
        search_button.click()

        # 等待搜索结果加载
        logger.info("等待搜索结果加载...")
        time.sleep(2)

        # 获取搜索结果标题
        logger.info("获取搜索结果...")
        result_title = tab.ele("h3").text
        logger.info(f"第一个搜索结果: {result_title}")

        # 执行 JS 获取更多信息
        logger.info("获取页面信息...")
        page_title = tab.run_js("return document.title")
        logger.info(f"页面标题: {page_title}")

        logger.info("搜索完成！")

    except ConnectionError as e:
        logger.error(f"连接失败: {e}")
        logger.info("请确保 Chrome 扩展已安装并启动 WebSocket 服务")
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        browser.disconnect()
        logger.info("程序结束")


if __name__ == "__main__":
    main()
