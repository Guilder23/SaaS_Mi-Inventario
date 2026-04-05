document.addEventListener('DOMContentLoaded', function () {
  // Preferencias guardadas en este navegador
  const KEY_LANG = 'cfg_language';
  const KEY_NOTIF_ENABLED = 'cfg_notif_enabled';
  const KEY_NOTIF_SOUND = 'cfg_notif_sound';

  const lang = document.getElementById('cfgLanguage');
  const notifEnabled = document.getElementById('cfgNotificationsEnabled');
  const notifSound = document.getElementById('cfgNotificationsSound');

  function safeGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  function safeSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      // ignore
    }
  }

  // Idioma (por ahora solo informativo)
  if (lang) {
    const storedLang = safeGet(KEY_LANG);
    if (storedLang) lang.value = storedLang;
    lang.addEventListener('change', function () {
      safeSet(KEY_LANG, lang.value);
    });
  }

  // Notificaciones
  if (notifEnabled) {
    const v = safeGet(KEY_NOTIF_ENABLED);
    if (v !== null) notifEnabled.checked = (v === '1');
    notifEnabled.addEventListener('change', function () {
      safeSet(KEY_NOTIF_ENABLED, notifEnabled.checked ? '1' : '0');
    });
  }

  if (notifSound) {
    const v = safeGet(KEY_NOTIF_SOUND);
    if (v !== null) notifSound.checked = (v === '1');
    notifSound.addEventListener('change', function () {
      safeSet(KEY_NOTIF_SOUND, notifSound.checked ? '1' : '0');
    });
  }

  // Tema (si está permitido por el plan)
  const themeCurrent = document.getElementById('cfgThemeCurrent');
  const toggleBtn = document.getElementById('cfgThemeToggleBtn');

  const rSystem = document.getElementById('cfgThemeSystem');
  const rLight = document.getElementById('cfgThemeLight');
  const rDark = document.getElementById('cfgThemeDark');

  const themeAllowed = (window.THEME_ALLOWED !== false);

  function isValidTheme(t) {
    return t === 'light' || t === 'dark';
  }

  function getCurrentTheme() {
    const attr = document.documentElement.getAttribute('data-theme');
    return isValidTheme(attr) ? attr : 'light';
  }

  function updateCurrentBadge() {
    if (!themeCurrent) return;
    const t = getCurrentTheme();
    themeCurrent.textContent = t;
  }

  function getStoredTheme() {
    try {
      const t = localStorage.getItem('theme');
      return isValidTheme(t) ? t : null;
    } catch (e) {
      return null;
    }
  }

  function setThemeMode(mode) {
    if (!themeAllowed) return;

    if (mode === 'system') {
      try { localStorage.removeItem('theme'); } catch (e) { /* ignore */ }
      // dejar que el script temprano / theme.js siga el sistema
      // Forzar re-evaluación rápida:
      if (window.Theme && typeof window.Theme.applyTheme === 'function') {
        // applyTheme sin persistir: intenta usar lo que ya tenga el atributo
        updateCurrentBadge();
      }
      return;
    }

    if (mode === 'light' || mode === 'dark') {
      if (window.Theme && typeof window.Theme.applyTheme === 'function') {
        window.Theme.applyTheme(mode, true);
      } else {
        document.documentElement.setAttribute('data-theme', mode);
        try { localStorage.setItem('theme', mode); } catch (e) { /* ignore */ }
      }
    }
  }

  function initThemeControls() {
    if (!themeAllowed) return;

    const stored = getStoredTheme();
    if (stored === 'dark') {
      if (rDark) rDark.checked = true;
    } else if (stored === 'light') {
      if (rLight) rLight.checked = true;
    } else {
      if (rSystem) rSystem.checked = true;
    }

    [rSystem, rLight, rDark].forEach(function (r) {
      if (!r) return;
      r.addEventListener('change', function () {
        if (!r.checked) return;
        setThemeMode(r.value);
        updateCurrentBadge();
      });
    });

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        if (!window.Theme || typeof window.Theme.toggleTheme !== 'function') return;
        window.Theme.toggleTheme();
        // al alternar, se vuelve “manual”
        const t = getCurrentTheme();
        if (t === 'dark' && rDark) rDark.checked = true;
        if (t === 'light' && rLight) rLight.checked = true;
        updateCurrentBadge();
      });
    }

    updateCurrentBadge();
  }

  initThemeControls();
});
