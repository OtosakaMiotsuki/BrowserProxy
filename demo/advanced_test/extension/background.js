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
    // 使用 Function 构造器代替 eval，避免 CSP 限制
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: (code) => {
        try {
          // 将用户代码包装在函数中执行
          const fn = new Function('return ' + code);
          return { success: true, data: fn() };
        } catch (e) {
          return { success: false, error: e.message };
        }
      },
      args: [script]
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
    const results = await chrome.scripting.executeScript({
      target: { tabId },
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
 */
function executeDOMAction(action, params) {
  const { selector } = params;

  try {
    // 查找元素
    let element = null;
    let elements = [];

    if (selector) {
      // 支持 CSS 和 XPath 选择器
      if (selector.startsWith('//') || selector.startsWith('(')) {
        const xpathResult = document.evaluate(
          selector,
          document,
          null,
          XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
          null
        );
        for (let i = 0; i < xpathResult.snapshotLength; i++) {
          elements.push(xpathResult.snapshotItem(i));
        }
        element = elements[0] || null;
      } else {
        element = document.querySelector(selector);
        elements = Array.from(document.querySelectorAll(selector));
      }
    }

    // ========== DOM 操作 ==========

    switch (action) {
      case 'click':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.click();
        return { success: true };

      case 'input':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.focus();
        element.value = params.text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return { success: true };

      case 'getText':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        return { success: true, data: element.textContent || '' };

      case 'getHtml':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        return { success: true, data: element.innerHTML || '' };

      case 'getOuterHtml':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        return { success: true, data: element.outerHTML || '' };

      case 'getAttr':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        return { success: true, data: element.getAttribute(params.attr) };

      case 'exists':
        return { success: true, data: element !== null };

      case 'isVisible':
        if (!element) return { success: true, data: false };
        const style = window.getComputedStyle(element);
        return {
          success: true,
          data: style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'
        };

      case 'getElements':
        return {
          success: true,
          data: elements.map(el => ({
            text: el.textContent || '',
            html: el.innerHTML || '',
            tagName: el.tagName.toLowerCase()
          }))
        };

      case 'getElementCount':
        return { success: true, data: elements.length };

      case 'scrollToElement':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return { success: true };

      case 'getElementRect':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        const rect = element.getBoundingClientRect();
        return {
          success: true,
          data: {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height,
            top: rect.top,
            left: rect.left,
            bottom: rect.bottom,
            right: rect.right
          }
        };

      case 'hover':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        const mouseEnterEvent = new MouseEvent('mouseenter', { bubbles: true });
        const mouseOverEvent = new MouseEvent('mouseover', { bubbles: true });
        element.dispatchEvent(mouseEnterEvent);
        element.dispatchEvent(mouseOverEvent);
        return { success: true };

      case 'focus':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.focus();
        return { success: true };

      case 'blur':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.blur();
        return { success: true };

      case 'selectOption':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        if (element.tagName.toLowerCase() === 'select') {
          element.value = params.value;
          element.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true };
        }
        return { success: false, error: '元素不是 select 标签' };

      case 'check':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        if (element.type === 'checkbox' || element.type === 'radio') {
          element.checked = true;
          element.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true };
        }
        return { success: false, error: '元素不是 checkbox 或 radio' };

      case 'uncheck':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        if (element.type === 'checkbox' || element.type === 'radio') {
          element.checked = false;
          element.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true };
        }
        return { success: false, error: '元素不是 checkbox 或 radio' };

      case 'clear':
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.value = '';
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return { success: true };

      case 'waitForElement':
        // 等待元素出现
        return new Promise((resolve) => {
          const timeout = params.timeout || 10000;
          const interval = params.interval || 100;
          const startTime = Date.now();

          const checkElement = () => {
            let el = null;
            if (selector.startsWith('//') || selector.startsWith('(')) {
              const result = document.evaluate(
                selector, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null
              );
              el = result.singleNodeValue;
            } else {
              el = document.querySelector(selector);
            }

            if (el) {
              resolve({ success: true, data: true });
            } else if (Date.now() - startTime > timeout) {
              resolve({ success: false, error: '等待元素超时' });
            } else {
              setTimeout(checkElement, interval);
            }
          };

          checkElement();
        });

      case 'waitForElementVisible':
        // 等待元素可见
        return new Promise((resolve) => {
          const timeout = params.timeout || 10000;
          const interval = params.interval || 100;
          const startTime = Date.now();

          const checkVisible = () => {
            let el = null;
            if (selector.startsWith('//') || selector.startsWith('(')) {
              const result = document.evaluate(
                selector, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null
              );
              el = result.singleNodeValue;
            } else {
              el = document.querySelector(selector);
            }

            if (el) {
              const style = window.getComputedStyle(el);
              const isVisible = style.display !== 'none' &&
                               style.visibility !== 'hidden' &&
                               style.opacity !== '0' &&
                               el.offsetWidth > 0 &&
                               el.offsetHeight > 0;

              if (isVisible) {
                resolve({ success: true, data: true });
                return;
              }
            }

            if (Date.now() - startTime > timeout) {
              resolve({ success: false, error: '等待元素可见超时' });
            } else {
              setTimeout(checkVisible, interval);
            }
          };

          checkVisible();
        });

      case 'waitForElementHidden':
        // 等待元素消失
        return new Promise((resolve) => {
          const timeout = params.timeout || 10000;
          const interval = params.interval || 100;
          const startTime = Date.now();

          const checkHidden = () => {
            let el = null;
            if (selector.startsWith('//') || selector.startsWith('(')) {
              const result = document.evaluate(
                selector, document, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null
              );
              el = result.singleNodeValue;
            } else {
              el = document.querySelector(selector);
            }

            if (!el) {
              resolve({ success: true, data: true });
              return;
            }

            const style = window.getComputedStyle(el);
            const isHidden = style.display === 'none' ||
                            style.visibility === 'hidden' ||
                            style.opacity === '0' ||
                            el.offsetWidth === 0 ||
                            el.offsetHeight === 0;

            if (isHidden) {
              resolve({ success: true, data: true });
            } else if (Date.now() - startTime > timeout) {
              resolve({ success: false, error: '等待元素消失超时' });
            } else {
              setTimeout(checkHidden, interval);
            }
          };

          checkHidden();
        });

      case 'waitForText':
        // 等待页面包含指定文本
        return new Promise((resolve) => {
          const timeout = params.timeout || 10000;
          const interval = params.interval || 100;
          const startTime = Date.now();
          const text = params.text;

          const checkText = () => {
            const bodyText = document.body.innerText || document.body.textContent || '';
            if (bodyText.includes(text)) {
              resolve({ success: true, data: true });
            } else if (Date.now() - startTime > timeout) {
              resolve({ success: false, error: `等待文本 "${text}" 超时` });
            } else {
              setTimeout(checkText, interval);
            }
          };

          checkText();
        });

      // ========== 高级元素查找 ==========

      case 'findByText':
        // 按文本查找元素
        {
          const textToFind = params.text;
          const exact = params.exact !== false;
          const allElements = document.querySelectorAll('*');
          const matches = [];

          for (const el of allElements) {
            const elText = el.textContent || '';
            const match = exact ? elText.trim() === textToFind : elText.includes(textToFind);
            if (match && el.children.length === 0) { // 叶子节点
              matches.push({
                tagName: el.tagName.toLowerCase(),
                text: elText.trim(),
                html: el.outerHTML
              });
            }
          }

          return { success: true, data: matches };
        }

      case 'findByAttr':
        // 按属性查找元素
        {
          const attrName = params.attr;
          const attrValue = params.value;
          const selector = `[${attrName}="${attrValue}"]`;
          const elements = document.querySelectorAll(selector);
          const matches = [];

          for (const el of elements) {
            matches.push({
              tagName: el.tagName.toLowerCase(),
              text: el.textContent || '',
              html: el.outerHTML
            });
          }

          return { success: true, data: matches };
        }

      case 'getElementParent':
        // 获取父元素
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        {
          const parent = element.parentElement;
          if (parent) {
            return {
              success: true,
              data: {
                tagName: parent.tagName.toLowerCase(),
                text: parent.textContent || '',
                html: parent.outerHTML
              }
            };
          }
          return { success: true, data: null };
        }

      case 'getElementChildren':
        // 获取子元素
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        {
          const children = Array.from(element.children);
          return {
            success: true,
            data: children.map(child => ({
              tagName: child.tagName.toLowerCase(),
              text: child.textContent || '',
              html: child.outerHTML
            }))
          };
        }

      // ========== 键盘操作 ==========

      case 'pressKey':
        // 按下按键
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        element.focus();
        {
          const key = params.key;
          const modifiers = params.modifiers || [];

          // 创建键盘事件
          const keyDownEvent = new KeyboardEvent('keydown', {
            key: key,
            code: params.code || key,
            bubbles: true,
            ctrlKey: modifiers.includes('ctrl'),
            shiftKey: modifiers.includes('shift'),
            altKey: modifiers.includes('alt'),
            metaKey: modifiers.includes('meta')
          });

          const keyUpEvent = new KeyboardEvent('keyup', {
            key: key,
            code: params.code || key,
            bubbles: true,
            ctrlKey: modifiers.includes('ctrl'),
            shiftKey: modifiers.includes('shift'),
            altKey: modifiers.includes('alt'),
            metaKey: modifiers.includes('meta')
          });

          element.dispatchEvent(keyDownEvent);
          element.dispatchEvent(keyUpEvent);
          return { success: true };
        }

      // ========== Cookie / Storage 操作 ==========

      case 'getCookies':
        // 获取所有 Cookie
        return { success: true, data: document.cookie };

      case 'getCookie':
        // 获取指定 Cookie
        {
          const cookieName = params.name;
          const cookies = document.cookie.split(';');
          for (const cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === cookieName) {
              return { success: true, data: decodeURIComponent(value || '') };
            }
          }
          return { success: true, data: null };
        }

      case 'setCookie':
        // 设置 Cookie
        {
          const { name, value, days, path, domain } = params;
          let cookieStr = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
          if (days) {
            const expires = new Date(Date.now() + days * 864e5).toUTCString();
            cookieStr += `; expires=${expires}`;
          }
          if (path) cookieStr += `; path=${path}`;
          if (domain) cookieStr += `; domain=${domain}`;
          document.cookie = cookieStr;
          return { success: true };
        }

      case 'deleteCookie':
        // 删除 Cookie
        {
          const cookieName = params.name;
          document.cookie = `${encodeURIComponent(cookieName)}=; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
          return { success: true };
        }

      case 'getLocalStorage':
        // 获取 localStorage
        {
          const key = params.key;
          if (key) {
            const value = localStorage.getItem(key);
            return { success: true, data: value };
          }
          // 获取所有
          const all = {};
          for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            all[k] = localStorage.getItem(k);
          }
          return { success: true, data: all };
        }

      case 'setLocalStorage':
        // 设置 localStorage
        {
          localStorage.setItem(params.key, params.value);
          return { success: true };
        }

      case 'deleteLocalStorage':
        // 删除 localStorage
        {
          localStorage.removeItem(params.key);
          return { success: true };
        }

      case 'getSessionStorage':
        // 获取 sessionStorage
        {
          const key = params.key;
          if (key) {
            const value = sessionStorage.getItem(key);
            return { success: true, data: value };
          }
          const all = {};
          for (let i = 0; i < sessionStorage.length; i++) {
            const k = sessionStorage.key(i);
            all[k] = sessionStorage.getItem(k);
          }
          return { success: true, data: all };
        }

      case 'setSessionStorage':
        // 设置 sessionStorage
        {
          sessionStorage.setItem(params.key, params.value);
          return { success: true };
        }

      case 'deleteSessionStorage':
        // 删除 sessionStorage
        {
          sessionStorage.removeItem(params.key);
          return { success: true };
        }

      // ========== iframe 操作 ==========

      case 'getIframes':
        // 获取所有 iframe
        {
          const iframes = document.querySelectorAll('iframe');
          const iframeList = Array.from(iframes).map((iframe, index) => ({
            index: index,
            src: iframe.src || '',
            name: iframe.name || '',
            id: iframe.id || '',
            className: iframe.className || '',
            width: iframe.width || iframe.offsetWidth,
            height: iframe.height || iframe.offsetHeight
          }));
          return { success: true, data: iframeList };
        }

      // ========== 拖拽 ==========

      case 'drag':
        // 拖拽元素
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        {
          const deltaX = params.deltaX || 100;
          const deltaY = params.deltaY || 100;

          const rect = element.getBoundingClientRect();
          const startX = rect.left + rect.width / 2;
          const startY = rect.top + rect.height / 2;

          // 触发 mousedown
          element.dispatchEvent(new MouseEvent('mousedown', {
            bubbles: true, clientX: startX, clientY: startY, button: 0
          }));

          // 模拟拖动过程
          const steps = 10;
          for (let i = 1; i <= steps; i++) {
            const currentX = startX + (deltaX * i / steps);
            const currentY = startY + (deltaY * i / steps);

            document.dispatchEvent(new MouseEvent('mousemove', {
              bubbles: true, clientX: currentX, clientY: currentY, button: 0
            }));
          }

          // 触发 mouseup
          document.dispatchEvent(new MouseEvent('mouseup', {
            bubbles: true, clientX: startX + deltaX, clientY: startY + deltaY, button: 0
          }));

          return { success: true };
        }

      case 'dragTo':
        // 拖拽元素到目标位置
        if (!element) return { success: false, error: `元素不存在: ${selector}` };
        {
          const toSelector = params.to;
          let targetElement = null;

          if (toSelector.startsWith('//') || toSelector.startsWith('(')) {
            const result = document.evaluate(toSelector, document, null,
              XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            targetElement = result.singleNodeValue;
          } else {
            targetElement = document.querySelector(toSelector);
          }

          if (!targetElement) return { success: false, error: `目标元素不存在: ${toSelector}` };

          const fromRect = element.getBoundingClientRect();
          const toRect = targetElement.getBoundingClientRect();

          const startX = fromRect.left + fromRect.width / 2;
          const startY = fromRect.top + fromRect.height / 2;
          const endX = toRect.left + toRect.width / 2;
          const endY = toRect.top + toRect.height / 2;

          // 触发 mousedown
          element.dispatchEvent(new MouseEvent('mousedown', {
            bubbles: true, clientX: startX, clientY: startY, button: 0
          }));

          // 模拟拖动过程
          const steps = 10;
          for (let i = 1; i <= steps; i++) {
            const currentX = startX + ((endX - startX) * i / steps);
            const currentY = startY + ((endY - startY) * i / steps);
            document.dispatchEvent(new MouseEvent('mousemove', {
              bubbles: true, clientX: currentX, clientY: currentY, button: 0
            }));
          }

          // 触发 mouseup
          document.dispatchEvent(new MouseEvent('mouseup', {
            bubbles: true, clientX: endX, clientY: endY, button: 0
          }));

          return { success: true };
        }

      // ========== 截图 ==========

      case 'screenshot':
        // 返回截图所需的信息，实际截图通过 chrome.tabs.captureVisibleTab
        return {
          success: true,
          data: {
            url: window.location.href,
            title: document.title,
            width: window.innerWidth,
            height: window.innerHeight,
            scrollWidth: document.documentElement.scrollWidth,
            scrollHeight: document.documentElement.scrollHeight,
            scrollX: window.scrollX,
            scrollY: window.scrollY
          }
        };

      // ========== 页面操作 ==========

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
