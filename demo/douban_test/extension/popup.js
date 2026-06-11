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

// 轮询检查连接状态
let pollInterval = null;

function startPolling() {
  if (pollInterval) return;
  pollInterval = setInterval(updateStatus, 500); // 每500ms检查一次
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
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
    // 更新状态为连接中
    statusEl.textContent = '连接中...';
    statusEl.className = 'status disconnected';
    connectBtn.disabled = true;

    // 发送连接请求
    await chrome.runtime.sendMessage({ action: 'connect', port: port });

    // 开始轮询检查状态
    startPolling();

    // 5秒后停止轮询（如果还没连上就是失败了）
    setTimeout(() => {
      stopPolling();
      updateStatus();
    }, 5000);

  } catch (e) {
    console.error('连接失败:', e);
    updateStatus();
  }
});

// 断开按钮点击事件
disconnectBtn.addEventListener('click', async () => {
  try {
    await chrome.runtime.sendMessage({ action: 'disconnect' });
    stopPolling();
    updateStatus();
  } catch (e) {
    console.error('断开失败:', e);
  }
});

// 初始化状态
updateStatus();
