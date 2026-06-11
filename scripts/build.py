"""
打包脚本 - 将扩展复制到包内并构建分发包
"""

import shutil
import subprocess
import sys
from pathlib import Path
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    extension_source = project_root / "extension"
    package_dir = project_root / "src" / "browserproxy"
    extension_target = package_dir / "extension"

    logger.info("=" * 60)
    logger.info("BrowserProxy 打包工具")
    logger.info("=" * 60)

    # 步骤 1: 复制扩展到包内
    logger.info("步骤 1: 复制 Chrome 扩展...")

    if extension_target.exists():
        shutil.rmtree(extension_target)

    shutil.copytree(extension_source, extension_target)
    logger.info(f"✅ 扩展已复制到: {extension_target}")

    # 步骤 2: 清理旧的构建文件
    logger.info("步骤 2: 清理旧的构建文件...")
    for dir_name in ["dist", "build", "*.egg-info"]:
        for p in project_root.glob(dir_name):
            if p.is_dir():
                shutil.rmtree(p)
                logger.info(f"  删除: {p}")

    # 步骤 3: 构建分发包
    logger.info("步骤 3: 构建分发包...")

    # 安装构建工具
    subprocess.run([sys.executable, "-m", "pip", "install", "build"], check=True)

    # 构建
    subprocess.run([sys.executable, "-m", "build"], cwd=str(project_root), check=True)

    logger.info("✅ 构建完成！")

    # 步骤 4: 显示结果
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        logger.info("\n" + "=" * 60)
        logger.info("生成的文件:")
        logger.info("=" * 60)

        for file in dist_dir.iterdir():
            size = file.stat().st_size / 1024
            logger.info(f"  {file.name} ({size:.2f} KB)")

    logger.info("\n" + "=" * 60)
    logger.info("发布到 PyPI:")
    logger.info("=" * 60)
    logger.info("1. 安装 twine: pip install twine")
    logger.info("2. 上传: twine upload dist/*")
    logger.info("")
    logger.info("或者使用以下命令:")
    logger.info("  uv run twine upload dist/*")

    # 步骤 5: 清理扩展副本
    logger.info("\n步骤 5: 清理...")
    if extension_target.exists():
        shutil.rmtree(extension_target)
        logger.info("✅ 已清理扩展副本")


if __name__ == "__main__":
    main()
