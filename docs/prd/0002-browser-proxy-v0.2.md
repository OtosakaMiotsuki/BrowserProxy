# PRD: BrowserProxy v0.2.0 - 浏览器自动化库

## Problem Statement

用户需要操控已经打开的浏览器页面（如自动搜索、自动填写表单、数据采集、文件下载等），但现有的浏览器自动化工具（Selenium、Playwright）都需要自己启动新的浏览器实例，无法操控用户已经打开并登录的浏览器页面。这导致用户无法利用已有的登录状态、Cookie、浏览器配置等。

现有工具 DrissionPage 虽然解决了这个问题，但用户希望有一个更轻量、更灵活的解决方案，通过 Chrome 扩展 + Python WebSocket 的架构实现浏览器操控，支持多个 Python 脚本同时连接，便于不同业务场景的自动化。

## Solution

开发一个名为 BrowserProxy 的 Python 库，通过以下架构实现浏览器自动化：

1. **Chrome 扩展**：运行在浏览器中，作为 WebSocket 客户端连接到 Python 程序
2. **Python 库**：启动 WebSocket 服务端，接收扩展连接，提供 DrissionPage 风格的 API
3. **WebSocket 通信**：使用 JSON 协议进行双向通信，支持命令发送和响应接收

核心设计理念：
- **前提条件**：浏览器必须已打开，扩展必须已安装并连接
- **Python 作为服务端**：支持多个 Python 客户端同时连接
- **按需注入 Content Script**：只有被选中的标签页才会注入操作脚本
- **DrissionPage 风格 API**：简洁易用的链式调用

## User Stories

### 连接管理

1. As a 用户, I want to 通过 `Browser(port=8765)` 创建浏览器连接对象, so that 我可以指定 WebSocket 端口
2. As a 用户, I want to 通过 `browser.connect(timeout=30)` 启动服务并等待扩展连接, so that 我可以控制等待时间
3. As a 用户, I want to 当扩展连接成功后自动继续执行, so that 不需要手动干预
4. As a 用户, I want to 当连接超时时得到明确的错误提示, so that 我知道如何解决问题
5. As a 用户, I want to 通过 `browser.disconnect()` 断开连接, so that 我可以优雅地结束程序
6. As a 用户, I want to 当 WebSocket 断开时自动重连, so that 网络不稳定时程序仍能继续
7. As a 用户, I want to 通过心跳机制保持连接, so that 长时间运行不会断开

### 标签页管理

8. As a 用户, I want to 通过 `browser.get_tabs()` 获取所有标签页, so that 我可以了解浏览器状态
9. As a 用户, I want to 通过 `browser.get_active_tab()` 获取当前活动标签页, so that 我可以操作当前页面
10. As a 用户, I want to 通过 `browser.new_tab(url)` 创建新标签页, so that 我可以打开新页面
11. As a 用户, I want to 通过 `browser.close_tab(tab_id)` 关闭标签页, so that 我可以清理不需要的页面
12. As a 用户, I want to 通过 `browser.switch_tab(tab_id)` 切换标签页, so that 我可以在多个页面间切换
13. As a 用户, I want to 通过 `browser.match(url_contains="baidu.com")` 按 URL 匹配标签页, so that 我可以快速找到目标页面
14. As a 用户, I want to 通过 `browser.match(title_contains="百度")` 按标题匹配标签页, so that 我可以通过页面标题查找
15. As a 用户, I want to 通过 `browser.match_all(...)` 获取所有匹配的标签页, so that 我可以处理多个相同类型的页面
16. As a 用户, I want to 通过 `browser.tab_count` 获取标签页数量, so that 我可以快速了解有多少页面

### 页面导航

17. As a 用户, I want to 通过 `tab.get(url)` 跳转到指定 URL, so that 我可以导航到目标页面
18. As a 用户, I want to 通过 `tab.back()` 后退, so that 我可以返回上一页
19. As a 用户, I want to 通过 `tab.forward()` 前进, so that 我可以前进到下一页
20. As a 用户, I want to 通过 `tab.refresh()` 刷新页面, so that 我可以重新加载内容

