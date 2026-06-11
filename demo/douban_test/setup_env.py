"""
创建独立的测试环境
运行此脚本会自动：
1. 创建虚拟环境
2. 安装 BrowserProxy
3. 复制扩展到测试目录
4. 显示使用说明
"""

import subprocess
import sys
import shutil
from pathlib import Path
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("BrowserProxy 独立测试环境创建工具")
    logger.info("=" * 60)

    # 获取路径
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    dist_dir = project_root / "dist"
    extension_source = project_root / "extension"

    # 检查打包文件
    whl_files = list(dist_dir.glob("browserproxy-*.whl"))
    if not whl_files:
        logger.error("❌ 未找到打包文件，请先运行 uv build")
        return

    whl_file = whl_files[0]
    logger.info(f"找到打包文件: {whl_file.name}")

    # 创建虚拟环境
    venv_dir = current_dir / "venv"
    logger.info(f"\n步骤 1: 创建虚拟环境: {venv_dir}")

    if venv_dir.exists():
        logger.info("  虚拟环境已存在，跳过创建")
    else:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        logger.info("✅ 虚拟环境创建成功")

    # 激活虚拟环境并安装
    if sys.platform == "win32":
        python_path = venv_dir / "Scripts" / "python.exe"
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        python_path = venv_dir / "bin" / "python"
        pip_path = venv_dir / "bin" / "pip"

    logger.info(f"\n步骤 2: 安装 BrowserProxy")
    subprocess.run([str(pip_path), "install", str(whl_file)], check=True)
    logger.info("✅ BrowserProxy 安装成功")

    # 复制扩展
    extension_target = current_dir / "extension"
    logger.info(f"\n步骤 3: 复制 Chrome 扩展")

    if extension_target.exists():
        shutil.rmtree(extension_target)

    shutil.copytree(extension_source, extension_target)
    logger.info(f"✅ 扩展已复制到: {extension_target}")

    # 显示使用说明
    logger.info("\n" + "=" * 60)
    logger.info("环境创建完成！")
    logger.info("=" * 60)

    logger.info("\n使用步骤:")
    logger.info("1. 打开 Chrome 浏览器，访问 chrome://extensions/")
    logger.info("2. 开启右上角的'开发者模式'")
    logger.info("3. 点击'加载已解压的扩展程序'")
    logger.info(f"4. 选择目录: {extension_target}")
    logger.info("")
    logger.info("5. 激活虚拟环境:")
    if sys.platform == "win32":
        logger.info(f"   {venv_dir}\\Scripts\\activate")
    else:
        logger.info(f"   source {venv_dir}/bin/activate")
    logger.info("")
    logger.info("6. 运行测试:")
    logger.info("   python douban_test.py")

    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    main()
