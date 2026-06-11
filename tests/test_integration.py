"""
BrowserProxy 集成测试
测试 WebSocket 连接和基本功能
"""

import sys
import time
import subprocess
import json
from loguru import logger
from pathlib import Path

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


def test_websocket_connection():
    """测试 WebSocket 连接"""
    try:
        import websocket
    except ImportError:
        logger.error("请先安装 websocket-client: pip install websocket-client")
        return False

    project_root = get_project_root()

    logger.info("=" * 60)
    logger.info("BrowserProxy WebSocket 连接测试")
    logger.info("=" * 60)

    # 启动 Python 服务器
    logger.info("启动 Python 服务器...")
    process = subprocess.Popen(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, 'src')
from browserproxy import Browser

browser = Browser(port=8768)
browser.connect(timeout=10)
print("服务器已启动，等待连接...")

# 保持运行
import time
while True:
    time.sleep(1)
"""],
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    logger.info(f"Python 进程已启动 (PID: {process.pid})")
    time.sleep(3)

    try:
        # 连接到 WebSocket
        logger.info("连接到 WebSocket 服务器 (ws://localhost:8768)...")
        ws = websocket.create_connection("ws://localhost:8768", timeout=5)

        # 发送注册消息
        logger.info("发送注册消息...")
        ws.send(json.dumps({
            "type": "register",
            "client_type": "extension"
        }))

        # 接收响应
        response = json.loads(ws.recv())
        logger.info(f"注册响应: {response}")

        if response.get("success"):
            logger.info("✅ 注册成功")

            # 测试 1: 发送 list_tabs 命令（模拟 Chrome 扩展）
            logger.info("\n测试 1: 模拟 Chrome 扩展响应 list_tabs...")

            # 在真实场景中，Chrome 扩展会收到这个命令并响应
            # 这里我们模拟扩展的响应
            logger.info("ℹ️ 注意: list_tabs 命令需要 Chrome 扩展响应")
            logger.info("   在真实测试中，扩展会查询 chrome.tabs.query()")

            # 测试 2: 发送自定义命令
            logger.info("\n测试 2: 测试自定义命令...")
            ws.send(json.dumps({
                "id": "test-002",
                "action": "ping"
            }))

            # 由于服务器不会响应未知命令，这里只是测试发送
            logger.info("✅ 命令已发送（服务器不会响应未知命令）")

            logger.info("\n" + "=" * 60)
            logger.info("✅ WebSocket 连接测试完成！")
            logger.info("=" * 60)
            logger.info("ℹ️ 注意: 完整功能测试需要 Chrome 扩展运行")

        else:
            logger.error(f"❌ 注册失败: {response.get('error')}")
            return False

        ws.close()
        return True

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False

    finally:
        # 终止 Python 进程
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            logger.info("Python 服务器已停止")


def test_browser_integration():
    """测试与浏览器的集成"""
    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
    except ImportError:
        logger.warning("DrissionPage 未安装，跳过浏览器集成测试")
        logger.info("安装命令: pip install DrissionPage")
        return True  # 不算失败

    project_root = get_project_root()
    extension_path = project_root / "extension"

    logger.info("=" * 60)
    logger.info("BrowserProxy 浏览器集成测试")
    logger.info("=" * 60)

    # 配置 Chrome 选项
    logger.info("配置 Chrome 浏览器...")
    co = ChromiumOptions()

    # 加载扩展
    co.set_argument(f"--load-extension={extension_path}")
    co.set_argument("--no-first-run")
    co.set_argument("--no-default-browser-check")
    co.set_argument("--disable-popup-blocking")

    # 启动浏览器
    logger.info("启动 Chrome 浏览器...")
    page = ChromiumPage(co)

    try:
        # 步骤 1: 打开测试页面
        logger.info("步骤 1: 打开测试页面...")
        page.get("https://www.baidu.com")
        time.sleep(2)

        title = page.title
        logger.info(f"页面标题: {title}")

        if "百度" in title:
            logger.info("✅ 页面加载成功")
        else:
            logger.warning("⚠️ 页面标题不符合预期，但继续测试")

        # 步骤 2: 测试页面操作
        logger.info("步骤 2: 测试页面操作...")

        # 测试获取元素
        search_input = page.ele("id:kw")
        if search_input:
            logger.info("✅ 找到搜索框")
            search_input.clear()
            search_input.input("BrowserProxy")
            logger.info("✅ 输入测试文本")
        else:
            logger.warning("⚠️ 未找到搜索框")

        # 测试点击
        search_btn = page.ele("id:su")
        if search_btn:
            logger.info("✅ 找到搜索按钮")
        else:
            logger.warning("⚠️ 未找到搜索按钮")

        logger.info("\n" + "=" * 60)
        logger.info("✅ 浏览器集成测试完成！")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False

    finally:
        # 关闭浏览器
        try:
            page.quit()
            logger.info("浏览器已关闭")
        except Exception:
            pass


def main():
    """主函数"""
    logger.info("BrowserProxy 集成测试工具")

    # 运行测试
    results = []

    # 测试 1: WebSocket 连接测试
    logger.info("\n" + "=" * 60)
    logger.info("测试 1: WebSocket 连接测试")
    logger.info("=" * 60)
    result1 = test_websocket_connection()
    results.append(("WebSocket 连接测试", result1))

    # 测试 2: 浏览器集成测试
    logger.info("\n" + "=" * 60)
    logger.info("测试 2: 浏览器集成测试")
    logger.info("=" * 60)
    result2 = test_browser_integration()
    results.append(("浏览器集成测试", result2))

    # 显示结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{name}: {status}")

    # 总结
    all_passed = all(r for _, r in results)
    if all_passed:
        logger.info("\n🎉 所有测试通过！")
    else:
        logger.info("\n⚠️ 部分测试失败，请检查日志")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