### 页面内容获取

21. As a 用户, I want to 通过 `tab.html` 获取页面 HTML, so that 我可以分析页面结构
22. As a 用户, I want to 通过 `tab.text` 获取页面文本, so that 我可以读取页面所有文字
23. As a 用户, I want to 通过 `tab.current_url` 获取当前 URL, so that 我可以确认当前页面
24. As a 用户, I want to 通过 `tab.current_title` 获取当前标题, so that 我可以确认页面内容

### 页面滚动

25. As a 用户, I want to 通过 `tab.scroll_to(x, y)` 滚动到指定位置, so that 我可以看到页面特定区域
26. As a 用户, I want to 通过 `tab.scroll_by(x, y)` 滚动指定距离, so that 我可以微调滚动位置
27. As a 用户, I want to 通过 `tab.scroll_to_top()` 快速滚动到顶部, so that 我可以回到页面开始
28. As a 用户, I want to 通过 `tab.scroll_to_bottom()` 快速滚动到底部, so that 我可以看到页面底部内容

### 等待机制

29. As a 用户, I want to 通过 `tab.wait(seconds)` 等待指定时间, so that 我可以等待页面加载
30. As a 用户, I want to 通过 `tab.wait_for_load(timeout)` 等待页面加载完成, so that 我可以确保页面就绪
31. As a 用户, I want to 通过 `tab.wait_for_element(selector, timeout)` 等待元素出现, so that 我可以处理异步加载的元素
32. As a 用户, I want to 通过 `tab.wait_for_element_visible(selector, timeout)` 等待元素可见, so that 我可以确保元素可交互
33. As a 用户, I want to 通过 `tab.wait_for_element_hidden(selector, timeout)` 等待元素消失, so that 我可以等待 loading 结束
34. As a 用户, I want to 通过 `tab.wait_for_text(text, timeout)` 等待文本出现, so that 我可以等待内容加载

### 元素查找

35. As a 用户, I want to 通过 `tab.ele(selector)` 获取单个元素, so that 我可以操作页面元素
36. As a 用户, I want to 通过 `tab.eles(selector)` 获取所有匹配的元素, so that 我可以批量处理
37. As a 用户, I want to 通过 `tab.find_by_text(text)` 按文本查找元素, so that 我可以通过文字内容定位
38. As a 用户, I want to 通过 `tab.find_by_attr(attr, value)` 按属性查找元素, so that 我可以通过属性值定位

### 元素操作

39. As a 用户, I want to 通过 `element.click()` 点击元素, so that 我可以触发按钮或链接
40. As a 用户, I want to 通过 `element.input(text)` 输入文本, so that 我可以填写表单
41. As a 用户, I want to 通过 `element.text` 获取元素文本, so that 我可以读取元素内容
42. As a 用户, I want to 通过 `element.html` 获取元素 HTML, so that 我可以分析元素结构
43. As a 用户, I want to 通过 `element.outer_html` 获取元素外部 HTML, so that 我可以获取完整元素
44. As a 用户, I want to 通过 `element.attr(name)` 获取元素属性, so that 我可以读取 href、src 等
45. As a 用户, I want to 通过 `element.exists()` 检查元素是否存在, so that 我可以根据状态决定下一步
46. As a 用户, I want to 通过 `element.is_visible()` 检查元素是否可见, so that 我可以判断元素是否在视口
47. As a 用户, I want to 通过 `element.rect` 获取元素位置和大小, so that 我可以进行坐标操作
48. As a 用户, I want to 通过 `element.scroll_to()` 滚动到元素位置, so that 我可以看到不在视口的元素
49. As a 用户, I want to 通过 `element.parent` 获取父元素, so that 我可以进行 DOM 遍历
50. As a 用户, I want to 通过 `element.children` 获取子元素, so that 我可以遍历子节点

