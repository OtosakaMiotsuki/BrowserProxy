/**
 * BrowserProxy Chrome 扩展 - Service Worker
 * 连接到 Python 程序的 WebSocket 服务端
 * 支持心跳和自动重连
 */

// WebSocket 连接状态
let ws = null;
let connected = false;
let currentPort = 8765;
let heartbeatInterval = null;
let reconnectTimeout = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_BASE_DELAY = 1000; // 1秒

// 标签页信息缓存
let tabsInfo = new Map();

/**
 * 连接到 WebSocket 服务端
 */
function connectWebSocket(port = 8765) {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    console.log('WebSocket 已连接或正在连接');
    return;
  }

  currentPort = port;

  try {
    ws = new WebSocket(`ws://localhost:${port}`);
  } catch (e) {
    console.error('创建 WebSocket 失败:', e);
    scheduleReconnect();
    return;
  }

  ws.onopen = () => {
    console.log(`WebSocket 连接成功: ws://localhost:${port}`);
    reconnectAttempts = 0;
    // 注册为扩展客户端
    ws.send(JSON.stringify({ type: 'register', client_type: 'extension' }));
    // 启动心跳
    startHeartbeat();
  };

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);

      // 处理注册响应
      if (message.type === 'registered') {
        if (message.success) {
          connected = true;
          updateBadge(true);
          console.log('注册成功');
        }
        return;
      }

      // 处理心跳响应
      if (message.type === 'heartbeat_ack') {
        return;
      }

      handleMessage(message);
    } catch (e) {
      console.error('解析消息失败:', e);
    }
  };

  ws.onclose = (event) => {
    console.log(`WebSocket 连接关闭 (code: ${event.code})`);
    connected = false;
    updateBadge(false);
    stopHeartbeat();

    // 如果不是主动关闭，尝试重连
    if (event.code !== 1000) {
      scheduleReconnect();
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
    connected = false;
    updateBadge(false);
  };
}

/**
 * 启动心跳
 */
function startHeartbeat() {
  stopHeartbeat();
  heartbeatInterval = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'heartbeat' }));
    }
  }, 5000); // 每5秒发送心跳
}

/**
 * 停止心跳
 */
function stopHeartbeat() {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }
}

/**
 * 计划重连（指数退避）
 */
function scheduleReconnect() {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.log('达到最大重连次数，停止重连');
    return;
  }

  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
  }

  const delay = Math.min(RECONNECT_BASE_DELAY * Math.pow(2, reconnectAttempts), 30000);
  console.log(`将在 ${delay}ms 后重连 (第 ${reconnectAttempts + 1} 次)`);

  reconnectTimeout = setTimeout(() => {
    reconnectAttempts++;
    connectWebSocket(currentPort);
  }, delay);
}

/**
 * 断开 WebSocket 连接
 */
function disconnectWebSocket() {
  // 停止重连
  if (reconnectTimeout) {
    clearTimeout(reconnectTimeout);
    reconnectTimeout = null;
  }
  reconnectAttempts = MAX_RECONNECT_ATTEMPTS; // 阻止自动重连

  stopHeartbeat();

  if (ws) {
    ws.close(1000); // 正常关闭
    ws = null;
  }
  connected = false;
  updateBadge(false);
}

/**
 * 更新扩展图标徽章
 */
function updateBadge(isConnected) {
  chrome.action.setBadgeText({
    text: isConnected ? 'ON' : 'OFF'
  });
  chrome.action.setBadgeBackgroundColor({
    color: isConnected ? '#4CAF50' : '#F44336'
  });
}

/**
 * 处理收到的消息
 */
