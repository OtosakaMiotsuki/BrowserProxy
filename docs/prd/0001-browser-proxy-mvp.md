# PRD: BrowserProxy MVP

## Problem Statement

用户需要操控已经打开的浏览器页面（如自动搜索、自动填写表单、自动下载等），但现有的浏览器自动化工具（Selenium、Playwright）都需要自己启动新的浏览器实例，无法操控用户已经打开并登录的浏览器页面。这导致用户无法利用已有的登录状态、Cookie、浏览器配置等。

## Solution

开发一个浏览器自动化工具，通过 Chrome 扩展 + WebSocket + Python 实现对已打开浏览器的操控。Chrome 扩展作为 WebSocket 服务端运行在浏览器中，Python 脚本作为客户端连接进来发送操控指令。用户可以将 Python 脚本打包成独立的 exe 程序，每个程序执行特定的自动化任务。

## User Stories

### 核心功能
1. As a 用户, I want to 安装 Chrome 扩展后能通过 Python 控制浏览器, so that 我可以自动化操作已打开的页面
2. As a 用户, I want to 通过 Python 选择要控制的标签页, so that 我可以精确操控目标页面
3. As a 用户, I want to 通过 URL 和标题匹配自动找到目标标签页, so that 不需要手动查找标签页
4. As a 用户, I want 当有多个匹配的标签页时能手动选择, so that 我可以精确控制目标页面
5. As a 用户, I want 当没有匹配的标签页时得到提示, so that 我知道需要先打开对应页面

### DOM 操作
6. As a 用户, I want to 通过 CSS 选择器点击页面元素, so that 我可以自动化点击按钮和链接
7. As a 用户, I want to 通过 XPath 选择器点击页面元素, so that 我可以用更灵活的方式定位元素
8. As a 用户, I want to 向输入框输入文本, so that 我可以自动化填写表单
9. As a 用户, I want to 获取元素的文本内容, so that 我可以读取页面信息
10. As a 用户, I want to 获取元素的属性值, so that 我可以读取元素状态
11. As a 用户, I want to 检查元素是否存在, so that 我可以根据页面状态决定下一步操作
12. As a 用户, I want to 等待元素出现后再操作, so that 我可以处理异步加载的页面

### 页面导航
13. As a 用户, I want to 跳转到指定 URL, so that 我可以导航到目标页面
14. As a 用户, I want to 执行浏览器的前进/后退操作, so that 我可以模拟用户导航
15. As a 用户, I want to 刷新当前页面, so that 我可以重新加载页面内容

### JavaScript 执行
16. As a 用户, I want to 在页面上下文执行任意 JavaScript 代码, so that 我可以实现复杂的自动化逻辑
17. As a 用户, I want to 获取 JavaScript 执行的返回值, so that 我可以根据执行结果做判断

### 标签页管理
18. As a 用户, I want to 获取所有打开的标签页列表, so that 我可以了解浏览器状态
19. As a 用户, I want to 获取标签页的 URL 和标题, so that 我可以识别目标页面
20. As a 用户, I want to 按需注入 Content Script, so that 只有被选中的标签页才会被操控

### 错误处理
21. As a 用户, I want to 当 WebSocket 连接失败时得到明确的错误提示, so that 我知道如何解决问题
22. As a 用户, I want to 当操作执行失败时得到详细的错误信息, so that 我可以调试问题
23. As a 用户, I want to 当标签页关闭时得到通知, so that 我可以知道操控已失效

### 日志与调试
24. As a 用户, I want to 通过 loguru 查看详细的操作日志, so that 我可以追踪问题
25. As a 用户, I want to 日志包含时间戳、操作类型、目标元素等信息, so that 我可以快速定位问题

### 分发与使用
26. As a 用户, I want to 将 Python 脚本打包成独立的 exe 程序, so that 其他用户不需要安装 Python 环境
27. As a 用户, I want to Chrome 扩展能打包成 .crx 文件, so that 可以方便分发给其他用户
28. As a 用户, I want to 有示例程序展示如何使用, so that 我可以快速上手

## Implementation Decisions

### 模块划分

