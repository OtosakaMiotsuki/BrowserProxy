/**
 * BrowserProxy Chrome 扩展 - Content Script
 * 注入到目标页面，执行 DOM 操作
 */

// 监听来自 Service Worker 的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('收到消息:', message);

  // 这个文件主要是作为占位符
  // 实际的 DOM 操作通过 chrome.scripting.executeScript 执行
  // 这样可以避免 Content Script 的隔离问题

  sendResponse({ received: true });
});

// 通知 Service Worker 页面已加载
chrome.runtime.sendMessage({
  event: 'page_loaded',
  url: window.location.href,
  title: document.title
}).catch(() => {
  // 忽略错误，Service Worker 可能还未启动
});

console.log('BrowserProxy Content Script 已加载');