async function handleMessage(message) {
  const { id, tab_id, action, params } = message;

  try {
    let result;

    switch (action) {
      // ========== 标签页管理 ==========
      case 'list_tabs':
        result = await listTabs();
        break;

      case 'get_active_tab':
        result = await getActiveTab();
        break;

      case 'create_tab':
        result = await createTab(params.url, params.active);
        break;

      case 'close_tab':
        result = await closeTab(tab_id);
        break;

      case 'switch_tab':
        result = await switchTab(tab_id);
        break;

      case 'get_tab_count':
        result = await getTabCount();
        break;

      // ========== Content Script 管理 ==========
      case 'inject_content_script':
        result = await injectContentScript(tab_id);
        break;

      // ========== DOM 操作 ==========
      case 'click':
        result = await executeOnTab(tab_id, 'click', params);
        break;

      case 'input':
        result = await executeOnTab(tab_id, 'input', params);
        break;

      case 'get_text':
        result = await executeOnTab(tab_id, 'getText', params);
        break;

      case 'get_html':
        result = await executeOnTab(tab_id, 'getHtml', params);
        break;

      case 'get_outer_html':
        result = await executeOnTab(tab_id, 'getOuterHtml', params);
        break;

      case 'get_attr':
        result = await executeOnTab(tab_id, 'getAttr', params);
        break;

      case 'exists':
        result = await executeOnTab(tab_id, 'exists', params);
        break;

      case 'is_visible':
        result = await executeOnTab(tab_id, 'isVisible', params);
        break;

      case 'get_elements':
        result = await executeOnTab(tab_id, 'getElements', params);
        break;

      case 'get_element_count':
        result = await executeOnTab(tab_id, 'getElementCount', params);
        break;

      case 'scroll_to_element':
        result = await executeOnTab(tab_id, 'scrollToElement', params);
        break;

      case 'get_element_rect':
        result = await executeOnTab(tab_id, 'getElementRect', params);
        break;

      case 'hover':
        result = await executeOnTab(tab_id, 'hover', params);
        break;

      case 'focus':
        result = await executeOnTab(tab_id, 'focus', params);
        break;

      case 'blur':
        result = await executeOnTab(tab_id, 'blur', params);
        break;

      case 'select_option':
        result = await executeOnTab(tab_id, 'selectOption', params);
        break;

      case 'check':
        result = await executeOnTab(tab_id, 'check', params);
        break;

      case 'uncheck':
        result = await executeOnTab(tab_id, 'uncheck', params);
        break;

      case 'clear':
        result = await executeOnTab(tab_id, 'clear', params);
        break;

      case 'wait_for_element_visible':
        result = await executeOnTab(tab_id, 'waitForElementVisible', params);
        break;

      case 'wait_for_element_hidden':
        result = await executeOnTab(tab_id, 'waitForElementHidden', params);
        break;

      case 'wait_for_text':
        result = await executeOnTab(tab_id, 'waitForText', params);
        break;

      case 'find_by_text':
        result = await executeOnTab(tab_id, 'findByText', params);
        break;

      case 'find_by_attr':
        result = await executeOnTab(tab_id, 'findByAttr', params);
        break;

      case 'get_element_parent':
        result = await executeOnTab(tab_id, 'getElementParent', params);
        break;

      case 'get_element_children':
        result = await executeOnTab(tab_id, 'getElementChildren', params);
        break;

      case 'press_key':
        result = await executeOnTab(tab_id, 'pressKey', params);
        break;

      case 'get_cookies':
        result = await executeOnTab(tab_id, 'getCookies', params);
        break;

      case 'get_cookie':
        result = await executeOnTab(tab_id, 'getCookie', params);
        break;

      case 'set_cookie':
        result = await executeOnTab(tab_id, 'setCookie', params);
        break;

      case 'delete_cookie':
        result = await executeOnTab(tab_id, 'deleteCookie', params);
        break;

      case 'get_local_storage':
        result = await executeOnTab(tab_id, 'getLocalStorage', params);
        break;

      case 'set_local_storage':
        result = await executeOnTab(tab_id, 'setLocalStorage', params);
        break;

      case 'delete_local_storage':
        result = await executeOnTab(tab_id, 'deleteLocalStorage', params);
        break;

      case 'get_session_storage':
        result = await executeOnTab(tab_id, 'getSessionStorage', params);
        break;

      case 'set_session_storage':
        result = await executeOnTab(tab_id, 'setSessionStorage', params);
        break;

      case 'delete_session_storage':
        result = await executeOnTab(tab_id, 'deleteSessionStorage', params);
        break;

      // ========== iframe 操作 ==========
      case 'get_iframes':
        result = await executeOnTab(tab_id, 'getIframes', params);
        break;

      case 'get_iframe_content':
        result = await getIframeContent(tab_id, params);
        break;

      // ========== 截图 ==========
      case 'screenshot':
        result = await takeScreenshot(tab_id, params);
        break;

      case 'screenshot_element':
        result = await screenshotElement(tab_id, params);
        break;

      // ========== 拖拽 ==========
      case 'drag':
        result = await executeOnTab(tab_id, 'drag', params);
        break;

      case 'drag_to':
        result = await executeOnTab(tab_id, 'dragTo', params);
        break;

      case 'wait_for_element':
        result = await executeOnTab(tab_id, 'waitForElement', params);
        break;

      // ========== 页面操作 ==========
      case 'navigate':
        result = await navigateTab(tab_id, params.url);
        break;

      case 'back':
        result = await goBack(tab_id);
        break;

      case 'forward':
        result = await goForward(tab_id);
        break;

      case 'refresh':
        result = await refreshTab(tab_id);
        break;

      case 'get_page_html':
        result = await executeOnTab(tab_id, 'getPageHtml', params);
        break;

      case 'get_page_text':
        result = await executeOnTab(tab_id, 'getPageText', params);
        break;

      case 'get_page_title':
        result = await executeOnTab(tab_id, 'getPageTitle', params);
        break;

      case 'get_page_url':
        result = await executeOnTab(tab_id, 'getPageUrl', params);
        break;

      case 'scroll_to':
        result = await executeOnTab(tab_id, 'scrollTo', params);
        break;

      case 'scroll_by':
        result = await executeOnTab(tab_id, 'scrollBy', params);
        break;

      case 'wait_for_load':
        result = await waitForLoad(tab_id, params.timeout);
        break;

      case 'execute_script':
        result = await executeScript(tab_id, params.script);
        break;

      default:
        result = { success: false, error: `未知操作: ${action}` };
    }

    // 发送响应
    sendResponse({ id, ...result });

  } catch (error) {
    console.error('执行操作失败:', error);
    sendResponse({
      id,
      success: false,
      error: error.message
    });
  }
}

