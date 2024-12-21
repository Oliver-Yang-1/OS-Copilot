// navigation.js
document.addEventListener("DOMContentLoaded", function () {
  const backButton = document.getElementById('back-button');
  if (backButton) {
    backButton.addEventListener('click', function () {
      const urlParams = new URLSearchParams(window.location.search);
      const tabUrl = urlParams.get('tabUrl');
      window.location.href = './popup.html' + (tabUrl ? '?tabUrl=' + encodeURIComponent(tabUrl) : '');
    });
  }
});