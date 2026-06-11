/**
 * BrowserProxy Chrome 扩展 - Service Worker
 * 连接到 Python 程序的 WebSocket 服务端
 */

// WebSocket 连接状态
let ws = null;
let connected = false;
let currentPort = 8765;

// 标签页信息缓存
let tabsInfo = new Map();

/**
 * 连接到 WebSocket 服务端
 */
function connectWebSocket(port = 8765) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log('WebSocket 已连接');
    return;
  }

  currentPort = port;

  ws = new WebSocket(`ws://localhost:${port}`);

  ws.onopen = () => {
    console.log(`WebSocket 连接成功: ws://localhost:${port}`);
    // 注册为扩展客户端
    ws.send(JSON.stringify({ type: 'register', client_type: 'extension' }));
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

      handleMessage(message);
    } catch (e) {
      console.error('解析消息失败:', e);
    }
  };

  ws.onclose = () => {
    console.log('WebSocket 连接关闭');
    connected = false;
    updateBadge(false);
  };

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
    connected = false;
    updateBadge(false);
  };
}

/**
 * 断开 WebSocket 连接
 */
function disconnectWebSocket() {
  if (ws) {
    ws.close();
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
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: (code) => {
        try {
          return { success: true, data: eval(code) };
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
