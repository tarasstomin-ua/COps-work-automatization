/**
 * Bridge between the dashboard page and the Chrome extension.
 * Runs as a content script on the GitHub Pages dashboard.
 * Relays messages in both directions via window.postMessage ↔ chrome.runtime.
 */

window.addEventListener('message', (e) => {
  if (e.source !== window) return;
  if (e.data?.type === 'cops-apply') {
    chrome.runtime.sendMessage(e.data);
  }
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === 'cops-result') {
    window.postMessage(msg, '*');
  }
});

window.postMessage({ type: 'cops-extension-ready' }, '*');
