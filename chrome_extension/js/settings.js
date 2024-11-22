// settings.js
document.addEventListener("DOMContentLoaded", function () {
  const serverAddress = localStorage.getItem('serverAddress');
  if (serverAddress) {
    document.getElementById('server-address').value = serverAddress;
  }

  function saveSettings() {
    const serverAddress = document.getElementById('server-address').value;
    localStorage.setItem('serverAddress', serverAddress);
    alert('Server address saved successfully!');
  }

  const saveButton = document.getElementById('save-button');
  if (saveButton) {
    saveButton.addEventListener('click', saveSettings);
  }
});