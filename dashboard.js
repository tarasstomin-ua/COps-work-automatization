(function() {
  'use strict';

  if (document.getElementById('cops-overlay')) {
    document.getElementById('cops-overlay').remove();
    document.getElementById('cops-log')?.remove();
    return;
  }

  const OWNER = 'tarasstomin-ua', REPO = 'COps-work-automatization';
  const RAW = `https://raw.githubusercontent.com/${OWNER}/${REPO}/main/Bad%20weather%20settings`;
  const STATUS_URL = `https://raw.githubusercontent.com/${OWNER}/${REPO}/main/status.json`;
  const GH_API = 'https://api.github.com';

  const USERS = [
    {email:'taras.stomin@bolt.eu', name:'Taras Stomin'},
    {email:'anna.tiurina@bolt.eu', name:'Anna Tiurina'},
    {email:'nataliia.malakova@bolt.eu', name:'Nataliia Malakova'}
  ];

  const CITIES = {
    "Kyiv":{g:"TOP",o:0,id:158,base:"Kyiv",p:["good","bad","harsh"],jn:"Kyiv",icon:"\u{1F3D9}"},
    "Lviv":{g:"TOP",o:0,id:496,base:"Lviv",p:["good","bad","harsh"],jn:"Lviv",icon:"\u{1F3F0}"},
    "Dnipro":{g:"TOP",o:0,id:499,base:"Dnipro",p:["good","bad","harsh"],jn:"Dnipro",icon:"\u{1F30A}"},
    "Kharkiv":{g:"TOP",o:0,id:491,base:"Kharkiv",p:["good","bad","harsh"],jn:"Kharkiv",icon:"\u{1F3ED}"},
    "Vinnytsia":{g:"TOP",o:0,id:501,base:"Vinnytsia",p:["good","bad","harsh"],jn:"Vinnytsia",icon:"\u{1F333}"},
    "Odesa":{g:"Tier 2",o:1,id:498,base:"Secondary%20cities/Tier2%20cities/Odesa",p:["good","harsh"],jn:"Odesa",icon:"\u{26F5}"},
    "Kryvyi Rih":{g:"Tier 2",o:1,id:504,base:"Secondary%20cities/Tier2%20cities/Kryvyi%20Rih",p:["good","harsh"],jn:"Kryvyi Rih",icon:"\u{26CF}"},
    "Poltava":{g:"Tier 2",o:1,id:506,base:"Secondary%20cities/Tier2%20cities/Poltava",p:["good","harsh"],jn:"Poltava",icon:"\u{1F33B}"},
    "Ivano-Frankivsk":{g:"Tier 2",o:1,id:990,base:"Secondary%20cities/Tier2%20cities/Ivano-Frankivsk",p:["good","harsh"],jn:"Ivano-Frankivsk",icon:"\u{26F0}"},
    "Chernivtsi":{g:"Tier 2",o:1,id:1084,base:"Secondary%20cities/Tier2%20cities/Chernivtsi",p:["good","harsh"],jn:"Chernivtsi",icon:"\u{1F3DB}"},
    "Irpin":{g:"Tier 2",o:1,id:1261,base:"Secondary%20cities/Tier2%20cities/Irpin",p:["good","harsh"],jn:"Irpin",icon:"\u{1F3E1}"},
    "Cherkasy":{g:"Tier 2",o:1,id:1087,base:"Secondary%20cities/Tier2%20cities/Cherkasy",p:["good","harsh"],jn:"Cherkasy",icon:"\u{1F3DE}"},
    "Zaporizhia":{g:"Tier 3",o:2,id:500,base:"Secondary%20cities/Tier3%20cities/Zaporizhia",p:["good","harsh"],jn:"Zaporizhia",icon:"\u{26A1}"},
    "Bila Tserkva":{g:"Tier 3",o:2,id:1079,base:"Secondary%20cities/Tier3%20cities/Bila%20Tserkva",p:["good","harsh"],jn:"Bila Tserkva",icon:"\u{26EA}"},
    "Khmelnytskyi":{g:"Tier 3",o:2,id:1081,base:"Secondary%20cities/Tier3%20cities/Khmelnytskyi",p:["good","harsh"],jn:"Khmelnytskyi",icon:"\u{1F3F5}"},
    "Rivne":{g:"Tier 3",o:2,id:1086,base:"Secondary%20cities/Tier3%20cities/Rivne",p:["good","harsh"],jn:"Rivne",icon:"\u{1F4A7}"},
    "Uzhhorod":{g:"Tier 3",o:2,id:1131,base:"Secondary%20cities/Tier3%20cities/Uzhhorod",p:["good","harsh"],jn:"Uzhhorod",icon:"\u{1F3F0}"},
    "Brovary":{g:"Tier 3",o:2,id:1259,base:"Secondary%20cities/Tier3%20cities/Brovary",p:["good","harsh"],jn:"Brovary",icon:"\u{1F3E2}"},
    "Zhytomyr":{g:"Tier 3",o:2,id:1083,base:"Secondary%20cities/Tier3%20cities/Zhytomyr",p:["good","harsh"],jn:"Zhytomyr",icon:"\u{1F332}"},
    "Mykolaiv":{g:"Rest",o:3,id:503,base:"Secondary%20cities/Rest%20of%20the%20cities/Mykolaiv",p:["good","harsh"],jn:"Mykolaiv",icon:"\u{2693}"},
    "Chernihiv":{g:"Rest",o:3,id:1076,base:"Secondary%20cities/Rest%20of%20the%20cities/Chenihiv",p:["good","harsh"],jn:"Chernihiv",icon:"\u{1F3F0}"},
    "Sumy":{g:"Rest",o:3,id:1078,base:"Secondary%20cities/Rest%20of%20the%20cities/Sumy",p:["good","harsh"],jn:"Sumy",icon:"\u{1F33F}"},
    "Ternopil":{g:"Rest",o:3,id:1080,base:"Secondary%20cities/Rest%20of%20the%20cities/Ternopil",p:["good","harsh"],jn:"Ternopil",icon:"\u{1F3DE}"},
    "Lutsk":{g:"Rest",o:3,id:1082,base:"Secondary%20cities/Rest%20of%20the%20cities/Lutsk",p:["good","harsh"],jn:"Lutsk",icon:"\u{1F3F0}"},
    "Kropyvnytskyi":{g:"Rest",o:3,id:1085,base:"Secondary%20cities/Rest%20of%20the%20cities/Kropyvnytskyi",p:["good","harsh"],jn:"Kropyvnytskyi",icon:"\u{1F33E}"},
    "Kremenchuk":{g:"Rest",o:3,id:1088,base:"Secondary%20cities/Rest%20of%20the%20cities/Kremenchuk",p:["good","harsh"],jn:"Kremenchuk",icon:"\u{1F3ED}"},
    "Kamianets-Podilskyi":{g:"Rest",o:3,id:1132,base:"Secondary%20cities/Rest%20of%20the%20cities/Kamianets-Podilskyi",p:["good","harsh"],jn:"Kamianets-Podilskyi",icon:"\u{1F3F0}"},
    "Pavlohrad":{g:"Rest",o:3,id:1176,base:"Secondary%20cities/Rest%20of%20the%20cities/Pavlohrad",p:["good","harsh"],jn:"Pavlohrad",icon:"\u{1F3D8}"},
    "Kamianske":{g:"Rest",o:3,id:1178,base:"Secondary%20cities/Rest%20of%20the%20cities/Kamianske",p:["good","harsh"],jn:"Kamianske",icon:"\u{1F3D7}"},
    "Mukachevo":{g:"Rest",o:3,id:1179,base:"Secondary%20cities/Rest%20of%20the%20cities/Mukachevo",p:["good","harsh"],jn:"Mukachevo",icon:"\u{26F0}"},
    "Boryspil":{g:"Rest",o:3,id:1220,base:"Secondary%20cities/Rest%20of%20the%20cities/Boryspil",p:["good","harsh"],jn:"Boryspil",icon:"\u{2708}"},
    "Vyshhorod":{g:"Rest",o:3,id:1262,base:"Secondary%20cities/Rest%20of%20the%20cities/Vyshhorod",p:["good","harsh"],jn:"Vyshhorod",icon:"\u{1F3DE}"},
    "Drohobych":{g:"Rest",o:3,id:1348,base:"Secondary%20cities/Rest%20of%20the%20cities/Drohobych",p:["good","harsh"],jn:"Drohobych",icon:"\u{1F6E2}"},
    "Truskavets":{g:"Rest",o:3,id:1357,base:"Secondary%20cities/Rest%20of%20the%20cities/Truskavets",p:["good","harsh"],jn:"Truskavets",icon:"\u{2668}"},
    "Kovel":{g:"Rest",o:3,id:2170,base:"Secondary%20cities/Rest%20of%20the%20cities/Kovel",p:["good","harsh"],jn:"Kovel",icon:"\u{1F6E4}"},
    "Oleksandriia":{g:"Rest",o:3,id:2171,base:"Secondary%20cities/Rest%20of%20the%20cities/Oleksandriia",p:["good","harsh"],jn:"Oleksandriia",icon:"\u{1F33E}"},
    "Kolomyia":{g:"Rest",o:3,id:2499,base:"Secondary%20cities/Rest%20of%20the%20cities/Kolomyia",p:["good","harsh"],jn:"Kolomyia",icon:"\u{26F0}"}
  };

  const PM = {good:{f:'Good%20weather',px:'Good%20Weather%20Settings'},bad:{f:'Bad%20weather',px:'Bad%20Weather%20Settings'},harsh:{f:'Harsh%20weather',px:'Harsh%20Weather%20Settings'}};
  const PL = {good:'Good',bad:'Bad',harsh:'Harsh'};
  const PF = {good:'Good Weather',bad:'Bad Weather',harsh:'Harsh Weather'};
  const PICON = {good:'\u2600\uFE0F',bad:'\u{1F327}\uFE0F',harsh:'\u{1F328}\uFE0F'};

  const LS = 'cops2_status', LS_U = 'cops2_user', LS_P = 'cops2_pat';
  function loadSt() { try { return JSON.parse(localStorage.getItem(LS)) || {}; } catch(e) { return {}; } }
  function saveSt(s) { localStorage.setItem(LS, JSON.stringify(s)); }
  function getU() { return localStorage.getItem(LS_U) || ''; }
  function getP() { return localStorage.getItem(LS_P) || ''; }

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

  function jsonUrl(name, prof) {
    const c = CITIES[name], m = PM[prof];
    return `${RAW}/${c.base}/${m.f}/${m.px}%20${encodeURIComponent(c.jn)}.json`;
  }

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  let busy = false, autoWin = null;

  async function setSt(city, profile, user) {
    const s = loadSt();
    s[city] = {profile, user, timestamp: new Date().toISOString()};
    if (!s._h) s._h = [];
    s._h.unshift({city, profile, user, timestamp: new Date().toISOString()});
    if (s._h.length > 200) s._h = s._h.slice(0, 200);
    saveSt(s);
    await pushGH(s);
  }

  async function pushGH(local) {
    const pat = getP();
    if (!pat) return;
    try {
      const fr = await fetch(`${GH_API}/repos/${OWNER}/${REPO}/contents/status.json`, {
        headers: {'Authorization': 'Bearer ' + pat, 'Accept': 'application/vnd.github+json'}
      });
      let sha = null, remote = {cities:{}, history:[], last_updated:null};
      if (fr.ok) { const d = await fr.json(); sha = d.sha; try { remote = JSON.parse(atob(d.content)); } catch(e) {} }
      for (const [c, info] of Object.entries(local)) {
        if (c === '_h') continue;
        remote.cities = remote.cities || {};
        remote.cities[c] = info;
      }
      remote.history = remote.history || [];
      for (const h of (local._h || [])) {
        if (!remote.history.find(r => r.city === h.city && r.timestamp === h.timestamp)) remote.history.unshift(h);
      }
      remote.history.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
      remote.history = remote.history.slice(0, 300);
      remote.last_updated = new Date().toISOString();
      const body = {message: `Status: ${new Date().toISOString()}`, content: btoa(unescape(encodeURIComponent(JSON.stringify(remote, null, 2))))};
      if (sha) body.sha = sha;
      await fetch(`${GH_API}/repos/${OWNER}/${REPO}/contents/status.json`, {
        method: 'PUT', headers: {'Authorization': 'Bearer ' + pat, 'Content-Type': 'application/json'}, body: JSON.stringify(body)
      });
    } catch(e) { console.warn('COps push error:', e); }
  }

  function deepMerge(dst, src) {
    for (const k of Object.keys(src)) {
      if (src[k] && typeof src[k] === 'object' && !Array.isArray(src[k])) {
        if (!dst[k] || typeof dst[k] !== 'object') dst[k] = {};
        deepMerge(dst[k], src[k]);
      } else dst[k] = src[k];
    }
  }

  // ── AUTOMATION: script injection into popup ────────────────────────────────

  async function applySettings(cityName, profile) {
    const user = getU();
    if (!user) { toast('Select your name first!', 'error'); return; }
    if (busy) { toast('Another task is running...', 'warn'); return; }
    busy = true;
    const city = CITIES[cityName];
    const settingsUrl = `https://admin-panel.bolt.eu/delivery-courier/settings/city/${city.id}`;
    setCardState(cityName, 'working', `${PICON[profile]} Applying ${PF[profile]}...`);

    if (!autoWin || autoWin.closed) {
      autoWin = window.open(settingsUrl, 'cops_auto', 'width=1300,height=900');
    } else {
      autoWin.location.href = settingsUrl;
    }
    if (!autoWin) {
      toast('Popup blocked! Allow popups for admin-panel.bolt.eu and try again.', 'error');
      setCardState(cityName, 'error', 'Popup blocked');
      busy = false;
      return;
    }

    try {
      toast(`Fetching ${PF[profile]} settings for ${cityName}...`);
      const resp = await fetch(jsonUrl(cityName, profile));
      if (!resp.ok) throw new Error('GitHub fetch failed: HTTP ' + resp.status);
      const target = await resp.json();

      toast('Waiting for admin panel page to load...');
      await waitForBody(autoWin, 15000);
      injectBanner(autoWin, '\u23F3 COps: Waiting for JSON editor to load...');

      await waitForEditor(autoWin, 90000);
      await sleep(2000);
      injectBanner(autoWin, '\u{1F527} COps: Running automation...');

      toast('Injecting automation into admin panel...');
      autoWin.__copsTargetJSON = JSON.stringify(target);

      const result = await runAutomationInPopup(autoWin);
      if (!result.success) throw new Error(result.error || 'Unknown automation error');

      await setSt(cityName, profile, user);
      setCardState(cityName, 'success', `${PICON[profile]} ${PF[profile]} applied!`);
      toast(`\u2705 ${cityName} \u2192 ${PF[profile]} applied by ${user.split('@')[0]}`, 'success');

      setTimeout(() => { try { autoWin.close(); } catch(e) {} }, 2000);
      window.focus();
      renderAll();
    } catch(e) {
      setCardState(cityName, 'error', e.message);
      toast('ERROR: ' + e.message, 'error');
      try { injectBanner(autoWin, '\u274C ERROR: ' + e.message, '#b91c1c'); } catch(x) {}
      window.focus();
    } finally {
      busy = false;
    }
  }

  function waitForBody(win, timeout) {
    return new Promise((resolve) => {
      const deadline = Date.now() + timeout;
      const iv = setInterval(() => {
        try {
          if (win.document && win.document.body) { clearInterval(iv); resolve(); return; }
        } catch(e) { /* cross-origin during SSO redirect, keep polling */ }
        if (Date.now() > deadline) { clearInterval(iv); resolve(); }
      }, 200);
    });
  }

  function injectBanner(win, text, bg) {
    try {
      let b = win.document.getElementById('cops-banner');
      if (!b) {
        b = win.document.createElement('div');
        b.id = 'cops-banner';
        b.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:999999;padding:18px 28px;font:700 18px/1.4 system-ui,sans-serif;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.6);transition:background .3s';
        win.document.body.appendChild(b);
      }
      b.style.background = bg || '#1e40af';
      b.textContent = text;
    } catch(e) { /* couldn't inject, non-critical */ }
  }

  function runAutomationInPopup(win) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        window.removeEventListener('message', handler);
        reject(new Error('Automation timed out (30s)'));
      }, 30000);

      const handler = function(e) {
        if (e.data && e.data.type === 'cops-done') {
          clearTimeout(timeout);
          window.removeEventListener('message', handler);
          resolve(e.data);
        }
      };
      window.addEventListener('message', handler);

      try {
        const script = win.document.createElement('script');
        script.textContent = [
          '(async function(){',
          '  var ban=document.getElementById("cops-banner");',
          '  function p(t,bg){if(ban){ban.textContent=t;if(bg)ban.style.background=bg;}}',
          '  try{',
          '    p("\\u{1F504} Switching to Code mode...");',
          '    var mb=document.querySelector("button.jsoneditor-modes");',
          '    if(mb){',
          '      mb.click();',
          '      await new Promise(function(r){setTimeout(r,600)});',
          '      var items=document.querySelectorAll(".jsoneditor-type-modes div,.jsoneditor-type-modes button");',
          '      for(var i=0;i<items.length;i++){if(items[i].textContent.trim()==="Code"){items[i].click();break;}}',
          '      await new Promise(function(r){setTimeout(r,1200)});',
          '    }',
          '    p("\\u{1F4D6} Reading current settings...");',
          '    var aceEl=document.querySelector(".ace_editor");',
          '    if(!aceEl)throw new Error("Ace editor element not found");',
          '    if(typeof ace==="undefined")throw new Error("ace global not defined");',
          '    var editor=ace.edit(aceEl);',
          '    var raw=editor.getValue();',
          '    if(!raw||raw.trim().length<10)throw new Error("Editor content empty or too short");',
          '    var current=JSON.parse(raw);',
          '    p("\\u{1F500} Merging settings...");',
          '    var target=JSON.parse(window.__copsTargetJSON);',
          '    function mg(d,s){for(var k in s){if(s.hasOwnProperty(k)){if(s[k]&&typeof s[k]==="object"&&!Array.isArray(s[k])){if(!d[k]||typeof d[k]!=="object")d[k]={};mg(d[k],s[k]);}else d[k]=s[k];}}}',
          '    mg(current,target);',
          '    p("\\u{1F4BE} Writing merged settings...");',
          '    editor.setValue(JSON.stringify(current,null,2),-1);',
          '    await new Promise(function(r){setTimeout(r,1000)});',
          '    p("\\u{1F5B1} Clicking Update...");',
          '    var btns=document.querySelectorAll("button");',
          '    var found=false;',
          '    for(var j=0;j<btns.length;j++){if(btns[j].textContent.trim()==="Update"){btns[j].click();found=true;break;}}',
          '    if(!found)throw new Error("Update button not found");',
          '    await new Promise(function(r){setTimeout(r,3000)});',
          '    p("\\u2705 Settings updated successfully!","#047857");',
          '    await new Promise(function(r){setTimeout(r,1000)});',
          '    window.opener.postMessage({type:"cops-done",success:true},"*");',
          '  }catch(e){',
          '    p("\\u274C "+e.message,"#b91c1c");',
          '    window.opener.postMessage({type:"cops-done",success:false,error:e.message||String(e)},"*");',
          '  }',
          '})();'
        ].join('\n');
        win.document.head.appendChild(script);
      } catch(e) {
        clearTimeout(timeout);
        window.removeEventListener('message', handler);
        reject(new Error('Could not inject script: ' + e.message));
      }
    });
  }

  function waitForEditor(win, timeout) {
    return new Promise((resolve, reject) => {
      const deadline = Date.now() + timeout;
      const iv = setInterval(() => {
        try {
          if (Date.now() > deadline) { clearInterval(iv); reject(new Error('Timeout: editor did not load in 90s')); return; }
          if (win.closed) { clearInterval(iv); reject(new Error('Popup was closed')); return; }
          const ed = win.document.querySelector('.jsoneditor');
          if (ed) { clearInterval(iv); resolve(ed); }
        } catch(e) {
          if (Date.now() > deadline) { clearInterval(iv); reject(new Error('Timeout (cross-origin): ' + e.message)); }
        }
      }, 500);
    });
  }

  // ── UI ──────────────────────────────────────────────────────────────────────

  const css = document.createElement('style');
  css.textContent = `
#cops-overlay{position:fixed;inset:0;z-index:999999;background:#06080d;overflow-y:auto;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#e2e5ea;font-size:16px;line-height:1.5}
#cops-overlay *{box-sizing:border-box;margin:0;padding:0}
.ch{background:linear-gradient(180deg,#0d1017 0%,#0a0d14 100%);border-bottom:1px solid #1a1f2e;padding:20px 40px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10;flex-wrap:wrap;gap:14px;backdrop-filter:blur(12px)}
.ch h1{font-size:30px;font-weight:800;color:#fff;letter-spacing:-.5px}
.ch .flag{font-size:38px;margin-right:10px}
.ch .sub{font-size:13px;color:#6b7280;font-weight:500;margin-left:14px;letter-spacing:.5px;text-transform:uppercase}
.chr{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.csel{background:#0d1017;border:1px solid #1e2536;border-radius:24px;padding:8px 18px;display:flex;align-items:center;gap:10px}
.csel label{font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:.6px;font-weight:600}
.csel select,.csel input{background:none;border:none;color:#fff;font-size:15px;font-weight:600;outline:none}
.csel select{cursor:pointer} .csel select option{background:#0d1017;color:#fff}
.csel input{width:160px;font-family:monospace;font-size:13px}
.csel input::placeholder{color:#374151}
.csel .tok{color:#10b981;font-size:16px;display:none}
.csel.v .tok{display:inline}
.cbtn{background:none;border:1px solid #2d3548;border-radius:10px;color:#9ca3af;font-size:16px;padding:10px 22px;cursor:pointer;font-weight:600;transition:all .15s}
.cbtn:hover{background:#111827;color:#fff;border-color:#4b5563}
.cm{padding:28px 40px 60px}
.cov{background:linear-gradient(135deg,#0d1017 0%,#111827 100%);border:1px solid #1e2536;border-radius:18px;padding:24px 28px;margin-bottom:24px}
.cov h3{font-size:16px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.7px;margin-bottom:16px}
.cpills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
.cpill{display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border-radius:10px;background:#080b12;border:1px solid #1a1f2e;font-size:14px;transition:all .15s}
.cpill:hover{border-color:#2d3548;background:#0d1017}
.cpill .ico{font-size:28px}
.cpill .dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.cpill .dot.good{background:#10b981;box-shadow:0 0 10px #10b98155}.cpill .dot.bad{background:#f59e0b;box-shadow:0 0 10px #f59e0b55}.cpill .dot.harsh{background:#ef4444;box-shadow:0 0 10px #ef444455}.cpill .dot.none{background:#374151}
.cpill .pn{font-weight:700;color:#fff;font-size:15px}
.cpill .pp{font-weight:600;font-size:14px}
.cpill .pp.good{color:#10b981}.cpill .pp.bad{color:#f59e0b}.cpill .pp.harsh{color:#ef4444}.cpill .pp.none{color:#6b7280}
.cpill .pm{color:#6b7280;font-size:12px}
.chist{background:#0d1017;border:1px solid #1e2536;border-radius:18px;padding:20px 24px;margin-bottom:24px}
.chist h3{font-size:15px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.7px;margin-bottom:12px;cursor:pointer;user-select:none}
.chist-list{max-height:260px;overflow-y:auto}
.chist-row{display:flex;align-items:center;gap:14px;padding:8px 0;border-bottom:1px solid #151b28;font-size:14px}
.chist-row:last-child{border-bottom:none}
.chist-row .hc{font-weight:700;color:#fff;min-width:140px;font-size:15px}
.chist-row .hp{font-weight:600;min-width:110px}
.chist-row .hp.good{color:#10b981}.chist-row .hp.bad{color:#f59e0b}.chist-row .hp.harsh{color:#ef4444}
.chist-row .hu{color:#3b82f6;font-weight:500;min-width:120px}
.chist-row .ht{color:#6b7280;font-size:13px;font-family:monospace}
.csearch{display:flex;align-items:center;gap:14px;margin-bottom:24px;background:#0d1017;border:1px solid #1e2536;border-radius:14px;padding:12px 20px}
.csearch input{flex:1;background:none;border:none;color:#fff;font-size:16px;outline:none;font-weight:500}
.csearch input::placeholder{color:#374151}
.csec{margin-bottom:24px;background:#0d1017;border:1px solid #1e2536;border-radius:18px;overflow:hidden}
.csec-h{display:flex;align-items:center;gap:14px;padding:16px 24px;cursor:pointer;user-select:none;transition:background .15s}
.csec-h:hover{background:#111827}
.csec-h .chv{font-size:14px;color:#6b7280;transition:transform .2s;width:18px}
.csec.closed .chv{transform:rotate(-90deg)}
.csec-h h2{font-size:18px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px}
.csec-h .cnt{font-size:13px;color:#6b7280;background:#080b12;padding:4px 12px;border-radius:12px;font-weight:700;margin-left:auto}
.csec.closed .csec-b{display:none}
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;padding:6px 24px 22px}
.ccard{background:#080b12;border:1px solid #1a1f2e;border-radius:14px;padding:22px 26px;transition:all .2s}
.ccard:hover{border-color:#2d3548;transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.35)}
.ccard-top{display:flex;align-items:center;gap:14px;margin-bottom:10px}
.ccard .ico{font-size:48px;line-height:1}
.ccard .cn{font-size:22px;font-weight:700;color:#fff}
.ccard .cst{font-size:14px;color:#6b7280;margin-bottom:14px;min-height:24px;display:flex;align-items:center;gap:8px}
.ccard .cst .dot{width:10px;height:10px;border-radius:50%}
.ccard .cst .sp{font-weight:600;font-size:15px}.ccard .cst .sp.good{color:#10b981}.ccard .cst .sp.bad{color:#f59e0b}.ccard .cst .sp.harsh{color:#ef4444}
.ccard .cst .su{color:#3b82f6;font-weight:500}
.cbtns{display:flex;gap:10px}
.cb{flex:1;padding:14px 0;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;letter-spacing:.3px;transition:all .15s;display:flex;align-items:center;justify-content:center;gap:7px}
.cb:disabled{opacity:.3;cursor:not-allowed}
.cb.good{background:linear-gradient(135deg,#059669,#10b981)}.cb.good:hover:not(:disabled){background:linear-gradient(135deg,#047857,#059669);transform:scale(1.03)}
.cb.bad{background:linear-gradient(135deg,#d97706,#f59e0b);color:#1a1a2e}.cb.bad:hover:not(:disabled){background:linear-gradient(135deg,#b45309,#d97706);transform:scale(1.03)}
.cb.harsh{background:linear-gradient(135deg,#dc2626,#ef4444)}.cb.harsh:hover:not(:disabled){background:linear-gradient(135deg,#b91c1c,#dc2626);transform:scale(1.03)}
.cb.on{box-shadow:0 0 0 3px #fff;transform:scale(1.04)}
.ccard .cprog{display:none;margin-top:12px;padding:10px 14px;border-radius:10px;font-size:14px;font-weight:600;text-align:center}
.ccard.working .cprog{display:block;background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.25);color:#60a5fa}
.ccard.success .cprog{display:block;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25);color:#34d399}
.ccard.error .cprog{display:block;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.25);color:#f87171}
#cops-log{position:fixed;bottom:24px;right:24px;z-index:1000000;display:flex;flex-direction:column;gap:8px;max-width:500px}
.tst{padding:14px 20px;border-radius:14px;font-size:15px;font-weight:600;animation:tsin .25s ease;box-shadow:0 8px 30px rgba(0,0,0,.5)}
.tst.info{background:#1e40af;color:#fff}.tst.success{background:#047857;color:#fff}.tst.error{background:#b91c1c;color:#fff}.tst.warn{background:#b45309;color:#fff}
@keyframes tsin{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}
@media(max-width:700px){.cgrid{grid-template-columns:1fr}.ch{padding:14px 18px}.cm{padding:18px 18px 40px}}
`;
  document.head.appendChild(css);

  const ov = document.createElement('div');
  ov.id = 'cops-overlay';
  document.body.appendChild(ov);

  const lg = document.createElement('div');
  lg.id = 'cops-log';
  document.body.appendChild(lg);

  function toast(msg, type='info') {
    const el = document.createElement('div');
    el.className = 'tst ' + type;
    el.textContent = msg;
    lg.appendChild(el);
    setTimeout(() => el.remove(), type === 'error' ? 10000 : 5000);
  }

  function groups() {
    const g = {};
    for (const [n, c] of Object.entries(CITIES)) { if (!g[c.g]) g[c.g] = {o:c.o, cs:[]}; g[c.g].cs.push(n); }
    return Object.entries(g).sort((a,b) => a[1].o - b[1].o);
  }

  function setCardState(cn, st, msg) {
    const cid = 'cc-' + cn.replace(/[^a-zA-Z0-9]/g, '_');
    const cd = document.getElementById(cid);
    if (!cd) return;
    cd.classList.remove('working','success','error');
    if (st) cd.classList.add(st);
    const p = cd.querySelector('.cprog');
    if (p) p.textContent = msg || '';
    if (st === 'success') setTimeout(() => { cd.classList.remove('success'); renderCards(); }, 6000);
    if (st === 'error') setTimeout(() => { cd.classList.remove('error'); }, 10000);
  }

  function renderOverview() {
    const st = loadSt(), el = document.getElementById('c-ov');
    if (!el) return;
    let tracked = 0;
    el.innerHTML = '<h3>\u{1F30D} Active Weather Status</h3>' + groups().map(([gn, gd]) => {
      const pills = gd.cs.map(cn => {
        const s = st[cn], c = CITIES[cn], prof = s?.profile || 'none', lbl = s ? PL[prof] : '\u2014';
        const meta = s ? `<span class="pm">${s.user.split('@')[0]} \u00b7 ${timeAgo(s.timestamp)}</span>` : '';
        if (s) tracked++;
        return `<span class="cpill"><span class="ico">${c.icon}</span><span class="dot ${prof}"></span><span class="pn">${cn}</span><span class="pp ${prof}">${lbl}</span>${meta}</span>`;
      }).join('');
      return `<div style="margin-bottom:12px"><div style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#6b7280;margin-bottom:8px">${gn} \u00b7 ${gd.cs.length}</div><div class="cpills">${pills}</div></div>`;
    }).join('');
    const cnt = document.getElementById('c-cnt');
    if (cnt) cnt.textContent = tracked;
  }

  function renderHist() {
    const st = loadSt(), wrap = document.getElementById('c-hist'), list = document.getElementById('c-hist-list');
    const h = st._h || [];
    if (!wrap || !list || !h.length) { if (wrap) wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    list.innerHTML = h.slice(0, 50).map(r => {
      const prof = r.profile || 'none';
      return `<div class="chist-row"><span class="hc">${CITIES[r.city]?.icon || ''} ${r.city}</span><span class="hp ${prof}">${PICON[prof] || ''} ${PF[prof] || prof}</span><span class="hu">${(r.user||'').split('@')[0]}</span><span class="ht">${r.timestamp ? new Date(r.timestamp).toLocaleString('uk-UA',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}) : ''}</span></div>`;
    }).join('');
  }

  function renderCards(filter) {
    const st = loadSt(), wrap = document.getElementById('c-cities');
    if (!wrap) return;
    const fl = (filter || '').toLowerCase();
    wrap.innerHTML = groups().map(([gn, gd], i) => {
      const cs = fl ? gd.cs.filter(c => c.toLowerCase().includes(fl)) : gd.cs;
      if (!cs.length) return '';
      const cards = cs.map(cn => {
        const c = CITIES[cn], s = st[cn], cid = 'cc-' + cn.replace(/[^a-zA-Z0-9]/g, '_');
        let stH = '<div class="cst">No profile set</div>';
        if (s) stH = `<div class="cst"><span class="dot ${s.profile}"></span><span class="sp ${s.profile}">${PICON[s.profile]} ${PF[s.profile]}</span><span>\u00b7</span><span class="su">${s.user.split('@')[0]}</span><span>\u00b7</span><span>${timeAgo(s.timestamp)}</span></div>`;
        const btns = c.p.map(p => `<button class="cb ${p}${s?.profile===p?' on':''}" onclick="window.__ca('${cn}','${p}')">${PICON[p]} ${PL[p]}</button>`).join('');
        return `<div class="ccard" id="${cid}"><div class="ccard-top"><span class="ico">${c.icon}</span><span class="cn">${cn}</span></div>${stH}<div class="cbtns">${btns}</div><div class="cprog"></div></div>`;
      }).join('');
      const closed = i > 0 && !fl ? ' closed' : '';
      return `<div class="csec${closed}"><div class="csec-h" onclick="this.parentElement.classList.toggle('closed')"><span class="chv">\u25BE</span><h2>${gn}</h2><span class="cnt">${cs.length}</span></div><div class="csec-b"><div class="cgrid">${cards}</div></div></div>`;
    }).join('');
  }

  function renderAll() { renderOverview(); renderHist(); renderCards(document.getElementById('c-search')?.value); }

  window.__ca = function(c, p) { applySettings(c, p); };
  window.__cf = function(v) { renderCards(v); };
  window.__sp = function(v) { localStorage.setItem(LS_P, v.trim()); const g = document.getElementById('c-pat'); if (g) g.classList.toggle('v', v.trim().startsWith('ghp_') || v.trim().startsWith('github_pat_')); };

  const uOpts = USERS.map(u => `<option value="${u.email}" ${getU()===u.email?'selected':''}>${u.name}</option>`).join('');
  const sp = getP(), pv = sp.startsWith('ghp_') || sp.startsWith('github_pat_');

  ov.innerHTML = `
<div class="ch">
  <div style="display:flex;align-items:center"><span class="flag">\u{1F1FA}\u{1F1E6}</span><h1>COps Weather Control</h1><span class="sub">Dashboard</span></div>
  <div class="chr">
    <div class="csel"><label>You</label><select onchange="localStorage.setItem('cops2_user',this.value)"><option value="">-- select --</option>${uOpts}</select></div>
    <div class="csel${pv?' v':''}" id="c-pat"><label>Token</label><input type="password" placeholder="ghp_..." value="${sp}" oninput="window.__sp(this.value)"><span class="tok">\u2713</span></div>
    <div style="text-align:center"><div style="font-size:28px;font-weight:800;color:#fff" id="c-cnt">0</div><div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Tracked</div></div>
    <button class="cbtn" onclick="document.getElementById('cops-overlay').remove();document.getElementById('cops-log')?.remove()">Close</button>
  </div>
</div>
<div class="cm">
  <div class="cov" id="c-ov"></div>
  <div class="chist" id="c-hist" style="display:none"><h3 onclick="var l=document.getElementById('c-hist-list');l.style.display=l.style.display==='none'?'block':'none'">\u{1F4CB} Recent Changes \u25BE</h3><div class="chist-list" id="c-hist-list"></div></div>
  <div class="csearch"><span style="font-size:20px">\u{1F50D}</span><input type="text" id="c-search" placeholder="Search cities..." oninput="window.__cf(this.value)"></div>
  <div id="c-cities"></div>
</div>`;

  renderAll();

  fetch(STATUS_URL + '?t=' + Date.now()).then(r => r.ok ? r.json() : null).then(data => {
    if (!data) return;
    const local = loadSt();
    if (data.cities) {
      for (const [c, info] of Object.entries(data.cities)) {
        if (!local[c] || new Date(info.timestamp) > new Date(local[c].timestamp)) local[c] = info;
      }
    }
    if (data.history) {
      local._h = local._h || [];
      for (const h of data.history) { if (!local._h.find(l => l.city===h.city && l.timestamp===h.timestamp)) local._h.push(h); }
      local._h.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp));
      local._h = local._h.slice(0, 300);
    }
    saveSt(local);
    renderAll();
  }).catch(() => {});

  toast(getP() ? '\u{1F30D} Dashboard ready! Status shared via GitHub.' : '\u{1F30D} Dashboard ready! Add token to share status.', 'success');
})();