### 表单操作

51. As a 用户, I want to 通过 `element.select(value)` 选择下拉框选项, so that 我可以填写下拉表单
52. As a 用户, I want to 通过 `element.check()` 勾选复选框, so that 我可以选中选项
53. As a 用户, I want to 通过 `element.uncheck()` 取消勾选, so that 我可以取消选中
54. As a 用户, I want to 通过 `element.clear()` 清空输入框, so that 我可以重新输入
55. As a 用户, I want to 通过 `element.focus()` 聚焦元素, so that 我可以激活输入框
56. As a 用户, I want to 通过 `element.blur()` 失去焦点, so that 我可以结束输入
57. As a 用户, I want to 通过 `element.hover()` 悬停元素, so that 我可以触发 hover 效果

### 键盘操作

58. As a 用户, I want to 通过 `element.press_key(key)` 按下按键, so that 我可以触发键盘事件
59. As a 用户, I want to 通过 `element.press_enter()` 按下回车, so that 我可以提交表单
60. As a 用户, I want to 通过 `element.press_tab()` 按下 Tab, so that 我可以切换焦点
61. As a 用户, I want to 通过 `element.press_escape()` 按下 Escape, so that 我可以关闭弹窗
62. As a 用户, I want to 通过 `element.press_ctrl_a()` 全选, so that 我可以快速选中所有内容
63. As a 用户, I want to 通过 `element.press_ctrl_c()` 复制, so that 我可以复制选中内容
64. As a 用户, I want to 通过 `element.press_ctrl_v()` 粘贴, so that 我可以粘贴内容
65. As a 用户, I want to 通过 `element.press_key(key, modifiers)` 使用修饰键, so that 我可以组合按键

### 拖拽操作

66. As a 用户, I want to 通过 `element.drag(delta_x, delta_y)` 拖拽元素, so that 我可以移动元素位置
67. As a 用户, I want to 通过 `element.drag_to(target)` 拖拽到目标元素, so that 我可以实现拖放功能

### Cookie / Storage 操作

68. As a 用户, I want to 通过 `tab.get_cookies()` 获取所有 Cookie, so that 我可以查看登录状态
69. As a 用户, I want to 通过 `tab.get_cookie(name)` 获取指定 Cookie, so that 我可以读取特定值
70. As a 用户, I want to 通过 `tab.set_cookie(name, value)` 设置 Cookie, so that 我可以注入登录状态
71. As a 用户, I want to 通过 `tab.delete_cookie(name)` 删除 Cookie, so that 我可以清除登录状态
72. As a 用户, I want to 通过 `tab.get_local_storage(key)` 获取 localStorage, so that 我可以读取前端存储
73. As a 用户, I want to 通过 `tab.set_local_storage(key, value)` 设置 localStorage, so that 我可以注入数据
74. As a 用户, I want to 通过 `tab.delete_local_storage(key)` 删除 localStorage, so that 我可以清除数据
75. As a 用户, I want to 通过 `tab.get_session_storage(key)` 获取 sessionStorage, so that 我可以读取会话数据
76. As a 用户, I want to 通过 `tab.set_session_storage(key, value)` 设置 sessionStorage, so that 我可以注入会话数据

### iframe 操作

77. As a 用户, I want to 通过 `tab.get_iframes()` 获取所有 iframe, so that 我可以了解页面结构
78. As a 用户, I want to 通过 `tab.get_iframe_content(selector)` 获取 iframe 信息, so that 我可以分析 iframe

### 截图

79. As a 用户, I want to 通过 `tab.screenshot(path)` 截取页面并保存, so that 我可以保存页面快照
80. As a 用户, I want to 通过 `tab.screenshot()` 返回 base64 数据, so that 我可以灵活处理截图
81. As a 用户, I want to 通过 `tab.screenshot_element(selector)` 获取元素位置, so that 我可以裁剪特定区域

### JavaScript 执行

