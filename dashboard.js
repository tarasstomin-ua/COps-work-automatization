(function() {
  'use strict';

  if (document.getElementById('cops-dashboard-overlay')) {
    document.getElementById('cops-dashboard-overlay').remove();
    return;
  }

  const OWNER = 'tarasstomin-ua';
  const REPO = 'COps-work-automatization';
  const REPO_RAW = `https://raw.githubusercontent.com/${OWNER}/${REPO}/main/Bad%20weather%20settings`;
  const STATUS_URL = `https://raw.githubusercontent.com/${OWNER}/${REPO}/main/status.json`;
  const GH_API = 'https://api.github.com';

  const USERS = [
    {email: 'taras.stomin@bolt.eu', name: 'Taras Stomin'},
    {email: 'anna.tiurina@bolt.eu', name: 'Anna Tiurina'},
    {email: 'nataliia.malakova@bolt.eu', name: 'Nataliia Malakova'}
  ];

  const CITIES = {
    "Kyiv":{g:"TOP",o:0,id:158,base:"Kyiv",p:["good","bad","harsh"],jn:"Kyiv"},
    "Lviv":{g:"TOP",o:0,id:496,base:"Lviv",p:["good","bad","harsh"],jn:"Lviv"},
    "Dnipro":{g:"TOP",o:0,id:499,base:"Dnipro",p:["good","bad","harsh"],jn:"Dnipro"},
    "Kharkiv":{g:"TOP",o:0,id:491,base:"Kharkiv",p:["good","bad","harsh"],jn:"Kharkiv"},
    "Vinnytsia":{g:"TOP",o:0,id:501,base:"Vinnytsia",p:["good","bad","harsh"],jn:"Vinnytsia"},
    "Odesa":{g:"Tier 2",o:1,id:498,base:"Secondary%20cities/Tier2%20cities/Odesa",p:["good","harsh"],jn:"Odesa"},
    "Kryvyi Rih":{g:"Tier 2",o:1,id:504,base:"Secondary%20cities/Tier2%20cities/Kryvyi%20Rih",p:["good","harsh"],jn:"Kryvyi Rih"},
    "Poltava":{g:"Tier 2",o:1,id:506,base:"Secondary%20cities/Tier2%20cities/Poltava",p:["good","harsh"],jn:"Poltava"},
    "Ivano-Frankivsk":{g:"Tier 2",o:1,id:990,base:"Secondary%20cities/Tier2%20cities/Ivano-Frankivsk",p:["good","harsh"],jn:"Ivano-Frankivsk"},
    "Chernivtsi":{g:"Tier 2",o:1,id:1084,base:"Secondary%20cities/Tier2%20cities/Chernivtsi",p:["good","harsh"],jn:"Chernivtsi"},
    "Irpin":{g:"Tier 2",o:1,id:1261,base:"Secondary%20cities/Tier2%20cities/Irpin",p:["good","harsh"],jn:"Irpin"},
    "Cherkasy":{g:"Tier 2",o:1,id:1087,base:"Secondary%20cities/Tier2%20cities/Cherkasy",p:["good","harsh"],jn:"Cherkasy"},
    "Zaporizhia":{g:"Tier 3",o:2,id:500,base:"Secondary%20cities/Tier3%20cities/Zaporizhia",p:["good","harsh"],jn:"Zaporizhia"},
    "Bila Tserkva":{g:"Tier 3",o:2,id:1079,base:"Secondary%20cities/Tier3%20cities/Bila%20Tserkva",p:["good","harsh"],jn:"Bila Tserkva"},
    "Khmelnytskyi":{g:"Tier 3",o:2,id:1081,base:"Secondary%20cities/Tier3%20cities/Khmelnytskyi",p:["good","harsh"],jn:"Khmelnytskyi"},
    "Rivne":{g:"Tier 3",o:2,id:1086,base:"Secondary%20cities/Tier3%20cities/Rivne",p:["good","harsh"],jn:"Rivne"},
    "Uzhhorod":{g:"Tier 3",o:2,id:1131,base:"Secondary%20cities/Tier3%20cities/Uzhhorod",p:["good","harsh"],jn:"Uzhhorod"},
    "Brovary":{g:"Tier 3",o:2,id:1259,base:"Secondary%20cities/Tier3%20cities/Brovary",p:["good","harsh"],jn:"Brovary"},
    "Zhytomyr":{g:"Tier 3",o:2,id:1083,base:"Secondary%20cities/Tier3%20cities/Zhytomyr",p:["good","harsh"],jn:"Zhytomyr"},
    "Mykolaiv":{g:"Rest",o:3,id:503,base:"Secondary%20cities/Rest%20of%20the%20cities/Mykolaiv",p:["good","harsh"],jn:"Mykolaiv"},
    "Chernihiv":{g:"Rest",o:3,id:1076,base:"Secondary%20cities/Rest%20of%20the%20cities/Chenihiv",p:["good","harsh"],jn:"Chernihiv"},
    "Sumy":{g:"Rest",o:3,id:1078,base:"Secondary%20cities/Rest%20of%20the%20cities/Sumy",p:["good","harsh"],jn:"Sumy"},
    "Ternopil":{g:"Rest",o:3,id:1080,base:"Secondary%20cities/Rest%20of%20the%20cities/Ternopil",p:["good","harsh"],jn:"Ternopil"},
    "Lutsk":{g:"Rest",o:3,id:1082,base:"Secondary%20cities/Rest%20of%20the%20cities/Lutsk",p:["good","harsh"],jn:"Lutsk"},
    "Kropyvnytskyi":{g:"Rest",o:3,id:1085,base:"Secondary%20cities/Rest%20of%20the%20cities/Kropyvnytskyi",p:["good","harsh"],jn:"Kropyvnytskyi"},
    "Kremenchuk":{g:"Rest",o:3,id:1088,base:"Secondary%20cities/Rest%20of%20the%20cities/Kremenchuk",p:["good","harsh"],jn:"Kremenchuk"},
    "Kamianets-Podilskyi":{g:"Rest",o:3,id:1132,base:"Secondary%20cities/Rest%20of%20the%20cities/Kamianets-Podilskyi",p:["good","harsh"],jn:"Kamianets-Podilskyi"},
    "Pavlohrad":{g:"Rest",o:3,id:1176,base:"Secondary%20cities/Rest%20of%20the%20cities/Pavlohrad",p:["good","harsh"],jn:"Pavlohrad"},
    "Kamianske":{g:"Rest",o:3,id:1178,base:"Secondary%20cities/Rest%20of%20the%20cities/Kamianske",p:["good","harsh"],jn:"Kamianske"},
    "Mukachevo":{g:"Rest",o:3,id:1179,base:"Secondary%20cities/Rest%20of%20the%20cities/Mukachevo",p:["good","harsh"],jn:"Mukachevo"},
    "Boryspil":{g:"Rest",o:3,id:1220,base:"Secondary%20cities/Rest%20of%20the%20cities/Boryspil",p:["good","harsh"],jn:"Boryspil"},
    "Vyshhorod":{g:"Rest",o:3,id:1262,base:"Secondary%20cities/Rest%20of%20the%20cities/Vyshhorod",p:["good","harsh"],jn:"Vyshhorod"},
    "Drohobych":{g:"Rest",o:3,id:1348,base:"Secondary%20cities/Rest%20of%20the%20cities/Drohobych",p:["good","harsh"],jn:"Drohobych"},
    "Truskavets":{g:"Rest",o:3,id:1357,base:"Secondary%20cities/Rest%20of%20the%20cities/Truskavets",p:["good","harsh"],jn:"Truskavets"},
    "Kovel":{g:"Rest",o:3,id:2170,base:"Secondary%20cities/Rest%20of%20the%20cities/Kovel",p:["good","harsh"],jn:"Kovel"},
    "Oleksandriia":{g:"Rest",o:3,id:2171,base:"Secondary%20cities/Rest%20of%20the%20cities/Oleksandriia",p:["good","harsh"],jn:"Oleksandriia"},
    "Kolomyia":{g:"Rest",o:3,id:2499,base:"Secondary%20cities/Rest%20of%20the%20cities/Kolomyia",p:["good","harsh"],jn:"Kolomyia"}
  };

  const PM = {
    good: {f:'Good%20weather', px:'Good%20Weather%20Settings'},
    bad:  {f:'Bad%20weather',  px:'Bad%20Weather%20Settings'},
    harsh:{f:'Harsh%20weather',px:'Harsh%20Weather%20Settings'}
  };

  const PL = {good:'Good',bad:'Bad',harsh:'Harsh'};
  const PF = {good:'Good Weather',bad:'Bad Weather',harsh:'Harsh Weather'};
  const LS_STATUS = 'cops_dash_status';
  const LS_USER = 'cops_dash_user';
  const LS_PAT = 'cops_gh_pat';

  function loadStatus() { try { return JSON.parse(localStorage.getItem(LS_STATUS)) || {}; } catch(e) { return {}; } }
  function saveStatus(s) { localStorage.setItem(LS_STATUS, JSON.stringify(s)); }
  function getUser() { return localStorage.getItem(LS_USER) || ''; }
  function getPat() { return localStorage.getItem(LS_PAT) || ''; }
  function savePat(v) { localStorage.setItem(LS_PAT, v.trim()); }

  async function setStatus(city, profile, user) {
    const s = loadStatus();
    s[city] = {profile, user, timestamp: new Date().toISOString()};
    if (!s._history) s._history = [];
    s._history.unshift({city, profile, user, timestamp: new Date().toISOString()});
    if (s._history.length > 200) s._history = s._history.slice(0, 200);
    saveStatus(s);
    await pushStatusToGitHub(s);
  }

  async function pushStatusToGitHub(localStatus) {
    const pat = getPat();
    if (!pat) return;
    try {
      const fileResp = await fetch(`${GH_API}/repos/${OWNER}/${REPO}/contents/status.json`, {
        headers: {'Authorization': 'Bearer ' + pat, 'Accept': 'application/vnd.github+json'}
      });
      let sha = null;
      let remote = {cities: {}, history: [], last_updated: null};
      if (fileResp.ok) {
        const fileData = await fileResp.json();
        sha = fileData.sha;
        try { remote = JSON.parse(atob(fileData.content)); } catch(e) {}
      }
      for (const [city, info] of Object.entries(localStatus)) {
        if (city === '_history') continue;
        remote.cities = remote.cities || {};
        remote.cities[city] = info;
      }
      remote.history = remote.history || [];
      const localHist = localStatus._history || [];
      for (const h of localHist) {
        if (!remote.history.find(rh => rh.city === h.city && rh.timestamp === h.timestamp)) {
          remote.history.unshift(h);
        }
      }
      remote.history.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
      remote.history = remote.history.slice(0, 300);
      remote.last_updated = new Date().toISOString();
      const content = btoa(unescape(encodeURIComponent(JSON.stringify(remote, null, 2))));
      const body = {message: `Status update: ${new Date().toISOString()}`, content};
      if (sha) body.sha = sha;
      await fetch(`${GH_API}/repos/${OWNER}/${REPO}/contents/status.json`, {
        method: 'PUT',
        headers: {'Authorization': 'Bearer ' + pat, 'Content-Type': 'application/json', 'Accept': 'application/vnd.github+json'},
        body: JSON.stringify(body)
      });
    } catch(e) {
      console.warn('COps: Failed to push status to GitHub:', e);
    }
  }

  function timeAgo(iso) {
    if (!iso) return '';
    const ms = Date.now() - new Date(iso).getTime();
    if (ms < 0) return 'just now';
    const m = Math.floor(ms/60000), h = Math.floor(m/60), d = Math.floor(h/24);
    if (m < 1) return 'just now';
    if (m < 60) return m + 'm ago';
    if (h < 24) return h + 'h ' + (m%60) + 'm ago';
    return d + 'd ago';
  }

  function getJsonUrl(name, profile) {
    const c = CITIES[name], m = PM[profile];
    return `${REPO_RAW}/${c.base}/${m.f}/${m.px}%20${encodeURIComponent(c.jn)}.json`;
  }

  let busy = false;
  let autoWin = null;

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  function waitForEl(doc, sel, timeout = 60000) {
    return new Promise((resolve, reject) => {
      const t = setTimeout(() => { clearInterval(iv); reject(new Error('Timeout: ' + sel)); }, timeout);
      const iv = setInterval(() => {
        try {
          const el = doc.querySelector(sel);
          if (el) { clearInterval(iv); clearTimeout(t); resolve(el); }
        } catch(e) { clearInterval(iv); clearTimeout(t); reject(e); }
      }, 300);
    });
  }

  async function applySettings(cityName, profile) {
    const user = getUser();
    if (!user) { showLog('Select your name first!', 'error'); return; }
    if (busy) { showLog('Another task is running...', 'warn'); return; }

    busy = true;
    const city = CITIES[cityName];
    const url = `/delivery-courier/settings/city/${city.id}`;
    updateCardState(cityName, 'working', `Applying ${PF[profile]}...`);

    try {
      showLog(`Fetching ${PF[profile]} settings for ${cityName}...`);
      const targetResp = await fetch(getJsonUrl(cityName, profile));
      if (!targetResp.ok) throw new Error('Failed to fetch target settings from GitHub');
      const target = await targetResp.json();

      showLog(`Opening ${cityName} settings page...`);
      if (autoWin && !autoWin.closed) {
        autoWin.location.href = 'https://admin-panel.bolt.eu' + url;
      } else {
        autoWin = window.open('https://admin-panel.bolt.eu' + url, 'cops_auto', 'width=1200,height=800');
      }
      if (!autoWin) throw new Error('Popup blocked! Allow popups for admin-panel.bolt.eu');

      showLog('Waiting for JSON editor to load...');
      await waitForEl(autoWin.document, '.jsoneditor', 90000);
      await sleep(1500);

      showLog('Switching to Code mode...');
      const modesBtn = autoWin.document.querySelector('button.jsoneditor-modes');
      if (modesBtn) {
        modesBtn.click();
        await sleep(400);
        const items = autoWin.document.querySelectorAll('.jsoneditor-type-modes div, .jsoneditor-type-modes button');
        for (const item of items) {
          if (item.textContent.trim() === 'Code') { item.click(); break; }
        }
        await sleep(800);
      }

      showLog('Reading current settings...');
      const aceEl = autoWin.document.querySelector('.ace_editor');
      const editor = autoWin.ace.edit(aceEl);
      const current = JSON.parse(editor.getValue());

      showLog(`Merging settings (${Object.keys(target).length} keys)...`);
      deepMerge(current, target);
      editor.setValue(JSON.stringify(current, null, 2), -1);
      await sleep(500);

      showLog('Clicking Update...');
      const btns = autoWin.document.querySelectorAll('button');
      let clicked = false;
      for (const btn of btns) {
        if (btn.textContent.trim() === 'Update') { btn.click(); clicked = true; break; }
      }
      if (!clicked) throw new Error('Update button not found');

      await sleep(3000);
      await setStatus(cityName, profile, user);
      updateCardState(cityName, 'success', `${PF[profile]} applied!`);
      showLog(`${cityName} -> ${PF[profile]} applied by ${user}`, 'success');
      renderOverview();
      renderHistory(loadStatus()._history || []);

    } catch(e) {
      updateCardState(cityName, 'error', e.message);
      showLog(`ERROR: ${e.message}`, 'error');
    } finally {
      busy = false;
    }
  }

  function deepMerge(dst, src) {
    for (const k of Object.keys(src)) {
      if (src[k] && typeof src[k] === 'object' && !Array.isArray(src[k])) {
        if (!dst[k] || typeof dst[k] !== 'object') dst[k] = {};
        deepMerge(dst[k], src[k]);
      } else {
        dst[k] = src[k];
      }
    }
  }

  // ── UI ──────────────────────────────────────────────────────────────────────

  const style = document.createElement('style');
  style.textContent = `
    #cops-dashboard-overlay{position:fixed;inset:0;z-index:999999;background:#080a0f;overflow-y:auto;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:13px;color:#d1d5db}
    #cops-dashboard-overlay *{box-sizing:border-box;margin:0;padding:0}
    .cd-hdr{background:#0f1218;border-bottom:1px solid #1c2230;padding:14px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10;flex-wrap:wrap;gap:10px}
    .cd-hdr h1{font-size:16px;font-weight:700;color:#f0f2f5;letter-spacing:-.3px}
    .cd-hdr .sub{font-size:11px;color:#5c6370;text-transform:uppercase;letter-spacing:.8px;font-weight:500;margin-left:14px}
    .cd-hdr-r{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
    .cd-sel{background:#080a0f;border:1px solid #1c2230;border-radius:20px;padding:4px 12px;display:flex;align-items:center;gap:6px}
    .cd-sel label{font-size:10px;color:#5c6370;text-transform:uppercase;letter-spacing:.5px}
    .cd-sel select{background:none;border:none;color:#f0f2f5;font-size:12px;font-weight:600;outline:none;cursor:pointer}
    .cd-sel select option{background:#0f1218;color:#f0f2f5}
    .cd-pat{background:#080a0f;border:1px solid #1c2230;border-radius:20px;padding:4px 12px;display:flex;align-items:center;gap:6px}
    .cd-pat label{font-size:10px;color:#5c6370;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
    .cd-pat input{background:none;border:none;color:#f0f2f5;font-size:11px;font-weight:600;width:140px;outline:none;font-family:monospace}
    .cd-pat input::placeholder{color:#3d4452;font-family:inherit}
    .cd-pat .ok{color:#10b981;font-size:12px;display:none}
    .cd-pat.valid .ok{display:inline}
    .cd-close{background:none;border:1px solid #252d3b;border-radius:8px;color:#5c6370;font-size:14px;padding:6px 14px;cursor:pointer;font-weight:600}
    .cd-close:hover{background:#151a22;color:#f0f2f5}
    .cd-hist{background:#0f1218;border:1px solid #1c2230;border-radius:12px;padding:14px 18px;margin-bottom:16px}
    .cd-hist h3{font-size:12px;font-weight:600;color:#f0f2f5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px;cursor:pointer;user-select:none}
    .cd-hist-list{max-height:200px;overflow-y:auto}
    .cd-hist-item{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid #1c2230;font-size:11px}
    .cd-hist-item:last-child{border-bottom:none}
    .cd-hist-item .h-city{font-weight:600;color:#f0f2f5;min-width:100px}
    .cd-hist-item .h-prof{font-weight:500;min-width:80px}
    .cd-hist-item .h-prof.good{color:#10b981}.cd-hist-item .h-prof.bad{color:#f59e0b}.cd-hist-item .h-prof.harsh{color:#ef4444}
    .cd-hist-item .h-user{color:#3b82f6;min-width:100px}
    .cd-hist-item .h-time{color:#5c6370;font-size:10px;font-family:monospace}
    .cd-main{max-width:1500px;margin:0 auto;padding:20px 28px 40px}
    .cd-ov{background:#0f1218;border:1px solid #1c2230;border-radius:12px;padding:14px 18px;margin-bottom:16px}
    .cd-ov h3{font-size:12px;font-weight:600;color:#f0f2f5;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px}
    .cd-pills{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px}
    .cd-pill{display:inline-flex;align-items:center;gap:5px;padding:4px 8px;border-radius:5px;background:#080a0f;border:1px solid #1c2230;font-size:10px}
    .cd-pill .dot{width:6px;height:6px;border-radius:50%}
    .cd-pill .dot.good{background:#10b981}.cd-pill .dot.bad{background:#f59e0b}.cd-pill .dot.harsh{background:#ef4444}.cd-pill .dot.none{background:#3d4452}
    .cd-pill .pn{font-weight:600;color:#f0f2f5}.cd-pill .pp{font-weight:500}
    .cd-pill .pp.good{color:#10b981}.cd-pill .pp.bad{color:#f59e0b}.cd-pill .pp.harsh{color:#ef4444}.cd-pill .pp.none{color:#5c6370}
    .cd-pill .pm{color:#5c6370;font-size:9px}
    .cd-sec{margin-bottom:16px;background:#0f1218;border:1px solid #1c2230;border-radius:12px;overflow:hidden}
    .cd-sec-h{display:flex;align-items:center;gap:10px;padding:10px 16px;cursor:pointer;user-select:none}
    .cd-sec-h:hover{background:#151a22}
    .cd-sec-h h2{font-size:12px;font-weight:600;color:#f0f2f5;text-transform:uppercase;letter-spacing:.5px}
    .cd-sec-h .cnt{font-size:10px;color:#5c6370;background:#080a0f;padding:2px 8px;border-radius:10px;font-weight:600;margin-left:auto}
    .cd-sec.closed .cd-sec-b{display:none}
    .cd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;padding:0 16px 14px}
    .cd-card{background:#080a0f;border:1px solid #1c2230;border-radius:8px;padding:12px;transition:border-color .15s}
    .cd-card:hover{border-color:#252d3b}
    .cd-card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px}
    .cd-card .cn{font-size:13px;font-weight:600;color:#f0f2f5}
    .cd-card .cst{font-size:10px;color:#5c6370;margin-bottom:8px;min-height:16px;display:flex;align-items:center;gap:5px}
    .cd-card .cst .cs-p{font-weight:500}.cd-card .cst .cs-p.good{color:#10b981}.cd-card .cst .cs-p.bad{color:#f59e0b}.cd-card .cst .cs-p.harsh{color:#ef4444}
    .cd-card .cst .cs-u{color:#3b82f6}
    .cd-btns{display:flex;gap:5px}
    .cd-btn{flex:1;padding:8px 0;border:none;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;color:#fff;letter-spacing:.2px;transition:all .12s}
    .cd-btn:disabled{opacity:.35;cursor:not-allowed}
    .cd-btn.good{background:#10b981}.cd-btn.good:hover:not(:disabled){background:#34d399}
    .cd-btn.bad{background:#f59e0b;color:#1a1a2e}.cd-btn.bad:hover:not(:disabled){background:#fbbf24}
    .cd-btn.harsh{background:#ef4444}.cd-btn.harsh:hover:not(:disabled){background:#f87171}
    .cd-btn.active{box-shadow:0 0 0 2px #f0f2f5;transform:scale(1.02)}
    .cd-card.working{border-color:#3b82f6}
    .cd-card .cd-prog{display:none;margin-top:6px;padding:6px;background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:5px;font-size:10px;color:#3b82f6;text-align:center}
    .cd-card.working .cd-prog{display:block}
    .cd-card.success .cd-prog{display:block;background:rgba(16,185,129,.08);border-color:rgba(16,185,129,.2);color:#10b981}
    .cd-card.error .cd-prog{display:block;background:rgba(239,68,68,.08);border-color:rgba(239,68,68,.2);color:#ef4444}
    .cd-log{position:fixed;bottom:16px;right:16px;z-index:1000000;display:flex;flex-direction:column;gap:5px;max-width:420px}
    .cd-log-item{padding:8px 14px;border-radius:8px;font-size:11px;font-weight:500;animation:cdsi .2s ease;box-shadow:0 4px 20px rgba(0,0,0,.4)}
    .cd-log-item.info{background:#3b82f6;color:#fff}
    .cd-log-item.success{background:#10b981;color:#fff}
    .cd-log-item.error{background:#ef4444;color:#fff}
    .cd-log-item.warn{background:#f59e0b;color:#1a1a2e}
    .cd-search{display:flex;align-items:center;gap:10px;margin-bottom:16px;background:#0f1218;border:1px solid #1c2230;border-radius:8px;padding:8px 14px}
    .cd-search input{flex:1;background:none;border:none;color:#f0f2f5;font-size:13px;outline:none}
    .cd-search input::placeholder{color:#3d4452}
    @keyframes cdsi{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
    @media(max-width:640px){.cd-grid{grid-template-columns:1fr}.cd-hdr{padding:10px 16px}.cd-main{padding:12px 16px 30px}}
  `;
  document.head.appendChild(style);

  const overlay = document.createElement('div');
  overlay.id = 'cops-dashboard-overlay';
  document.body.appendChild(overlay);

  const logContainer = document.createElement('div');
  logContainer.className = 'cd-log';
  logContainer.id = 'cops-log';
  document.body.appendChild(logContainer);

  function showLog(msg, type = 'info') {
    const el = document.createElement('div');
    el.className = 'cd-log-item ' + type;
    el.textContent = msg;
    logContainer.appendChild(el);
    setTimeout(() => el.remove(), type === 'error' ? 10000 : 5000);
  }

  function buildGroups() {
    const g = {};
    for (const [n, c] of Object.entries(CITIES)) {
      if (!g[c.g]) g[c.g] = {o: c.o, cities: []};
      g[c.g].cities.push(n);
    }
    return Object.entries(g).sort((a,b) => a[1].o - b[1].o);
  }

  function renderOverview() {
    const status = loadStatus();
    const groups = buildGroups();
    const el = document.getElementById('cops-overview');
    if (!el) return;
    let tracked = 0;
    el.innerHTML = '<h3>Active Weather Status</h3>' + groups.map(([gn, gd]) => {
      const pills = gd.cities.map(cn => {
        const s = status[cn];
        const prof = s?.profile || 'none';
        const lbl = s ? PL[prof] : '\u2014';
        const meta = s ? `<span class="pm">${s.user.split('@')[0]} \u00b7 ${timeAgo(s.timestamp)}</span>` : '';
        if (s) tracked++;
        return `<span class="cd-pill"><span class="dot ${prof}"></span><span class="pn">${cn}</span><span class="pp ${prof}">${lbl}</span>${meta}</span>`;
      }).join('');
      return `<div style="margin-bottom:8px"><div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:#5c6370;margin-bottom:4px">${gn} \u00b7 ${gd.cities.length}</div><div class="cd-pills">${pills}</div></div>`;
    }).join('');
    const cntEl = document.getElementById('cops-tracked-cnt');
    if (cntEl) cntEl.textContent = tracked;
  }

  function updateCardState(cityName, state, msg) {
    const cid = 'cops-card-' + cityName.replace(/[^a-zA-Z0-9]/g, '_');
    const card = document.getElementById(cid);
    if (!card) return;
    card.classList.remove('working', 'success', 'error');
    if (state) card.classList.add(state);
    const prog = card.querySelector('.cd-prog');
    if (prog) prog.textContent = msg || '';
    if (state === 'success') setTimeout(() => { card.classList.remove('success'); renderCards(); }, 5000);
    if (state === 'error') setTimeout(() => { card.classList.remove('error'); }, 10000);
  }

  function renderCards(filter) {
    const groups = buildGroups();
    const status = loadStatus();
    const wrap = document.getElementById('cops-cities');
    if (!wrap) return;
    const fl = (filter || '').toLowerCase();

    wrap.innerHTML = groups.map(([gn, gd], i) => {
      const cities = fl ? gd.cities.filter(c => c.toLowerCase().includes(fl)) : gd.cities;
      if (!cities.length) return '';
      const cards = cities.map(cn => {
        const c = CITIES[cn];
        const s = status[cn];
        const cid = 'cops-card-' + cn.replace(/[^a-zA-Z0-9]/g, '_');
        let stHtml = '<div class="cst" style="color:#3d4452">No profile set</div>';
        if (s) stHtml = `<div class="cst"><span class="dot ${s.profile}" style="width:6px;height:6px;border-radius:50%"></span><span class="cs-p ${s.profile}">${PF[s.profile]}</span><span>\u00b7</span><span class="cs-u">${s.user.split('@')[0]}</span><span>\u00b7</span><span style="font-size:9px">${timeAgo(s.timestamp)}</span></div>`;
        const btns = c.p.map(p => {
          const active = s?.profile === p ? ' active' : '';
          return `<button class="cd-btn ${p}${active}" onclick="window.__copsApply('${cn}','${p}')">${PL[p]}</button>`;
        }).join('');
        return `<div class="cd-card" id="${cid}"><div class="cd-card-top"><span class="cn">${cn}</span></div>${stHtml}<div class="cd-btns">${btns}</div><div class="cd-prog"></div></div>`;
      }).join('');
      const closed = i > 0 && !fl ? ' closed' : '';
      return `<div class="cd-sec${closed}" id="cops-sec-${i}"><div class="cd-sec-h" onclick="this.parentElement.classList.toggle('closed')"><span style="font-size:10px;color:#5c6370;width:14px;text-align:center">\u25BE</span><h2>${gn}</h2><span class="cnt">${cities.length}</span></div><div class="cd-sec-b"><div class="cd-grid">${cards}</div></div></div>`;
    }).join('');
  }

  window.__copsApply = function(city, profile) { applySettings(city, profile); };

  const userOpts = USERS.map(u => `<option value="${u.email}" ${getUser() === u.email ? 'selected' : ''}>${u.name}</option>`).join('');
  const savedPat = getPat();
  const patValid = savedPat.startsWith('ghp_') || savedPat.startsWith('github_pat_');

  overlay.innerHTML = `
    <div class="cd-hdr">
      <div style="display:flex;align-items:center">
        <h1>COps Weather Control</h1>
        <span class="sub">Bookmarklet Dashboard</span>
      </div>
      <div class="cd-hdr-r">
        <div class="cd-sel">
          <label>You:</label>
          <select id="cops-user" onchange="localStorage.setItem('cops_dash_user',this.value)">
            <option value="">-- select --</option>
            ${userOpts}
          </select>
        </div>
        <div class="cd-pat${patValid ? ' valid' : ''}" id="cops-pat-group">
          <label>Token:</label>
          <input type="password" id="cops-pat" placeholder="ghp_xxx..." value="${savedPat}" oninput="window.__copsSavePat(this.value)">
          <span class="ok" title="Token set — status will be shared">&#10003;</span>
        </div>
        <div style="text-align:center"><div style="font-size:18px;font-weight:700;color:#f0f2f5" id="cops-tracked-cnt">0</div><div style="font-size:9px;color:#5c6370;text-transform:uppercase;letter-spacing:.6px">Tracked</div></div>
        <button class="cd-close" onclick="document.getElementById('cops-dashboard-overlay').remove();document.getElementById('cops-log').remove()">Close Dashboard</button>
      </div>
    </div>
    <div class="cd-main">
      <div class="cd-ov" id="cops-overview"></div>
      <div class="cd-hist" id="cops-history" style="display:none">
        <h3 onclick="document.getElementById('cops-hist-list').style.display=document.getElementById('cops-hist-list').style.display==='none'?'block':'none'">Recent Changes \u25BE</h3>
        <div class="cd-hist-list" id="cops-hist-list"></div>
      </div>
      <div class="cd-search"><span style="color:#5c6370;font-size:14px">\uD83D\uDD0D</span><input type="text" placeholder="Search cities..." oninput="window.__copsFilter(this.value)"></div>
      <div id="cops-cities"></div>
    </div>
  `;

  window.__copsSavePat = function(v) {
    savePat(v);
    const g = document.getElementById('cops-pat-group');
    if (g) g.classList.toggle('valid', v.trim().startsWith('ghp_') || v.trim().startsWith('github_pat_'));
  };

  window.__copsFilter = function(val) { renderCards(val); };

  function renderHistory(history) {
    const wrap = document.getElementById('cops-history');
    const list = document.getElementById('cops-hist-list');
    if (!wrap || !list || !history || !history.length) return;
    wrap.style.display = 'block';
    list.innerHTML = history.slice(0, 50).map(h => {
      const prof = h.profile || 'none';
      const userName = (h.user || '').split('@')[0] || '?';
      const time = h.timestamp ? new Date(h.timestamp).toLocaleString('uk-UA', {day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}) : '';
      return `<div class="cd-hist-item"><span class="h-city">${h.city}</span><span class="h-prof ${prof}">${PF[prof] || prof}</span><span class="h-user">${userName}</span><span class="h-time">${time}</span></div>`;
    }).join('');
  }

  renderOverview();
  renderCards();

  fetch(STATUS_URL + '?t=' + Date.now()).then(r => r.ok ? r.json() : null).then(data => {
    if (data) {
      const local = loadStatus();
      if (data.cities) {
        for (const [city, info] of Object.entries(data.cities)) {
          if (!local[city] || new Date(info.timestamp) > new Date(local[city].timestamp)) {
            local[city] = info;
          }
        }
      }
      if (data.history) {
        local._history = local._history || [];
        for (const h of data.history) {
          if (!local._history.find(lh => lh.city === h.city && lh.timestamp === h.timestamp)) {
            local._history.push(h);
          }
        }
        local._history.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
        local._history = local._history.slice(0, 300);
      }
      saveStatus(local);
      renderOverview();
      renderCards();
      renderHistory(local._history || data.history || []);
    }
  }).catch(() => {});

  showLog(getPat()
    ? 'Dashboard loaded! Status is shared via GitHub.'
    : 'Dashboard loaded! Add a GitHub token (header) to share status with your team.',
    'success');
})();
