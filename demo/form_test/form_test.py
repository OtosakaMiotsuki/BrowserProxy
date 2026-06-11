"""
表单自动填写测试
打开本地表单页面，自动填写所有字段，验证结果
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
    # 获取表单 HTML 的绝对路径
    form_path = Path(__file__).parent / "form.html"
    form_url = form_path.as_uri()

    browser = Browser(port=8765)

    try:
        logger.info("启动服务，等待扩展连接...")
        browser.connect(timeout=30)

        # 打开本地表单页面
        logger.info(f"打开表单页面: {form_url}")
        tab = browser.new_tab(form_url)
        time.sleep(1)

        # 注入 Content Script
        browser._ws_server.send_and_receive({
            "action": "inject_content_script",
            "tab_id": tab.tab_id
        })

        tab_id = tab.tab_id

        # 开始填写表单
        logger.info("\n开始填写表单...")

        # 1. 用户名
        logger.info("填写用户名...")
        tab.ele("#username").input("Miotsuki")
        time.sleep(0.3)

        # 2. 邮箱
        logger.info("填写邮箱...")
        tab.ele("#email").input("test@browserproxy.com")
        time.sleep(0.3)

        # 3. 密码
        logger.info("填写密码...")
        tab.ele("#password").input("password123")
        time.sleep(0.3)

        # 4. 年龄
        logger.info("填写年龄...")
        tab.ele("#age").input("25")
        time.sleep(0.3)

        # 5. 性别（单选）
        logger.info("选择性别...")
        tab.ele("input[value='male']").click()
        time.sleep(0.3)

        # 6. 城市（下拉框）
        logger.info("选择城市...")
        tab.ele("#city").select("beijing")
        time.sleep(0.3)

        # 7. 兴趣爱好（复选框）
        logger.info("选择兴趣爱好...")
        tab.ele("input[value='coding']").check()
        time.sleep(0.1)
        tab.ele("input[value='gaming']").check()
        time.sleep(0.1)
        tab.ele("input[value='travel']").check()
        time.sleep(0.3)

        # 8. 个人简介
        logger.info("填写个人简介...")
        tab.ele("#bio").input("我是一名开发者，喜欢用自动化工具提高效率。")
        time.sleep(0.3)

        # 9. 同意条款
        logger.info("勾选同意条款...")
        tab.ele("#agree").check()
        time.sleep(0.5)

        logger.info("\n表单填写完成！点击提交按钮...")

        # 点击提交按钮
        tab.ele("#submitBtn").click()
        time.sleep(1)

        # 读取提交结果
        result_text = tab.ele("#formData").text
        logger.info(f"\n提交结果:\n{result_text}")

        # 关闭标签页
        time.sleep(2)
        browser.close_tab(tab_id)
        logger.info("标签页已关闭")

    except Exception as e:
        logger.error(f"错误: {e}")
    finally:
        browser.disconnect()


if __name__ == "__main__":
    main()