82. As a 用户, I want to 通过 `tab.run_js(script)` 执行 JavaScript 代码, so that 我可以实现复杂逻辑
83. As a 用户, I want to 通过 `tab.run_js()` 获取返回值, so that 我可以根据结果做判断

### 选择器支持

84. As a 用户, I want to 支持 CSS 选择器（#id, .class, tag）, so that 我可以用标准方式定位元素
85. As a 用户, I want to 支持 XPath 选择器, so that 我可以用更灵活的方式定位元素
86. As a 用户, I want to 支持 CSS 组合选择器（#form .input）, so that 我可以精确查找

### 错误处理

87. As a 用户, I want to 当连接失败时得到 ConnectionError, so that 我知道连接问题
88. As a 用户, I want to 当元素不存在时得到 ElementNotFoundError, so that 我知道选择器有问题
89. As a 用户, I want to 当等待超时时得到 WaitTimeoutError, so that 我知道需要调整超时时间
90. As a 用户, I want to 当 JS 执行失败时得到 JavaScriptError, so that 我知道代码有问题
91. As a 用户, I want to 所有异常都继承自 BrowserProxyError, so that 我可以统一捕获

### 安装与分发

92. As a 用户, I want to 通过 `pip install browserproxy` 安装库, so that 我可以快速开始使用
93. As a 用户, I want to 通过 `install_extension()` 安装 Chrome 扩展, so that 我不需要手动复制文件
94. As a 用户, I want to 扩展随库一起分发, so that 我不需要单独下载扩展
95. As a 用户, I want to 支持 Python 3.10+, so that 我可以在大多数环境使用

## Implementation Decisions

### 架构决策

1. **Python 作为 WebSocket 服务端**：Python 程序启动 WebSocket 服务，Chrome 扩展连接进来。这样多个 Python 脚本可以同时连接到同一个浏览器实例，便于不同业务场景的自动化。

2. **Chrome 扩展作为客户端**：扩展连接到 Python 的 WebSocket 服务端，接收命令并执行。扩展可以操控任意已打开的页面，无需启动新的浏览器实例。

3. **异步→同步包装器**：WebSocket 服务端内部使用 asyncio 异步处理，但对外提供同步 API（SyncWebSocketServer），简化用户使用。内部通过线程和 asyncio.run_coroutine_threadsafe 实现同步调用。

4. **JSON 协议**：使用 JSON 格式进行 WebSocket 通信，便于扩展字段和调试。每个请求包含 id、action、params，响应包含 id、success、data/error。

5. **按需注入 Content Script**：只有被选中的标签页才会注入 Content Script，避免不必要的性能开销和安全风险。

6. **心跳和自动重连**：扩展每 5 秒发送心跳，断线后使用指数退避算法自动重连（最大 30 秒），确保长时间运行的稳定性。

### 模块划分

1. **Browser 类**：顶层 API，管理连接和标签页。提供连接/断开、标签页获取/创建/关闭/切换/匹配等功能。

2. **Tab 类**：单个标签页的操作接口。提供页面导航、内容获取、滚动、等待、Cookie/Storage、iframe、截图、JavaScript 执行等功能。

3. **Element 类**：单个 DOM 元素的操作接口。提供点击、输入、获取内容/属性、状态检查、位置获取、表单操作、键盘操作、拖拽等功能。

4. **Elements 类**：多个元素的集合类。支持迭代、索引、获取数量等操作。

5. **VirtualElement 类**：虚拟元素类，用于 DOM 遍历返回的结果（如 parent、children）。

6. **TabMatcher 类**：标签页匹配器，支持按 URL 和标题匹配标签页。

7. **SyncWebSocketServer**：同步 WebSocket 服务端包装器，内部使用 asyncio，对外提供同步 API。

8. **exceptions.py**：自定义异常层次结构，所有异常继承自 BrowserProxyError。

### API 设计决策

1. **DrissionPage 风格**：采用 DrissionPage 的 API 风格，如 `tab.ele("#btn").click()`，用户熟悉且简洁。

