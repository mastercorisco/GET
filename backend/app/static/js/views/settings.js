import { resetAppearance, saveAppearance } from "../components/appearance.js";
import { setHelpLevel, wireDeclarativeHelp } from "../components/help-ui.js";

let _workspaceOpen = false;

export function setSettingsWorkspaceOpen(open) {
  _workspaceOpen = open;
  const wrap = document.getElementById("settingsHelpWrap");
  const hint = document.getElementById("settingsHelpHint");
  const sel = document.getElementById("helpLevel");
  if (wrap) wrap.classList.toggle("settings-help-disabled", !open);
  if (hint) hint.hidden = open;
  if (sel) sel.disabled = !open;
  if (open) loadHelpLevel();
}

function loadHelpLevel() {
  fetch("/api/workspace/preferences")
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (p) {
      const sel = document.getElementById("helpLevel");
      if (p && sel) sel.value = p.help_level;
    })
    .catch(function () {});
}

export function initSettingsView(router) {
  const map = {
    uiTheme: "theme",
    uiAccent: "accent",
    uiFont: "font",
    uiDensity: "density",
    uiContentWidth: "content_width",
  };

  Object.keys(map).forEach(function (id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("change", function () {
      const patch = {};
      patch[map[id]] = el.value;
      saveAppearance(patch).catch(function (err) {
        const st = document.getElementById("settingsStatus");
        if (st) st.textContent = String(err.message || err);
      });
    });
  });

  document.getElementById("uiReset")?.addEventListener("click", function () {
    resetAppearance()
      .then(syncFormFromPrefs)
      .catch(function (err) {
        const st = document.getElementById("settingsStatus");
        if (st) st.textContent = String(err.message || err);
      });
  });

  const headerBtn = document.getElementById("headerSettings");
  if (headerBtn && router) {
    headerBtn.addEventListener("click", function () {
      router.navigate("settings");
    });
  }

  const helpSel = document.getElementById("helpLevel");
  if (helpSel) {
    helpSel.addEventListener("change", function () {
      if (!_workspaceOpen) return;
      fetch("/api/workspace/preferences", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ help_level: helpSel.value }),
      })
        .then(function (r) {
          return r.ok ? r.json() : Promise.reject(new Error("Falha ao guardar nível de ajuda"));
        })
        .then(function (p) {
          setHelpLevel(p.help_level);
          wireDeclarativeHelp(document);
        })
        .catch(function (err) {
          const st = document.getElementById("settingsStatus");
          if (st) st.textContent = err.message;
        });
    });
  }

  document.addEventListener("get:appearance-changed", syncFormFromPrefs);
  loadSettingsForm();
}

function syncFormFromPrefs(ev) {
  const prefs = ev && ev.detail ? ev.detail : null;
  if (!prefs) return loadSettingsForm();
  const ids = {
    uiTheme: prefs.theme,
    uiAccent: prefs.accent,
    uiFont: prefs.font,
    uiDensity: prefs.density,
    uiContentWidth: prefs.content_width,
  };
  Object.keys(ids).forEach(function (id) {
    const el = document.getElementById(id);
    if (el && ids[id]) el.value = ids[id];
  });
}

function loadSettingsForm() {
  fetch("/api/ui-preferences")
    .then(function (r) {
      return r.ok ? r.json() : null;
    })
    .then(function (prefs) {
      if (prefs) syncFormFromPrefs({ detail: prefs });
    });
  if (_workspaceOpen) {
    fetch("/api/workspace/preferences")
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (p) {
        const sel = document.getElementById("helpLevel");
        if (p && sel) sel.value = p.help_level;
      })
      .catch(function () {});
  }
}