/**
 * 发送响应
 */
function sendResponse(response) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(response));
  }
}

// ========== 标签页管理 ==========

/**
 * 获取所有标签页
 */
async function listTabs() {
  const tabs = await chrome.tabs.query({});
  const tabsData = tabs.map(tab => ({
    id: tab.id,
    url: tab.url || '',
    title: tab.title || '',
    active: tab.active,
    windowId: tab.windowId,
    index: tab.index
  }));

  return { success: true, data: tabsData };
}

/**
 * 获取当前活动标签页
 */
async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) {
    return {
      success: true,
      data: {
        id: tab.id,
        url: tab.url || '',
        title: tab.title || '',
        active: tab.active,
        windowId: tab.windowId,
        index: tab.index
      }
    };
  }
  return { success: false, error: '没有活动标签页' };
}

/**
 * 创建新标签页
 */
async function createTab(url = 'chrome://newtab/', active = true) {
  try {
    const tab = await chrome.tabs.create({ url, active });
    return {
      success: true,
      data: {
        id: tab.id,
        url: tab.url || '',
        title: tab.title || '',
        active: tab.active
      }
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 关闭标签页
 */
async function closeTab(tabId) {
  try {
    await chrome.tabs.remove(tabId);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 切换标签页（激活）
 */
async function switchTab(tabId) {
  try {
    const tab = await chrome.tabs.update(tabId, { active: true });
    // 将窗口也切换到前台
    await chrome.windows.update(tab.windowId, { focused: true });
    return {
      success: true,
      data: {
        id: tab.id,
        url: tab.url || '',
        title: tab.title || ''
      }
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 获取标签页数量
 */
async function getTabCount() {
  const tabs = await chrome.tabs.query({});
  return { success: true, data: tabs.length };
}

// ========== Content Script 管理 ==========

/**
 * 注入 Content Script
 */
async function injectContentScript(tabId) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ['content.js']
    });

    // 缓存标签页信息
    const tab = await chrome.tabs.get(tabId);
    tabsInfo.set(tabId, {
      url: tab.url,
      title: tab.title
    });

    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// ========== 页面操作 ==========

/**
 * 导航到指定 URL
 */
async function navigateTab(tabId, url) {
  try {
    await chrome.tabs.update(tabId, { url });
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 后退
 */
async function goBack(tabId) {
  try {
    await chrome.tabs.goBack(tabId);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 前进
 */
async function goForward(tabId) {
  try {
    await chrome.tabs.goForward(tabId);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 刷新页面
 */
async function refreshTab(tabId) {
  try {
    await chrome.tabs.reload(tabId);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 等待页面加载
 */
async function waitForLoad(tabId, timeout = 10000) {
  try {
    const tab = await chrome.tabs.get(tabId);
    if (tab.status === 'complete') {
      return { success: true };
    }

    // 等待页面加载完成
    return new Promise((resolve) => {
      const startTime = Date.now();
      const checkInterval = setInterval(async () => {
        try {
          const currentTab = await chrome.tabs.get(tabId);
          if (currentTab.status === 'complete' || Date.now() - startTime > timeout) {
            clearInterval(checkInterval);
            resolve({ success: currentTab.status === 'complete' });
          }
        } catch (e) {
          clearInterval(checkInterval);
          resolve({ success: false, error: e.message });
        }
      }, 100);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 执行 JavaScript 代码
 */
async function executeScript(tabId, script) {
  try {
    // new Function 在 Service Worker 中编译（不受页面 CSP 约束）
    // 编译后 Chrome 会把函数体序列化注入页面，页面看到的是普通函数声明，不是 eval
    const compiled = new Function('return (' + script + ')');
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: compiled,
    });

    if (results && results[0]) {
      return results[0].result;
    }
    return { success: false, error: '没有执行结果' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// ========== DOM 操作 ==========

/**
 * 在标签页上执行操作
 */
async function executeOnTab(tabId, action, params) {
  try {
    // 需要触发页面 JS 事件监听器的操作在主世界执行
    const mainWorldActions = [
      'click', 'selectOption', 'check', 'uncheck', 'hover',
      'focus', 'blur', 'pressKey', 'drag', 'dragTo'
    ];
    const world = mainWorldActions.includes(action) ? 'MAIN' : 'ISOLATED';

    const results = await chrome.scripting.executeScript({
      target: { tabId },
      world: world,
      func: executeDOMAction,
      args: [action, params]
    });

    if (results && results[0]) {
      return results[0].result;
    }
    return { success: false, error: '没有执行结果' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Content Script 中执行的函数
 * 所有 helper 必须定义在函数内部（Chrome API 序列化约束）
 */
function executeDOMAction(action, params) {
  // ========== 共享 Helper ==========

  /** 解析选择器 → { element, elements }。修复 XPath 上下文 bug。 */
  function resolveElement(sel, ctx) {
    if (!sel) return { element: null, elements: [] };
    if (sel.startsWith('//') || sel.startsWith('(')) {
      // 当 ctx 非 document 时，绝对 XPath 转相对路径以尊重上下文
      const xpath = (ctx !== document && sel.startsWith('//')) ? '.' + sel : sel;
      const result = document.evaluate(xpath, ctx, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
      const els = [];
      for (let i = 0; i < result.snapshotLength; i++) els.push(result.snapshotItem(i));
      return { element: els[0] || null, elements: els };
    }
    return {
      element: ctx.querySelector(sel),
      elements: Array.from(ctx.querySelectorAll(sel))
    };
  }

  /** 解析父级作用域上下文 */
  function resolveContext(p) {
    let ps = p.parentSelector;
    if (ps && ps.startsWith('xpath=')) ps = ps.substring(6);
    if (!ps) return document;
    const { element } = resolveElement(ps, document);
    return element || document;
  }

  /** 轮询等待，3 个 wait action 共用 */
  function poll(checkFn, timeout, interval) {
    return new Promise(resolve => {
      const start = Date.now();
      const check = () => {
        const result = checkFn();
        if (result.resolved) { resolve(result.value); return; }
        if (Date.now() - start > timeout) { resolve({ success: false, error: '等待超时' }); return; }
        setTimeout(check, interval);
      };
      check();
    });
  }

  /** 检查元素是否可见 */
  function isVisible(el) {
    if (!el) return false;
    const s = window.getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0'
      && el.offsetWidth > 0 && el.offsetHeight > 0;
  }

  // ========== 主逻辑 ==========

  try {
    // 剥离 "xpath=" 前缀
    let selector = params.selector;
    if (selector && selector.startsWith('xpath=')) selector = selector.substring(6);

    // 解析元素
    const context = resolveContext(params);
    let { element, elements } = resolveElement(selector, context);

    // 索引选择
    if (params.index !== undefined && params.index !== null) {
      element = elements[params.index] || null;
    }

    /** 要求元素存在，否则抛异常（被外层 try/catch 捕获） */
    function requireEl() {
      if (!element) throw new Error(`元素不存在: ${selector}`);
      return element;
    }

    // ========== 分发 ==========

    switch (action) {

      // ----- 元素交互 -----

      case 'click':
        requireEl().click();
        return { success: true };

      case 'input':
        { const el = requireEl();
          el.focus(); el.value = params.text;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true }; }

      case 'clear':
        { const el = requireEl();
          el.value = '';
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true }; }

      case 'hover':
        { const el = requireEl();
          el.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
          el.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
          return { success: true }; }

      case 'focus':
        requireEl().focus();
        return { success: true };

      case 'blur':
        requireEl().blur();
        return { success: true };

      case 'selectOption':
        { const el = requireEl();
          if (el.tagName.toLowerCase() !== 'select') return { success: false, error: '元素不是 select 标签' };
          el.value = params.value;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true }; }

      case 'check':
        { const el = requireEl();
          if (el.type !== 'checkbox' && el.type !== 'radio') return { success: false, error: '元素不是 checkbox 或 radio' };
          el.checked = true;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true }; }

      case 'uncheck':
        { const el = requireEl();
          if (el.type !== 'checkbox' && el.type !== 'radio') return { success: false, error: '元素不是 checkbox 或 radio' };
          el.checked = false;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true }; }

      // ----- 元素查询 -----

      case 'getText':
        return { success: true, data: requireEl().textContent || '' };

      case 'getHtml':
        return { success: true, data: requireEl().innerHTML || '' };

      case 'getOuterHtml':
        return { success: true, data: requireEl().outerHTML || '' };

      case 'getAttr':
        return { success: true, data: requireEl().getAttribute(params.attr) };

      case 'exists':
        return { success: true, data: element !== null };

      case 'isVisible':
        return { success: true, data: isVisible(element) };

      case 'getElements':
        return { success: true, data: elements.map(el => ({
          text: el.textContent || '', html: el.innerHTML || '', tagName: el.tagName.toLowerCase()
        })) };

      case 'getElementCount':
        return { success: true, data: elements.length };

      case 'scrollToElement':
        requireEl().scrollIntoView({ behavior: 'smooth', block: 'center' });
        return { success: true };

      case 'getElementRect':
        { const r = requireEl().getBoundingClientRect();
          return { success: true, data: {
            x: r.x, y: r.y, width: r.width, height: r.height,
            top: r.top, left: r.left, bottom: r.bottom, right: r.right
          }}; }

      case 'getElementParent':
        { const p = requireEl().parentElement;
          return { success: true, data: p
            ? { tagName: p.tagName.toLowerCase(), text: p.textContent || '', html: p.outerHTML }
            : null }; }

      case 'getElementChildren':
        return { success: true, data: Array.from(requireEl().children).map(c => ({
          tagName: c.tagName.toLowerCase(), text: c.textContent || '', html: c.outerHTML
        })) };

      case 'findByText':
        { const matches = [];
          for (const el of document.querySelectorAll('*')) {
            const t = el.textContent || '';
            const match = params.exact !== false ? t.trim() === params.text : t.includes(params.text);
            if (match && el.children.length === 0) {
              matches.push({ tagName: el.tagName.toLowerCase(), text: t.trim(), html: el.outerHTML });
            }
          }
          return { success: true, data: matches }; }

      case 'findByAttr':
        { const matches = [];
          for (const el of document.querySelectorAll(`[${params.attr}="${params.value}"]`)) {
            matches.push({ tagName: el.tagName.toLowerCase(), text: el.textContent || '', html: el.outerHTML });
          }
          return { success: true, data: matches }; }

      // ----- 键盘 -----

      case 'pressKey':
        { const el = requireEl();
          el.focus();
          const mkEvent = (type) => new KeyboardEvent(type, {
            key: params.key, code: params.code || params.key, bubbles: true,
            ctrlKey: (params.modifiers || []).includes('ctrl'),
            shiftKey: (params.modifiers || []).includes('shift'),
            altKey: (params.modifiers || []).includes('alt'),
            metaKey: (params.modifiers || []).includes('meta')
          });
          el.dispatchEvent(mkEvent('keydown'));
          el.dispatchEvent(mkEvent('keyup'));
          return { success: true }; }

      // ----- 等待 -----

      case 'waitForElement':
        return poll(() => {
          const { element: el } = resolveElement(selector, document);
          return el ? { resolved: true, value: { success: true, data: true } } : { resolved: false };
        }, params.timeout || 10000, params.interval || 100);

      case 'waitForElementVisible':
        return poll(() => {
          const { element: el } = resolveElement(selector, document);
          return el && isVisible(el) ? { resolved: true, value: { success: true, data: true } } : { resolved: false };
        }, params.timeout || 10000, params.interval || 100);

      case 'waitForElementHidden':
        return poll(() => {
          const { element: el } = resolveElement(selector, document);
          if (!el) return { resolved: true, value: { success: true, data: true } };
          const s = window.getComputedStyle(el);
          const hidden = s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0'
            || el.offsetWidth === 0 || el.offsetHeight === 0;
          return hidden ? { resolved: true, value: { success: true, data: true } } : { resolved: false };
        }, params.timeout || 10000, params.interval || 100);

      case 'waitForText':
        return poll(() => {
          const bodyText = document.body.innerText || document.body.textContent || '';
          return bodyText.includes(params.text)
            ? { resolved: true, value: { success: true, data: true } } : { resolved: false };
        }, params.timeout || 10000, params.interval || 100);

      // ----- 存储 -----

      case 'getCookies':
        return { success: true, data: document.cookie };

      case 'getCookie':
        { for (const c of document.cookie.split(';')) {
            const [n, v] = c.trim().split('=');
            if (n === params.name) return { success: true, data: decodeURIComponent(v || '') };
          }
          return { success: true, data: null }; }

      case 'setCookie':
        { let s = `${encodeURIComponent(params.name)}=${encodeURIComponent(params.value)}`;
          if (params.days) s += `; expires=${new Date(Date.now() + params.days * 864e5).toUTCString()}`;
          if (params.path) s += `; path=${params.path}`;
          if (params.domain) s += `; domain=${params.domain}`;
          document.cookie = s;
          return { success: true }; }

      case 'deleteCookie':
        document.cookie = `${encodeURIComponent(params.name)}=; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
        return { success: true };

      case 'getLocalStorage':
        { const k = params.key;
          if (k) return { success: true, data: localStorage.getItem(k) };
          const all = {};
          for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i); all[key] = localStorage.getItem(key);
          }
          return { success: true, data: all }; }

      case 'setLocalStorage':
        localStorage.setItem(params.key, params.value);
        return { success: true };

      case 'deleteLocalStorage':
        localStorage.removeItem(params.key);
        return { success: true };

      case 'getSessionStorage':
        { const k = params.key;
          if (k) return { success: true, data: sessionStorage.getItem(k) };
          const all = {};
          for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i); all[key] = sessionStorage.getItem(key);
          }
          return { success: true, data: all }; }

      case 'setSessionStorage':
        sessionStorage.setItem(params.key, params.value);
        return { success: true };

      case 'deleteSessionStorage':
        sessionStorage.removeItem(params.key);
        return { success: true };

      // ----- iframe -----

      case 'getIframes':
        return { success: true, data: Array.from(document.querySelectorAll('iframe')).map((f, i) => ({
          index: i, src: f.src || '', name: f.name || '', id: f.id || '',
          className: f.className || '', width: f.width || f.offsetWidth, height: f.height || f.offsetHeight
        })) };

      // ----- 拖拽 -----

      case 'drag':
        { const el = requireEl();
          const dx = params.deltaX || 100, dy = params.deltaY || 100;
          const r = el.getBoundingClientRect();
          const sx = r.left + r.width / 2, sy = r.top + r.height / 2;
          el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, clientX: sx, clientY: sy, button: 0 }));
          for (let i = 1; i <= 10; i++) {
            document.dispatchEvent(new MouseEvent('mousemove', {
              bubbles: true, clientX: sx + dx * i / 10, clientY: sy + dy * i / 10, button: 0
            }));
          }
          document.dispatchEvent(new MouseEvent('mouseup', {
            bubbles: true, clientX: sx + dx, clientY: sy + dy, button: 0
          }));
          return { success: true }; }

      case 'dragTo':
        { const el = requireEl();
          let toSel = params.to;
          if (toSel && toSel.startsWith('xpath=')) toSel = toSel.substring(6);
          const { element: target } = resolveElement(toSel, document);
          if (!target) return { success: false, error: `目标元素不存在: ${params.to}` };
          const fr = el.getBoundingClientRect(), tr = target.getBoundingClientRect();
          const sx = fr.left + fr.width / 2, sy = fr.top + fr.height / 2;
          const ex = tr.left + tr.width / 2, ey = tr.top + tr.height / 2;
          el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, clientX: sx, clientY: sy, button: 0 }));
          for (let i = 1; i <= 10; i++) {
            document.dispatchEvent(new MouseEvent('mousemove', {
              bubbles: true, clientX: sx + (ex - sx) * i / 10, clientY: sy + (ey - sy) * i / 10, button: 0
            }));
          }
          document.dispatchEvent(new MouseEvent('mouseup', {
            bubbles: true, clientX: ex, clientY: ey, button: 0
          }));
          return { success: true }; }

      // ----- 页面 -----

      case 'screenshot':
        return { success: true, data: {
          url: window.location.href, title: document.title,
          width: window.innerWidth, height: window.innerHeight,
          scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight,
          scrollX: window.scrollX, scrollY: window.scrollY
        } };

      case 'getPageHtml':
        return { success: true, data: document.documentElement.outerHTML };

      case 'getPageText':
        return { success: true, data: document.body.innerText || document.body.textContent };

      case 'getPageTitle':
        return { success: true, data: document.title };

      case 'getPageUrl':
        return { success: true, data: window.location.href };

      case 'scrollTo':
        window.scrollTo(params.x || 0, params.y || 0);
        return { success: true };

      case 'scrollBy':
        window.scrollBy(params.x || 0, params.y || 0);
        return { success: true };

      default:
        return { success: false, error: `未知 DOM 操作: ${action}` };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// ========== 独立函数 ==========

/**
 * 获取 iframe 内容（需要注入到 iframe 中）
 */
async function getIframeContent(tabId, params) {
  try {
    const { iframeSelector } = params;

    // 先找到 iframe 的 index
    const iframeResults = await chrome.scripting.executeScript({
      target: { tabId },
      func: (sel) => {
        let iframe = null;
        if (sel.startsWith('//') || sel.startsWith('(')) {
          const result = document.evaluate(sel, document, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          iframe = result.singleNodeValue;
        } else {
          iframe = document.querySelector(sel);
        }

        if (!iframe || iframe.tagName.toLowerCase() !== 'iframe') {
          return { success: false, error: `iframe 不存在: ${sel}` };
        }

        // 获取 iframe 在页面中的信息
        return {
          success: true,
          data: {
            src: iframe.src,
            name: iframe.name,
            id: iframe.id
          }
        };
      },
      args: [iframeSelector]
    });

    if (iframeResults && iframeResults[0]) {
      return iframeResults[0].result;
    }
    return { success: false, error: '获取 iframe 信息失败' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 截图
 */
async function takeScreenshot(tabId, params) {
  try {
    // 使用 Chrome API 截图
    const format = params.format || 'png';
    const quality = params.quality || 100;

    const dataUrl = await chrome.tabs.captureVisibleTab(null, {
      format: format,
      quality: quality
    });

    return {
      success: true,
      data: {
        dataUrl: dataUrl,
        format: format
      }
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 元素截图（通过 canvas 实现）
 */
async function screenshotElement(tabId, params) {
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: (sel) => {
        let element = null;
        if (sel.startsWith('//') || sel.startsWith('(')) {
          const result = document.evaluate(sel, document, null,
            XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          element = result.singleNodeValue;
        } else {
          element = document.querySelector(sel);
        }

        if (!element) {
          return { success: false, error: `元素不存在: ${sel}` };
        }

        const rect = element.getBoundingClientRect();
        return {
          success: true,
          data: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          }
        };
      },
      args: [params.selector]
    });

    if (results && results[0]) {
      return results[0].result;
    }
    return { success: false, error: '获取元素位置失败' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 监听来自 popup 的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'getStatus':
      sendResponse({ connected, port: currentPort });
      break;
    case 'connect':
      connectWebSocket(message.port);
      sendResponse({ success: true });
      break;
    case 'disconnect':
      disconnectWebSocket();
      sendResponse({ success: true });
      break;
    default:
      sendResponse({ error: '未知操作' });
  }
  return true; // 保持消息通道开放
});
