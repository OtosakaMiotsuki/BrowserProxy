/**
 * BrowserProxy Chrome 扩展 - Popup 脚本
 */

const statusEl = document.getElementById('status');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const portInput = document.getElementById('portInput');

// 获取背景页的连接状态
async function updateStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getStatus' });
    if (response && response.connected) {
      statusEl.textContent = `已连接 (端口: ${response.port})`;
      statusEl.className = 'status connected';
      connectBtn.disabled = true;
      disconnectBtn.disabled = false;
      portInput.disabled = true;
    } else {
      statusEl.textContent = '未连接';
      statusEl.className = 'status disconnected';
      connectBtn.disabled = false;
      disconnectBtn.disabled = true;
      portInput.disabled = false;
    }
  } catch (e) {
    statusEl.textContent = '未连接';
    statusEl.className = 'status disconnected';
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
    portInput.disabled = false;
  }
}

// 连接按钮点击事件
connectBtn.addEventListener('click', async () => {
  const port = parseInt(portInput.value);
  if (isNaN(port) || port < 1024 || port > 65535) {
    alert('请输入有效的端口号 (1024-65535)');
    return;
  }

  try {
    await chrome.runtime.sendMessage({ action: 'connect', port: port });
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
