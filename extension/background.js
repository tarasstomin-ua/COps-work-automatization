/**
 * Background service worker for COps Weather Control extension.
 * Orchestrates the full Selenium-like automation flow:
 *   1. Opens admin panel tab
 *   2. Waits for jsoneditor to load (user must be logged in)
 *   3. Switches to Code mode
 *   4. Reads current settings → fetches target from GitHub → deep merges
 *   5. Writes merged JSON back → clicks Update
 *   6. Reports result back to dashboard
 */

let dashboardTabId = null;

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.type === 'cops-apply') {
    dashboardTabId = sender.tab?.id ?? null;
    handleApply(msg);
  }
});

async function handleApply({ city, profile, adminUrl, jsonUrl }) {
  const notify = (success, message) => {
    if (dashboardTabId) {
      chrome.tabs.sendMessage(dashboardTabId, {
        type: 'cops-result', city, profile, success, message,
      }).catch(() => {});
    }
  };

  let tab;
  try {
    tab = await chrome.tabs.create({ url: adminUrl, active: true });
    await waitForTabLoad(tab.id);
    await sleep(2000);

    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      world: 'MAIN',
      func: runAutomation,
      args: [jsonUrl],
    });

    const result = await pollForResult(tab.id, 120_000);

    notify(result.success, result.message);

    if (result.success) {
      await sleep(3000);
      try { chrome.tabs.remove(tab.id); } catch (_) {}
    }
  } catch (e) {
    notify(false, e.message || 'Extension error');
  }
}

function waitForTabLoad(tabId) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => {
      chrome.tabs.onUpdated.removeListener(listener);
      reject(new Error('Tab load timeout'));
    }, 30_000);

    function listener(id, info) {
      if (id === tabId && info.status === 'complete') {
        clearTimeout(timeout);
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
      }
    }
    chrome.tabs.onUpdated.addListener(listener);
  });
}

async function pollForResult(tabId, timeout) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const [frame] = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          const el = document.getElementById('cops-automation-result');
          return el ? el.textContent : null;
        },
      });
      if (frame?.result) return JSON.parse(frame.result);
    } catch (_) {}
    await sleep(2000);
  }
  return { success: false, message: 'Timeout — editor may not have loaded (are you logged in?)' };
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/**
 * Injected into the admin panel page in the MAIN world.
 * Has full access to `ace` editor and page DOM.
 */
function runAutomation(jsonUrl) {
  (async () => {
    const done = (success, message) => {
      let el = document.getElementById('cops-automation-result');
      if (!el) {
        el = document.createElement('div');
        el.id = 'cops-automation-result';
        el.style.display = 'none';
        document.body.appendChild(el);
      }
      el.textContent = JSON.stringify({ success, message });
    };

    try {
      // 1. Wait for jsoneditor to appear (up to 90 s — time for login if needed)
      let found = false;
      for (let i = 0; i < 90; i++) {
        if (document.querySelector('.jsoneditor')) { found = true; break; }
        await new Promise(r => setTimeout(r, 1000));
      }
      if (!found) { done(false, 'JSON editor not found — are you logged in to Bolt Admin Panel?'); return; }

      await new Promise(r => setTimeout(r, 1000));

      // 2. Switch to Code mode
      const modesBtn = document.querySelector('button.jsoneditor-modes');
      if (modesBtn) {
        modesBtn.click();
        await new Promise(r => setTimeout(r, 400));
        const items = document.querySelectorAll('.jsoneditor-type-modes div, .jsoneditor-type-modes button');
        for (const item of items) {
          if (item.textContent.trim() === 'Code') { item.click(); break; }
        }
        await new Promise(r => setTimeout(r, 800));
      }

      // 3. Read current settings from ace editor
      const aceEl = document.querySelector('.ace_editor');
      if (!aceEl) { done(false, 'Ace editor element not found'); return; }
      /* global ace */
      const editor = ace.edit(aceEl);
      const current = JSON.parse(editor.getValue());

      // 4. Fetch target settings from GitHub
      const resp = await fetch(jsonUrl);
      if (!resp.ok) { done(false, 'Failed to fetch target JSON: HTTP ' + resp.status); return; }
      const target = await resp.json();

      // 5. Deep merge target into current (preserves admin-panel-only fields)
      function merge(dst, src) {
        for (const key of Object.keys(src)) {
          if (src[key] && typeof src[key] === 'object' && !Array.isArray(src[key])) {
            if (!dst[key] || typeof dst[key] !== 'object') dst[key] = {};
            merge(dst[key], src[key]);
          } else {
            dst[key] = src[key];
          }
        }
        return dst;
      }
      merge(current, target);

      // 6. Write merged settings back to editor
      editor.setValue(JSON.stringify(current, null, 2), -1);
      await new Promise(r => setTimeout(r, 500));

      // 7. Click Update
      const updateBtn = [...document.querySelectorAll('button')]
        .find(b => b.textContent.trim() === 'Update');
      if (updateBtn) {
        updateBtn.click();
        done(true, 'Settings applied and Update clicked');
      } else {
        done(false, 'Update button not found — please click it manually');
      }
    } catch (e) {
      done(false, 'Automation error: ' + (e.message || String(e)));
    }
  })();
}
