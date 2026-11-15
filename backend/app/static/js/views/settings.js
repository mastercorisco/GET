import {
  applyAppearance,
  getAppearancePrefs,
  resetAppearance,
  saveAppearance,
  toggleManualSettingsVisibility,
} from "../components/appearance.js";
import { rewireHelpAfterLevelChange, setHelpLevel } from "../components/help-ui.js";

let _workspaceOpen = false;
let _saveTimer = null;

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

function defaultPrefs() {
  return {
    schema_version: "1.1",
    theme: "light",
    accent: "blue",
    accent_color: "#1d4ed8",
    font: "system",
    font_family_custom: "",
    density: "normal",
    control_font_size_rem: 1,
    control_padding_block_rem: 0.55,
    control_padding_inline_rem: 0.65,
    textarea_min_height_rem: 5,
    content_width: "normal",
    content_max_px: 1200,
    ui_scale_percent: 100,
  };
}

function readManualPatch() {
  return {
    accent_color: document.getElementById("uiAccentColor")?.value,
    font_family_custom: document.getElementById("uiFontCustom")?.value || "",
    control_font_size_rem: parseFloat(document.getElementById("uiFontSizeRem")?.value || "1"),
    control_padding_block_rem: parseFloat(document.getElementById("uiPadBlockRem")?.value || "0.55"),
    control_padding_inline_rem: parseFloat(document.getElementById("uiPadInlineRem")?.value || "0.65"),
    textarea_min_height_rem: parseFloat(document.getElementById("uiTextareaMinRem")?.value || "5"),
    content_max_px: parseInt(document.getElementById("uiContentMaxPx")?.value || "1200", 10),
    ui_scale_percent: parseInt(document.getElementById("uiScalePercent")?.value || "100", 10),
  };
}

function queueSave(patch) {
  const base = getAppearancePrefs() || defaultPrefs();
  applyAppearance(Object.assign({}, base, patch));
  if (_saveTimer) clearTimeout(_saveTimer);
  _saveTimer = setTimeout(function () {
    saveAppearance(patch).catch(function (err) {
      const st = document.getElementById("settingsStatus");
      if (st) st.textContent = String(err.message || err);
    });
  }, 280);
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
      const patch = readManualPatch();
      patch[map[id]] = el.value;
      toggleManualSettingsVisibility();
      queueSave(patch);
    });
  });

  ["uiFontSizeRem", "uiPadBlockRem", "uiPadInlineRem", "uiTextareaMinRem", "uiScalePercent", "uiContentMaxPx"].forEach(
    function (id) {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("change", function () {
        queueSave(readManualPatch());
      });
    }
  );

  const colorText = document.getElementById("uiAccentColor");
  const colorPick = document.getElementById("uiAccentColorPicker");
  if (colorText && colorPick) {
    colorPick.addEventListener("input", function () {
      colorText.value = colorPick.value;
      const patch = readManualPatch();
      patch.accent = "custom";
      document.getElementById("uiAccent").value = "custom";
      queueSave(patch);
    });
    colorText.addEventListener("change", function () {
      const v = colorText.value.trim();
      if (/^#[0-9A-Fa-f]{6}$/.test(v)) {
        colorPick.value = v;
        const patch = readManualPatch();
        patch.accent = "custom";
        document.getElementById("uiAccent").value = "custom";
        queueSave(patch);
      }
    });
  }

  document.getElementById("uiFontCustom")?.addEventListener("change", function () {
    const patch = readManualPatch();
    patch.font = "custom";
    document.getElementById("uiFont").value = "custom";
    queueSave(patch);
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
          rewireHelpAfterLevelChange(document);
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
  const setVal = function (id, val) {
    const el = document.getElementById(id);
    if (el && val !== undefined && val !== null) el.value = val;
  };
  setVal("uiAccentColor", prefs.accent_color);
  setVal("uiAccentColorPicker", prefs.accent_color);
  setVal("uiFontCustom", prefs.font_family_custom);
  setVal("uiFontSizeRem", prefs.control_font_size_rem);
  setVal("uiPadBlockRem", prefs.control_padding_block_rem);
  setVal("uiPadInlineRem", prefs.control_padding_inline_rem);
  setVal("uiTextareaMinRem", prefs.textarea_min_height_rem);
  setVal("uiContentMaxPx", prefs.content_max_px);
  setVal("uiScalePercent", prefs.ui_scale_percent);
  toggleManualSettingsVisibility();
  const density = prefs.density;
  const sizesHead = document.getElementById("uiManualSizes");
  const sizesFields = document.getElementById("uiManualSizesFields");
  if (sizesHead) sizesHead.hidden = density !== "custom";
  if (sizesFields) sizesFields.hidden = density !== "custom";
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