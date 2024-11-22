// popup.js
document.addEventListener("DOMContentLoaded", function () {
  function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  }

  const tagName = getQueryParam('tabUrl');

  const settingsButton = document.querySelector("#settings-button");
  if (settingsButton) {
    settingsButton.addEventListener("click", function () {
      window.location.href = './settings.html?tabUrl=' + encodeURIComponent(tagName);
    });
  }

  const closeButton = document.getElementById('close-button');
  if (closeButton) {
    closeButton.addEventListener('click', function () {
      parent.postMessage({ action: 'closeSidebar' }, '*');
    });
  }

  let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || {};

  const chatArea = document.getElementById('chat-area');
  const userInput = document.querySelector("input[type='text']");
  const sendButton = document.querySelector(".send-button");

  if (chatHistory[tagName]) {
    chatHistory[tagName].forEach(entry => {
      const [sender, message] = entry;
      const messageDiv = document.createElement('div');
      messageDiv.className = `chat-message ${sender}`;
      messageDiv.textContent = message;
      chatArea.appendChild(messageDiv);
    });
  }

  function getPageHTML() {
    return new Promise((resolve, reject) => {
      window.addEventListener('message', function handler(event) {
        if (event.data && event.data.action === 'pageHTML') {
          resolve(event.data.htmlContent);
          window.removeEventListener('message', handler);
        }
      });
      parent.postMessage({ action: 'getPageHTML' }, '*');
    });
  }

  if (sendButton) {
    sendButton.addEventListener("click", async function () {
      if (!userInput || !userInput.value) {
        alert("Please enter a task.");
        return;
      }

      const serverAddress = localStorage.getItem('serverAddress');
      if (!serverAddress) {
        alert("Server address not set. Please go to settings to configure.");
        return;
      }

      const userOrder = userInput.value;

      const userMessageDiv = document.createElement('div');
      userMessageDiv.className = 'chat-message user';
      userMessageDiv.textContent = userOrder;
      chatArea.appendChild(userMessageDiv);

      if (!chatHistory[tagName]) {
        chatHistory[tagName] = [];
      }
      chatHistory[tagName].push(['user', userOrder]);

      try {
        const htmlContent = await getPageHTML();
        const containHtml = true;

        const formData = new FormData();
        formData.append("contain_html", containHtml);
        formData.append("html_file", new Blob([htmlContent], { type: "text/html" }));
        formData.append("userOrder", userOrder);

        const apiResponse = await fetch(`${serverAddress}/process-task`, {
          method: "POST",
          body: formData,
        });

        if (apiResponse.ok) {
          const result = await apiResponse.json();
          const systemMessageDiv = document.createElement('div');
          systemMessageDiv.className = 'chat-message system';
          systemMessageDiv.textContent = result.response;
          chatArea.appendChild(systemMessageDiv);

          chatHistory[tagName].push(['system', result.response]);
          localStorage.setItem('chatHistory', JSON.stringify(chatHistory));

          if (result.script) {
            parent.postMessage({ action: 'executeScript', script: result.script }, '*');
          }
        } else {
          const error = await apiResponse.json();
          const errorMessageDiv = document.createElement('div');
          errorMessageDiv.className = 'chat-message system';
          errorMessageDiv.textContent = `Error: ${error.error}`;
          chatArea.appendChild(errorMessageDiv);

          chatHistory[tagName].push(['system', `Error: ${error.error}`]);
          localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
        }
      } catch (error) {
        const connectionErrorDiv = document.createElement('div');
        connectionErrorDiv.className = 'chat-message system';
        connectionErrorDiv.textContent = "Failed to connect to the server. Please check your server address and internet connection.";
        chatArea.appendChild(connectionErrorDiv);

        chatHistory[tagName].push(['system', "Failed to connect to the server. Please check your server address and internet connection."]);
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
      }

      userInput.value = "";
    });
  }
});