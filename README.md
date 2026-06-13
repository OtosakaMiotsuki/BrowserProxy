# BrowserProxy

通过 Chrome 扩展 + Python 实现对已打开浏览器的自动化操控。

## 目录

- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [安装](#安装)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [API 参考](#api-参考)
- [示例程序](#示例程序)
- [架构说明](#架构说明)
- [常见问题](#常见问题)
- [开发指南](#开发指南)

---

## 功能特性

- ✅ **操控已打开的浏览器** - 无需启动新的浏览器实例
- ✅ **DOM 操作** - 点击、输入、获取文本/属性
- ✅ **页面导航** - 跳转 URL、前进、后退、刷新
- ✅ **JavaScript 执行** - 在页面上下文执行任意 JS 代码
- ✅ **标签页管理** - 获取标签页列表、按 URL/标题匹配
- ✅ **多 Python 客户端** - 多个脚本可同时连接
- ✅ **DrissionPage 风格 API** - 简洁易用的链式调用

---

## 系统要求

### 浏览器
- Google Chrome 或基于 Chromium 的浏览器（Edge、Brave 等）

### Python
- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) 包管理器（推荐）

### 操作系统
- Windows 10/11
- macOS
- Linux

---

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/OtosakaMiotsuki/BrowserProxy.git
cd BrowserProxy
```

### 2. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install .
```

### 3. 安装 Chrome 扩展

1. 打开 Chrome 浏览器，访问 `chrome://extensions/`
2. 开启右上角的 **"开发者模式"**
3. 点击 **"加载已解压的扩展程序"**
4. 选择项目中的 `extension/` 目录
5. 扩展安装完成，浏览器右上角会出现 BrowserProxy 图标

---

## 快速开始

### 示例：打印所有标签页

```python
from browserproxy import Browser

# 创建浏览器连接（会启动 WebSocket 服务端）
browser = Browser(port=8765)

try:
    # 启动服务并等待扩展连接
    browser.connect(timeout=30)

    # 获取所有标签页
    tabs = browser.get_tabs()
    print(f"找到 {len(tabs)} 个标签页")

    for tab in tabs:
        print(f"[{tab.tab_id}] {tab.title} - {tab.url}")

finally:
    browser.disconnect()
```

### 运行步骤

1. **运行 Python 程序**
   ```bash
   uv run python your_script.py
   ```

2. **连接 Chrome 扩展**
   - 点击浏览器右上角的 BrowserProxy 图标
   - 输入端口号（默认 `8765`）
   - 点击 **"连接"** 按钮

3. **等待连接成功**
   - 扩展图标显示 "ON" 表示连接成功
   - Python 程序会继续执行

---

## 使用指南

### 基本流程

```python
from browserproxy import Browser

# 1. 创建浏览器连接
browser = Browser(port=8765)

# 2. 启动服务并等待扩展连接
browser.connect(timeout=30)

# 3. 获取标签页
tabs = browser.get_tabs()

# 4. 匹配目标标签页
tab = browser.match(url_contains="example.com")

# 5. 执行操作
tab.ele("#btn").click()           # 点击元素
tab.ele("#input").input("hello")  # 输入文本
text = tab.ele(".title").text     # 获取文本

# 6. 页面导航
tab.get("https://example.com")    # 跳转 URL
tab.back()                        # 后退
tab.forward()                     # 前进
tab.refresh()                     # 刷新

# 7. 断开连接
browser.disconnect()
```

### 标签页匹配

```python
# 通过 URL 匹配
tab = browser.match(url_contains="baidu.com")

# 通过标题匹配
tab = browser.match(title_contains="百度")

# 同时匹配 URL 和标题
tab = browser.match(url_contains="baidu.com", title_contains="百度")

# 获取所有匹配的标签页
tabs = browser.match_all(url_contains="baidu.com")

# 按 ID 选择标签页
tab = browser.select_tab(123456)
```

### 元素操作

```python
# CSS 选择器
tab.ele("#btn").click()              # ID 选择器
tab.ele(".btn").click()              # 类选择器
tab.ele("button").click()            # 标签选择器
tab.ele("#form .input").input("text") # 组合选择器

# XPath 选择器
tab.ele("xpath=//button[@type='submit']").click()
tab.ele("xpath=//div[@class='content']").text

# 获取属性
href = tab.ele("a").attr("href")
src = tab.ele("img").attr("src")

# 检查元素是否存在
if tab.ele("#btn").exists():
    tab.ele("#btn").click()
```

### 页面内容获取

```python
# 获取页面文本
text = tab.text

# 获取页面 HTML
html = tab.html

# 获取当前 URL
url = tab.current_url

# 获取页面标题
title = tab.current_title

# 获取元素属性
href = tab.ele("a").attr("href")
src = tab.ele("img").attr("src")
```

---

## API 参考

### Browser 类

```python
class Browser:
    def __init__(self, host: str = "localhost", port: int = 8765)
```

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `connect(timeout=30)` | `timeout: float` | `None` | 启动服务并等待扩展连接 |
| `disconnect()` | - | `None` | 断开连接并停止服务 |
| `get_tabs()` | - | `List[Tab]` | 获取所有标签页 |
| `match(url_contains="", title_contains="")` | `url_contains: str`, `title_contains: str` | `Optional[Tab]` | 匹配单个标签页 |
| `match_all(url_contains="", title_contains="")` | `url_contains: str`, `title_contains: str` | `List[Tab]` | 匹配所有标签页 |
| `select_tab(tab_id)` | `tab_id: int` | `Optional[Tab]` | 按 ID 选择标签页 |

**属性：**
- `connected: bool` - 是否已连接
- `tabs: List[Tab]` - 标签页列表

---

### Tab 类

```python
class Tab:
    def __init__(self, tab_id: int, ws_server: Any, url: str = "", title: str = "")
```

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `ele(selector)` | `selector: str` | `Element` | 获取元素 |
| `eles(selector)` | `selector: str` | `Elements` | 获取多个元素 |
| `get(url)` | `url: str` | `None` | 跳转到指定 URL |
| `back()` | - | `None` | 后退 |
| `forward()` | - | `None` | 前进 |
| `refresh()` | - | `None` | 刷新页面 |
| `html` (属性) | - | `str` | 获取页面 HTML |
| `text` (属性) | - | `str` | 获取页面文本 |
| `current_url` (属性) | - | `str` | 获取当前 URL |
| `current_title` (属性) | - | `str` | 获取页面标题 |

**属性：**
- `tab_id: int` - 标签页 ID
- `url: str` - 标签页 URL
- `title: str` - 标签页标题

---

### Element 类

```python
class Element:
    def __init__(self, tab: Tab, selector: str)
```

| 方法/属性 | 参数 | 返回值 | 说明 |
|-----------|------|--------|------|
| `click()` | - | `None` | 点击元素 |
| `input(text)` | `text: str` | `None` | 输入文本 |
| `clear()` | - | `None` | 清空输入框 |
| `select(value)` | `value: str` | `None` | 选择下拉框选项 |
| `check()` | - | `None` | 勾选复选框 |
| `uncheck()` | - | `None` | 取消勾选 |
| `hover()` | - | `None` | 悬停元素 |
| `focus()` | - | `None` | 聚焦元素 |
| `text` (属性) | - | `str` | 获取元素文本 |
| `html` (属性) | - | `str` | 获取元素 HTML |
| `attr(name)` | `name: str` | `Optional[str]` | 获取元素属性 |
| `exists()` | - | `bool` | 检查元素是否存在 |
| `is_visible()` | - | `bool` | 检查元素是否可见 |
| `ele(selector)` | `selector: str` | `Element` | 在当前元素内查找子元素 |
| `eles(selector)` | `selector: str` | `Elements` | 在当前元素内查找多个子元素 |

---

### 选择器支持

| 类型 | 示例 | 说明 |
|------|------|------|
| CSS ID | `#btn` | ID 选择器 |
| CSS 类 | `.btn` | 类选择器 |
| CSS 标签 | `button` | 标签选择器 |
| CSS 组合 | `#form .input` | 组合选择器 |
| XPath | `xpath=//button[@type='submit']` | XPath 选择器 |

---

## 示例程序

### 1. 百度搜索

```python
from browserproxy import Browser
import time

browser = Browser()
browser.connect()

# 匹配百度标签页
tab = browser.match(url_contains="baidu.com")

if tab:
    # 输入搜索关键词
    tab.ele("#kw").input("BrowserProxy")

    # 点击搜索按钮
    tab.ele("#su").click()

    # 等待搜索结果
    time.sleep(2)

    # 获取搜索结果标题
    title = tab.current_title
    print(f"页面标题: {title}")

browser.disconnect()
```

### 2. 表单自动填写

```python
from browserproxy import Browser

browser = Browser()
browser.connect()

tab = browser.match(url_contains="form-page.com")

if tab:
    # 填写表单
    tab.ele("#username").input("myuser")
    tab.ele("#password").input("mypassword")
    tab.ele("#email").input("test@example.com")

    # 选择下拉框
    tab.ele("#select").select("option1")

    # 勾选复选框
    tab.ele("#checkbox").check()

    # 提交表单
    tab.ele("button[type='submit']").click()

browser.disconnect()
```

---

## 架构说明

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Python 程序                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Browser 类                        │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Tab 类    │  │  Element 类  │  │ TabMatcher  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WebSocket 服务端                        │   │
│  │           (ws://localhost:8765)                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ WebSocket 连接
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Chrome 扩展                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Service Worker                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │  消息处理   │  │  标签页管理  │  │  DOM 操作   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Content Script                          │   │
│  │           (注入到目标页面)                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Chrome 浏览器                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  标签页 1   │  │  标签页 2   │  │  标签页 3   │   ...   │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 通信流程

1. **Python 启动** - 创建 WebSocket 服务端，监听指定端口
2. **扩展连接** - Chrome 扩展连接到 Python 的 WebSocket 服务端
3. **发送命令** - Python 发送操作命令（如点击、输入）
4. **执行操作** - Chrome 扩展在目标页面执行 DOM 操作
5. **返回结果** - Chrome 扩展返回执行结果给 Python

### WebSocket 协议

**请求格式（Python → 扩展）：**
```json
{
    "id": "req-001",
    "tab_id": 123456,
    "action": "click",
    "params": {
        "selector": "#btn"
    }
}
```

**响应格式（扩展 → Python）：**
```json
{
    "id": "req-001",
    "success": true,
    "data": null
}
```

**支持的操作：**
- `list_tabs` - 获取所有标签页
- `inject_content_script` - 注入 Content Script
- `click` - 点击元素
- `input` - 输入文本
- `get_text` - 获取元素文本
- `get_attr` - 获取元素属性
- `exists` - 检查元素是否存在
- `navigate` - 跳转 URL
- `back` / `forward` / `refresh` - 页面导航
- `execute_script` - 执行 JavaScript

---

## 常见问题

### Q: 连接超时怎么办？

**A:** 检查以下几点：
1. Chrome 扩展是否已安装并启用
2. 扩展弹窗中输入的端口号是否正确
3. Python 程序是否已启动
4. 防火墙是否阻止了本地连接

### Q: 元素找不到怎么办？

**A:** 
1. 确保页面已完全加载
2. 使用浏览器开发者工具检查元素选择器
3. 尝试使用不同的选择器（CSS 或 XPath）
4. 使用 `exists()` 方法检查元素是否存在

### Q: 如何处理动态加载的内容？

**A:**
1. 使用 `time.sleep()` 等待内容加载
2. 使用 `wait_for_element(selector)` 等待元素出现
3. 使用 `wait_for_text(text)` 等待文本出现

### Q: 可以同时控制多个浏览器吗？

**A:** 目前只支持控制一个浏览器实例。每个 Python 程序需要使用不同的端口号。

### Q: 如何在无头模式下使用？

**A:** BrowserProxy 需要操控已打开的浏览器，不支持无头模式。如需无头自动化，建议使用 Selenium 或 Playwright。

---

## 开发指南

### 项目结构

```
BrowserProxy/
├── src/browserproxy/           # Python 核心库
│   ├── __init__.py
│   ├── browser.py              # Browser 类
│   ├── tab.py                  # Tab 和 Element 类
│   ├── match.py                # 标签页匹配
│   ├── ws_server.py            # WebSocket 服务端
│   ├── ws_client.py            # WebSocket 客户端
│   └── exceptions.py           # 异常定义
├── extension/                  # Chrome 扩展
│   ├── manifest.json
│   ├── background.js           # Service Worker
│   ├── content.js              # Content Script
│   ├── popup.html              # 弹窗页面
│   └── popup.js                # 弹窗脚本
├── tests/                      # 单元测试
├── examples/                   # 示例程序
└── pyproject.toml              # 项目配置
```

### 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_browser.py -v
```

### 添加新功能

1. 在 `src/browserproxy/` 中添加实现
2. 在 `tests/` 中添加测试用例
3. 在 `examples/` 中添加示例程序
4. 更新本文档

---

## 依赖项

### Python 依赖
- `websocket-client` - WebSocket 客户端
- `websockets` - WebSocket 服务端
- `loguru` - 日志管理

### 开发依赖
- `pytest` - 测试框架
- `pytest-cov` - 测试覆盖率
- `DrissionPage` - 集成测试对比

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 联系方式

- GitHub: [OtosakaMiotsuki](https://github.com/OtosakaMiotsuki)
- 博客: [miotsuki.cn](https://miotsuki.cn/)
