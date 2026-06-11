# 豆瓣 Top250 测试 Demo
# 测试 BrowserProxy 的完整功能

## 环境要求

- Python 3.10+
- Chrome 浏览器
- BrowserProxy Chrome 扩展

## 安装步骤

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装 BrowserProxy（从本地打包文件）
pip install ../../dist/browserproxy-0.2.0-py3-none-any.whl

# 4. 安装扩展
python -c "from browserproxy import install_extension; install_extension()"

# 5. 运行测试
python douban_test.py
```

## 测试内容

1. 打开豆瓣 Top250 页面
2. 自动滚动到底部
3. 获取所有电影信息（名称、评分、评价数）
4. 点击下一页
5. 继续获取下一页的电影信息
6. 保存结果到文件
