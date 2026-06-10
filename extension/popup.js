/**
 * BrowserProxy Chrome 扩展 - Popup 脚本
 */

const statusEl = document.getElementById('status');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

// 获取背景页的连接状态
async function updateStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
    if (response && response.connected) {
      statusEl.textContent = '已连接';
      statusEl.className = 'status connected';
      connectBtn.disabled = true;
      disconnectBtn.disabled = false;
    } else {
      statusEl.textContent = '未连接';
      statusEl.className = 'status disconnected';
      connectBtn.disabled = false;
      disconnectBtn.disabled = true;
    }
  } catch (e) {
    statusEl.textContent = '未连接';
    statusEl.className = 'status disconnected';
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
  }
}

// 连接按钮点击事件
connectBtn.addEventListener('click', async () => {
  try {
    await chrome.runtime.sendMessage({ action: 'connect' });
    updateStatus();
  } catch (e) {
    console.error('连接失败:', e);
  }
});

// 断开按钮点击事件
disconnectBtn.addEventListener('click', async () => {
  try {
    await chrome.runtime.sendMessage({ action: 'disconnect' });
    updateStatus();
  } catch (e) {
    console.error('断开失败:', e);
  }
});

// 初始化状态
updateStatus();
