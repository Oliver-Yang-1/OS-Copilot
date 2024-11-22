// injectSidebar.js

const SIDEBAR_WIDTH = 400; // 设置侧边栏宽度

// 检查侧边栏是否已存在
if (!document.getElementById('web-copilot-sidebar')) {
  // 创建侧边栏容器
  const sidebarContainer = document.createElement('div');
  sidebarContainer.id = 'web-copilot-sidebar';
  sidebarContainer.style.position = 'fixed';
  sidebarContainer.style.top = '0';
  sidebarContainer.style.right = '0';
  sidebarContainer.style.width = '0';
  sidebarContainer.style.height = '100vh';
  sidebarContainer.style.zIndex = '999999';
  sidebarContainer.style.transition = 'width 0.3s ease-in-out';
  sidebarContainer.style.overflow = 'hidden';
  sidebarContainer.style.borderRadius = '12px'; // 全部四个角增加圆角
  sidebarContainer.style.backgroundColor = '#ffffff'; // 背景颜色
  sidebarContainer.style.boxShadow = '-4px 0 8px rgba(0, 0, 0, 0.1)'; // 添加阴影

  // 创建 iframe 加载 Copilot 页面
  const iframe = document.createElement('iframe');
  iframe.src = chrome.runtime.getURL('html/popup.html') + '?tabUrl=' + encodeURIComponent(window.location.href);
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  iframe.style.border = 'none';
  iframe.style.borderRadius = '12px'; // 保持 iframe 圆角一致

  // 将 iframe 添加到侧边栏容器
  sidebarContainer.appendChild(iframe);
  document.body.appendChild(sidebarContainer);

  // 动态调整页面宽度
  document.body.style.transition = 'margin-right 0.3s ease-in-out';
  document.body.style.marginRight = `${SIDEBAR_WIDTH}px`;

  // 展开侧边栏
  requestAnimationFrame(() => {
    sidebarContainer.style.width = `${SIDEBAR_WIDTH}px`;
  });

  // 监听 iframe 中的关闭事件
  window.addEventListener('message', function (event) {
    if (event.data && event.data.action === 'closeSidebar') {
      // 收回侧边栏
      sidebarContainer.style.width = '0';
      document.body.style.marginRight = '0'; // 恢复页面宽度
      sidebarContainer.addEventListener('transitionend', () => {
        sidebarContainer.remove();
      }, { once: true });
    }
  });
} else {
  // 收回侧边栏
  const sidebarContainer = document.getElementById('web-copilot-sidebar');
  sidebarContainer.style.width = '0';
  document.body.style.marginRight = '0'; // 恢复页面宽度

  // 删除侧边栏元素
  sidebarContainer.addEventListener('transitionend', () => {
    sidebarContainer.remove();
  }, { once: true });
}