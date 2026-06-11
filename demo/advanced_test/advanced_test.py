"""
高级功能测试
测试：动态加载、表格提取、悬停菜单、模态框、计数器、滚动加载、多步骤向导、标签切换
"""

import sys
import time
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from browserproxy import Browser

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def main():
    html_path = Path(__file__).parent / "advanced.html"
    html_url = html_path.as_uri()

    browser = Browser(port=8765)

    try:
        logger.info("启动服务，等待扩展连接...")
        browser.connect(timeout=30)

        tab = browser.new_tab(html_url)
        time.sleep(1)

        browser._ws_server.send_and_receive({
            "action": "inject_content_script",
            "tab_id": tab.tab_id
        })

        tab_id = tab.tab_id

        # ========== 场景 1: 动态加载 ==========
        logger.info("\n[场景 1] 动态加载")
        tab.ele("button:contains('点击加载')").click() if tab.ele("button:contains('点击加载')").exists() else None
        # 直接用选择器
        tab.scroll_to_top()
        tab.eles("button")[0].click()
        time.sleep(3)
        text = tab.ele("#dynamicText").text
        logger.info(f"  结果: {text}")
        logger.info(f"  ✅ 通过" if "加载完成" in text else "  ❌ 失败")

        # ========== 场景 2: 表格数据提取 ==========
        logger.info("\n[场景 2] 表格数据提取")
        rows = tab.eles("#dataTable tbody tr")
        logger.info(f"  表格共 {len(rows)} 行")

        for row in rows:
            name = row.ele("td:nth-child(2)").text
            dept = row.ele("td:nth-child(3)").text
            salary = row.ele("td:nth-child(4)").text
            logger.info(f"  {name} | {dept} | {salary}")

        # 高亮技术部
        tab.eles("button")[1].click()
        time.sleep(0.5)
        result = tab.ele("#tableResult").text
        logger.info(f"  {result}")
        logger.info(f"  ✅ 通过" if "2" in result else "  ❌ 失败")

        # ========== 场景 3: 悬停下拉菜单 ==========
        logger.info("\n[场景 3] 悬停下拉菜单")
        tab.hover(".dropdown-btn")
        time.sleep(0.5)
        tab.ele(".dropdown-menu a:nth-child(3)").click()  # 点击"删除"
        time.sleep(0.5)
        result = tab.ele("#actionResult").text
        logger.info(f"  {result}")
        logger.info(f"  ✅ 通过" if "删除" in result else "  ❌ 失败")

        # ========== 场景 4: 模态框 ==========
        logger.info("\n[场景 4] 模态框交互")
        tab.eles("button")[3].click()  # 打开对话框
        time.sleep(0.5)
        tab.ele("#modalInput").input("ABC123")
        tab.ele("button:contains('确认')").click()
        time.sleep(0.5)
        result = tab.ele("#modalResult").text
        logger.info(f"  {result}")
        logger.info(f"  ✅ 通过" if "ABC123" in result else "  ❌ 失败")

        # ========== 场景 5: 计数器 ==========
        logger.info("\n[场景 5] 计数器")
        tab.ele("button:contains('+')").click()
        tab.ele("button:contains('+')").click()
        tab.ele("button:contains('+')").click()
        tab.ele("button:contains('-')").click()
        time.sleep(0.3)
        count = tab.ele("#count").text
        logger.info(f"  计数器值: {count}")
        logger.info(f"  ✅ 通过" if count == "2" else f"  ❌ 失败 (期望 2，实际 {count})")

        # ========== 场景 6: 动态列表 ==========
        logger.info("\n[场景 6] 动态列表（滚动加载）")
        items_before = len(tab.eles(".dynamic-list .item"))
        tab.ele("button:contains('加载更多')").click()
        time.sleep(0.5)
        items_after = len(tab.eles(".dynamic-list .item"))
        logger.info(f"  加载前: {items_before} 项, 加载后: {items_after} 项")
        logger.info(f"  ✅ 通过" if items_after > items_before else "  ❌ 失败")

        # ========== 场景 7: 多步骤向导 ==========
        logger.info("\n[场景 7] 多步骤向导")
        tab.ele("#category").select("product")
        tab.eles("button:contains('下一步')")[0].click()
        time.sleep(0.3)
        tab.ele("#detail").input("这是一个测试产品")
        tab.eles("button:contains('下一步')")[1].click()
        time.sleep(0.3)
        summary = tab.ele("#summary").text
        logger.info(f"  {summary}")
        tab.ele("button:contains('提交')").click()
        time.sleep(0.3)
        result = tab.ele("#wizardResult").text
        logger.info(f"  {result}")
        logger.info(f"  ✅ 通过" if "product" in result else "  ❌ 失败")

        # ========== 场景 8: 标签切换 ==========
        logger.info("\n[场景 8] 页面内标签切换")
        tab.eles("button:contains('标签 B')")[0].click()
        time.sleep(0.3)
        content = tab.ele("#tabContent2").text
        logger.info(f"  标签 B 内容: {content}")
        logger.info(f"  ✅ 通过" if "标签 B" in content else "  ❌ 失败")

        # 关闭标签页
        logger.info("\n测试完成，关闭标签页...")
        browser.close_tab(tab_id)

    except Exception as e:
        logger.error(f"错误: {e}")
    finally:
        browser.disconnect()


if __name__ == "__main__":
    main()
