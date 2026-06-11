"""
豆瓣 Top250 测试
测试：滚动、翻页、获取电影信息、关闭标签页
"""

import sys
import time
import json
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from browserproxy import Browser

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def main():
    browser = Browser(port=8765)

    try:
        logger.info("启动服务，等待扩展连接...")
        browser.connect(timeout=30)

        # 找到或打开豆瓣页面
        tab = browser.match(url_contains="douban.com")
        if not tab:
            tab = browser.new_tab("https://movie.douban.com/top250")
            time.sleep(2)
            browser.get_tabs()
            tab = browser.match(url_contains="douban.com")

        # 注入 Content Script
        browser._ws_server.send_and_receive({
            "action": "inject_content_script",
            "tab_id": tab.tab_id
        })

        all_movies = []
        tab_id = tab.tab_id

        # 获取 3 页数据
        for page in range(3):
            logger.info(f"\n第 {page+1} 页")

            # 滚动到底部
            tab.scroll_to_bottom()
            time.sleep(1)

            # 获取电影信息
            items = tab.eles(".item")
            logger.info(f"找到 {len(items)} 部电影")

            for item in items:
                try:
                    title = item.ele(".hd a span").text
                    rating = item.ele(".rating_num").text
                    votes = item.ele(".star span:last-child").text

                    all_movies.append({
                        "title": title,
                        "rating": rating,
                        "votes": votes
                    })
                except Exception:
                    continue

            # 每页获取完就保存一次（防止中途出错丢数据）
            output = Path(__file__).parent / "movies.json"
            with open(output, "w", encoding="utf-8") as f:
                json.dump(all_movies, f, ensure_ascii=False, indent=2)

            logger.info(f"已保存 {len(all_movies)} 部电影")

            # 点击下一页
            if page < 2:
                next_btn = tab.ele(".next a")
                if next_btn.exists():
                    next_btn.click()
                    time.sleep(2)
                else:
                    logger.info("没有下一页了")
                    break

        logger.info(f"\n完成！共 {len(all_movies)} 部电影")

        # 关闭标签页
        logger.info("关闭豆瓣标签页...")
        browser.close_tab(tab_id)
        logger.info("标签页已关闭")

    except Exception as e:
        logger.error(f"错误: {e}")
    finally:
        browser.disconnect()


if __name__ == "__main__":
    main()