1. **Chrome 扩展模块**
   - Manifest V3 格式
   - Service Worker (background.js): 维持 WebSocket 连接，管理标签页，转发指令
   - Content Script (content.js): 注入目标页面，执行 DOM 操作
   - 按需注入 Content Script，只有被选中的标签页才注入

2. **Python WebSocket 客户端模块**
   - 使用 websocket-client 库
   - 支持异步接收事件推送
   - 自动重连机制

3. **Python Browser 模块**
   - Browser 类：连接管理、标签页选择、标签页匹配
   - DrissionPage 风格 API
   - 链式调用支持

4. **Python Tab 模块**
   - Tab 类：DOM 操作、页面导航、JS 执行
   - 支持 CSS 和 XPath 选择器
   - 元素等待机制

5. **Python 标签页匹配模块**
   - URL + 标题匹配
   - 支持多个匹配结果的选择

### WebSocket 协议

- 格式: JSON
- 连接地址: ws://localhost:8765
- 请求包含: id (请求ID), tab_id (目标标签页), action (操作类型), params (参数)
- 响应包含: id (对应请求ID), success (是否成功), data (返回数据)
- 事件推送: event (事件类型), tab_id, 相关数据

### API 设计

```python
# 连接浏览器
browser = Browser()

# 选择标签页（自动匹配）
tab = browser.match(url_contains="baidu.com", title_contains="百度")

# 或手动选择
tab = browser.tabs[0]

# DOM 操作
tab.ele('#btn').click()
tab.ele('#input').input('关键词')
tab.ele('.result').text

# 页面导航
tab.get('https://example.com')
tab.back()
tab.forward()
tab.refresh()

# JavaScript 执行
tab.run_js('return document.title')
```

### 日志设计

- 使用 loguru 库
- 日志级别: DEBUG, INFO, WARNING, ERROR
- 日志内容: 时间戳, 操作类型, 目标元素, 结果
- 支持文件输出和控制台输出

## Testing Decisions

### 测试策略

1. **单元测试**
   - WebSocket 客户端: 测试连接、断开、消息收发
   - 标签页匹配: 测试 URL 匹配、标题匹配、多结果处理
   - Browser 类: 测试连接管理、标签页选择
   - Tab 类: 测试各操作方法的参数验证

2. **集成测试**
   - Chrome 扩展: 测试 Service Worker 和 Content Script 通信
   - 端到端: Python 发送指令 → 扩展执行 → 返回结果

3. **测试工具**
   - pytest 作为测试框架
   - mock 用于模拟 WebSocket 连接
   - 真实浏览器环境用于集成测试

### 测试重点

- 错误处理路径（连接失败、操作失败、标签页关闭）
- 并发场景（多个 Python 客户端同时连接）
- 边界情况（元素不存在、JS 执行超时）

## Out of Scope

以下功能不在 MVP 范围内：

1. **网络请求拦截/修改** — 后续版本
2. **事件监听**（DOM 事件、页面加载完成等） — 后续版本
3. **Cookie/Storage 操作** — 后续版本
4. **截图功能** — 后续版本
5. **标签页管理**（创建、关闭标签页） — 后续版本
6. **远程连接** — 后续版本
7. **Token 认证** — 后续版本
8. **PySide6 GUI 编排工具** — 后续版本（Phase 3）
9. **多浏览器支持** — 仅支持 Chrome

## Further Notes

### 依赖项

**Chrome 扩展:**
- 无外部依赖，使用 Chrome 原生 API

**Python:**
- websocket-client: WebSocket 客户端
- loguru: 日志管理
- PyInstaller: 打包成 exe（可选）

### 技术风险

1. **Content Script 注入时机** — 需要确保在页面加载完成后注入
2. **WebSocket 连接稳定性** — 需要处理断线重连
3. **跨域限制** — Content Script 受 Chrome 安全策略限制

### 未来扩展

- 支持 Firefox 扩展
- 支持远程 WebSocket 连接
- 添加 Token 认证
- 添加网络请求拦截功能
- 添加事件监听功能
- 添加 PySide6 GUI 编排工具
