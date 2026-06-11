"""创建独立测试环境"""

import subprocess
import sys
import shutil
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def main():
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    dist_dir = project_root / "dist"

    whl_files = list(dist_dir.glob("browserproxy-*.whl"))
    if not whl_files:
        logger.error("未找到打包文件，请先运行 uv build")
        return

    venv_dir = current_dir / "venv"
    if not venv_dir.exists():
        logger.info("创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    pip_path = venv_dir / "Scripts" / "pip.exe" if sys.platform == "win32" else venv_dir / "bin" / "pip"
    logger.info("安装 BrowserProxy...")
    subprocess.run([str(pip_path), "install", str(whl_files[0])], check=True)

    extension_target = current_dir / "extension"
    if extension_target.exists():
        shutil.rmtree(extension_target)
    shutil.copytree(project_root / "extension", extension_target)

    logger.info("环境创建完成！")
    logger.info(f"1. 加载扩展: {extension_target}")
    logger.info(f"2. 激活环境: {venv_dir}\\Scripts\\activate")
    logger.info(f"3. 运行测试: python advanced_test.py")


if __name__ == "__main__":
    main()
