"""
下载 miotsuki.cn 博客内容
打开博客，点击第一篇文章，下载内容到本地
"""

import sys
import time
from loguru import logger
from browserproxy import Browser, enable_logging

# 启用框架日志
enable_logging(level="INFO")


def main():
    """主函数"""
    logger.info("开始下载 miotsuki.cn 博客内容")

    # 创建浏览器连接
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

        # 查找 miotsuki.cn 标签页
        logger.info("查找 miotsuki.cn 标签页...")
        blog_tab = browser.match(url_contains="miotsuki.cn")

        if blog_tab:
            logger.info(f"找到博客标签页: {blog_tab.title} (ID: {blog_tab.tab_id})")
        else:
            # 如果没有打开，创建新标签页
            logger.info("未找到博客标签页，正在打开...")
            blog_tab = browser.match(url_contains="chrome://newtab")

            if not blog_tab:
                logger.error("无法创建新标签页")
                return

            # 导航到博客
            blog_tab.get("https://miotsuki.cn/")
            time.sleep(2)

            # 重新获取标签页列表并找到博客
            browser.get_tabs()
            blog_tab = browser.match(url_contains="miotsuki.cn")

            if not blog_tab:
                logger.error("无法打开博客页面")
                return

            logger.info(f"已打开博客: {blog_tab.title}")

        # 注入 Content Script
        logger.info("注入 Content Script...")
        browser._ws_server.send_and_receive({
            "action": "inject_content_script",
            "tab_id": blog_tab.tab_id
        })
        time.sleep(0.5)

        # 点击第一篇博客文章
        logger.info("点击第一篇博客文章...")

        # 尝试多种选择器来找到文章链接
        selectors = [
            "article a",           # 文章链接
            ".post-title a",       # 标题链接
            ".entry-title a",      # 入口标题链接
            "h2 a",                # h2 标签内的链接
            "h3 a",                # h3 标签内的链接
            ".content a",          # 内容区域的链接
            "a[href*='/post/']",   # 包含 /post/ 的链接
            "a[href*='/posts/']",  # 包含 /posts/ 的链接
            "a[href*='/blog/']",   # 包含 /blog/ 的链接
        ]

        clicked = False
        for selector in selectors:
            try:
                element = blog_tab.ele(selector)
                if element.exists():
                    # 获取链接文本和 URL
                    link_text = element.text
                    link_url = element.attr("href")

                    if link_text and link_url:
                        logger.info(f"找到文章: {link_text}")
                        logger.info(f"链接: {link_url}")
                        element.click()
                        clicked = True
                        break
            except Exception:
                continue

        if not clicked:
            # 如果找不到选择器，尝试用 JS 获取第一个文章链接
            logger.info("尝试用 JavaScript 查找文章链接...")
            try:
                result = blog_tab.run_js("""
                    // 查找所有文章链接
                    const links = document.querySelectorAll('a');
                    const articleLinks = [];
                    for (const link of links) {
                        const href = link.href;
                        const text = link.textContent.trim();
                        // 过滤出可能是文章的链接
                        if (href && text && text.length > 5 &&
                            (href.includes('/post/') || href.includes('/posts/') ||
                             href.includes('/blog/') || href.includes('/article/'))) {
                            articleLinks.push({href, text});
                        }
                    }
                    return articleLinks;
                """)

                if result and len(result) > 0:
                    first_article = result[0]
                    logger.info(f"找到文章: {first_article['text']}")
                    logger.info(f"链接: {first_article['href']}")

                    # 导航到文章页面
                    blog_tab.get(first_article['href'])
                    clicked = True
                else:
                    logger.warning("未找到文章链接")
            except Exception as e:
                logger.error(f"JavaScript 执行失败: {e}")

        if not clicked:
            logger.error("无法点击文章")
            return

        # 等待页面加载
        logger.info("等待页面加载...")
        time.sleep(3)

        # 获取文章内容
        logger.info("获取文章内容...")

        # 尝试获取文章标题
        title = None
        title_selectors = [
            "h1",
            ".post-title",
            ".entry-title",
            "article h1",
            ".content h1",
        ]

        for selector in title_selectors:
            try:
                element = blog_tab.ele(selector)
                if element.exists():
                    title = element.text
                    if title:
                        logger.info(f"文章标题: {title}")
                        break
            except Exception:
                continue

        if not title:
            title = "untitled"

        # 尝试获取文章内容
        content = None
        content_selectors = [
            "article",
            ".post-content",
            ".entry-content",
            ".content",
            "main",
            "#content",
        ]

        for selector in content_selectors:
            try:
                element = blog_tab.ele(selector)
                if element.exists():
                    content = element.text
                    if content and len(content) > 100:  # 确保内容足够长
                        logger.info(f"获取到内容: {len(content)} 字符")
                        break
            except Exception:
                continue

        if not content:
            # 尝试用 JS 获取内容
            logger.info("尝试用 JavaScript 获取内容...")
            try:
                content = blog_tab.run_js("""
                    // 获取文章内容
                    const article = document.querySelector('article') ||
                                   document.querySelector('.post-content') ||
                                   document.querySelector('.entry-content') ||
                                   document.querySelector('.content') ||
                                   document.querySelector('main');
                    if (article) {
                        return article.innerText;
                    }
                    return null;
                """)
            except Exception as e:
                logger.error(f"JavaScript 执行失败: {e}")

        if not content:
            logger.error("无法获取文章内容")
            return

        # 保存到本地文件
        logger.info("保存到本地文件...")

        # 清理文件名
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50]  # 限制文件名长度

        filename = f"blog_{safe_title}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"标题: {title}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content)

        logger.info(f"已保存到: {filename}")
        logger.info("下载完成！")

    except TimeoutError as e:
        logger.error(f"等待超时: {e}")
    except Exception as e:
        logger.error(f"发生错误: {e}")
    finally:
        browser.disconnect()
        logger.info("程序结束")


if __name__ == "__main__":
    main()