2. **属性访问**：部分内容使用属性访问（如 `tab.html`、`element.text`），符合 Python 习惯。

3. **方法调用**：操作类使用方法调用（如 `tab.get(url)`、`element.click()`），语义清晰。

4. **异常而非返回值**：错误情况抛出异常而非返回布尔值，便于调试和错误处理。

### WebSocket 协议

请求格式：
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

响应格式：
```json
{
    "id": "req-001",
    "success": true,
    "data": null
}
```

心跳消息：
```json
{"type": "heartbeat"}
// 响应
{"type": "heartbeat_ack"}
```

注册消息：
```json
{"type": "register", "client_type": "extension"}
// 响应
{"type": "registered", "success": true}
```

### 依赖项

核心依赖：
- websocket-client：WebSocket 客户端（备用）
- websockets：WebSocket 服务端
- loguru：日志管理

开发依赖：
- pytest：测试框架
- pytest-cov：测试覆盖率
- DrissionPage：集成测试

## Testing Decisions

### 测试策略

1. **单元测试**：使用 mock 模拟 WebSocket 连接，测试各个类的核心逻辑。覆盖 Browser、Tab、Element、TabMatcher、WebSocketClient 等模块。

2. **集成测试**：使用 DrissionPage 驱动真实浏览器，测试完整的连接和操作流程。需要手动安装 Chrome 扩展。

3. **测试覆盖**：核心模块（Browser、Tab、Element）的测试覆盖率应达到 80% 以上。

### 测试重点

1. 连接管理：连接成功/失败、断开连接、重连机制
2. 标签页管理：获取/创建/关闭/切换、URL/标题匹配
3. DOM 操作：点击、输入、获取内容、属性
4. 等待机制：元素出现/可见/消失、超时处理
5. 异常处理：各种错误场景的异常抛出

### 测试文件

- test_browser.py：Browser 类测试
- test_tab.py：Tab 和 Element 类测试
- test_match.py：TabMatcher 类测试
- test_ws_client.py：WebSocket 客户端测试
- test_integration.py：集成测试（需要手动运行）

## Out of Scope

以下功能不在 v0.2.0 范围内，留待后续版本：

1. **文件下载管理**：下载链接点击、下载路径获取、等待下载完成
2. **网络请求拦截**：请求拦截、响应拦截、请求修改
3. **Shadow DOM 支持**：穿透 Shadow DOM 查找元素
4. **多窗口管理**：获取所有窗口、切换窗口焦点、关闭窗口
5. **事件监听**：DOM 事件监听、页面加载事件、网络请求事件
6. **远程连接**：支持远程 WebSocket 连接（当前仅支持 localhost）
7. **Token 认证**：WebSocket 连接的 Token 验证
8. **PySide6 GUI**：可视化任务编排工具
9. **异步 API**：原生 asyncio 支持（当前通过同步包装器实现）

## Further Notes

### 已知限制

1. Chrome 扩展无法作为 WebSocket 服务端（Chrome 安全限制），因此 Python 必须作为服务端
2. Content Script 注入受 Chrome 安全策略限制，某些页面（如 chrome://）无法注入
3. 截图功能依赖 Chrome 的 captureVisibleTab API，只能截取当前可见区域
4. 拖拽操作通过模拟鼠标事件实现，某些使用自定义拖拽库的页面可能不生效

### 后续迭代计划

**v0.3.0（功能完善）**
- 文件下载管理
- 网络请求拦截
- Shadow DOM 支持

**v0.4.0（稳定性）**
- 完善错误处理
- 添加重试机制
- 性能优化

**v1.0.0（正式发布）**
- API 冻结，向后兼容承诺
- 完整文档和示例
- PyPI 发布
- CI/CD 自动化

### 贡献指南

欢迎提交 Issue 和 Pull Request。请确保：
1. 代码符合项目风格
2. 添加相应的测试用例
3. 更新相关文档
