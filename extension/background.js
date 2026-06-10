/**
 * BrowserProxy Chrome 扩展 - Service Worker
 * 维持 WebSocket 连接，接收 Python 脚本的指令
 */

// WebSocket 连接状态
let ws = null;
let connected = false;

// 标签页信息缓存
let tabsInfo = new Map();

/**
 * 初始化 WebSocket 连接
 */
function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log('WebSocket 已连接');
    return;
  }

  ws = new WebSocket('ws://localhost:8765');

  ws.onopen = () => {
    console.log('WebSocket 连接成功');
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
    // 尝试重连
    setTimeout(connectWebSocket, 3000);
  };

  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error);
    connected = false;
    updateBadge(false);
  };
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
      case 'list_tabs':
        result = await listTabs();
        break;

      case 'inject_content_script':
        result = await injectContentScript(tab_id);
        break;

      case 'click':
        result = await executeOnTab(tab_id, 'click', params);
        break;

      case 'input':
        result = await executeOnTab(tab_id, 'input', params);
        break;

      case 'get_text':
        result = await executeOnTab(tab_id, 'getText', params);
        break;

      case 'get_attr':
        result = await executeOnTab(tab_id, 'getAttr', params);
        break;

      case 'exists':
        result = await executeOnTab(tab_id, 'exists', params);
        break;

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

/**
 * 获取所有标签页
 */
async function listTabs() {
  const tabs = await chrome.tabs.query({});
  const tabsData = tabs.map(tab => ({
    id: tab.id,
    url: tab.url || '',
    title: tab.title || '',
    active: tab.active
  }));

  return { success: true, data: tabsData };
}

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
    let element;

    // 支持 CSS 和 XPath 选择器
    if (selector.startsWith('//') || selector.startsWith('(')) {
      const xpathResult = document.evaluate(
        selector,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
      );
      element = xpathResult.singleNodeValue;
    } else {
      element = document.querySelector(selector);
    }

    if (!element) {
      return { success: false, error: `元素不存在: ${selector}` };
    }

    switch (action) {
      case 'click':
        element.click();
        return { success: true };

      case 'input':
        element.value = params.text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        return { success: true };

      case 'getText':
        return { success: true, data: element.textContent || '' };

      case 'getAttr':
        return { success: true, data: element.getAttribute(params.attr) };

      case 'exists':
        return { success: true, data: true };

      default:
        return { success: false, error: `未知 DOM 操作: ${action}` };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

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

// 监听来自 popup 的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'getStatus':
      sendResponse({ connected });
      break;
    case 'connect':
      connectWebSocket();
      sendResponse({ success: true });
      break;
    case 'disconnect':
      if (ws) {
        ws.close();
        ws = null;
      }
      connected = false;
      updateBadge(false);
      sendResponse({ success: true });
      break;
    default:
      sendResponse({ error: '未知操作' });
  }
  return true; // 保持消息通道开放
});

// 启动时尝试连接
connectWebSocket();
