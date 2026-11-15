/** Preferências de aparência (máquina local + /api/ui-preferences). */

const STORAGE_KEY = "get:ui-prefs";

const FONT_STACKS = {
  system: '"Segoe UI", system-ui, -apple-system, sans-serif',
  segoe: '"Segoe UI", system-ui, sans-serif',
  atkinson: '"Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif',
  source_sans: '"Source Sans 3", "Segoe UI", system-ui, sans-serif',
  georgia: 'Georgia, "Times New Roman", serif',
  monospace: 'ui-monospace, Consolas, "Cascadia Code", monospace',
};

const FONT_CDN = {
  atkinson:
    "https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;600&display=swap",
  source_sans:
    "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600&display=swap",
};

let _prefs = null;
let _systemMq = null;

const DENSITY_TOKENS = {
  compact: {
    "--control-padding": "0.35rem 0.5rem",
    "--control-font-size": "0.875rem",
    "--textarea-min-height": "3.25rem",
    "--card-padding": "0.75rem 0.85rem",
    "--heading-scale": "0.95",
  },
  normal: {
    "--control-padding": "0.55rem 0.65rem",
    "--control-font-size": "1rem",
    "--textarea-min-height": "5rem",
    "--card-padding": "1.25rem 1.35rem",
    "--heading-scale": "1",
  },
  comfortable: {
    "--control-padding": "0.7rem 0.85rem",
    "--control-font-size": "1.05rem",
    "--textarea-min-height": "6.5rem",
    "--card-padding": "1.5rem 1.65rem",
    "--heading-scale": "1.05",
  },
};

const CONTENT_WIDTH_TOKENS = {
  narrow: "960px",
  normal: "1200px",
  wide: "1400px",
  xlarge: "1600px",
};

function scaleRem(rem, percent) {
  const n = parseFloat(rem) * (percent / 100);
  return n.toFixed(3).replace(/\.?0+$/, "") + "rem";
}

function buildCustomDensityTokens(prefs) {
  const scale = prefs.ui_scale_percent || 100;
  const block = prefs.control_padding_block_rem ?? 0.55;
  const inline = prefs.control_padding_inline_rem ?? 0.65;
  const font = prefs.control_font_size_rem ?? 1;
  const ta = prefs.textarea_min_height_rem ?? 5;
  return {
    "--control-padding": scaleRem(block, scale) + " " + scaleRem(inline, scale),
    "--control-font-size": scaleRem(font, scale),
    "--textarea-min-height": scaleRem(ta, scale),
    "--card-padding": scaleRem(1.25, scale) + " " + scaleRem(1.35, scale),
    "--heading-scale": String(Math.min(1.15, Math.max(0.85, scale / 100))),
  };
}

function resolveDensityTokens(prefs) {
  if (prefs.density === "custom") {
    return buildCustomDensityTokens(prefs);
  }
  const base = DENSITY_TOKENS[prefs.density] || DENSITY_TOKENS.normal;
  if ((prefs.ui_scale_percent || 100) === 100) {
    return base;
  }
  const scale = prefs.ui_scale_percent;
  const custom = buildCustomDensityTokens({
    control_padding_block_rem: parseFloat(base["--control-padding"].split(" ")[0]),
    control_padding_inline_rem: parseFloat(base["--control-padding"].split(" ")[1]),
    control_font_size_rem: parseFloat(base["--control-font-size"]),
    textarea_min_height_rem: parseFloat(base["--textarea-min-height"]),
    ui_scale_percent: scale,
  });
  return custom;
}

function resolveContentMax(prefs) {
  if (prefs.content_width === "custom") {
    return (prefs.content_max_px || 1200) + "px";
  }
  return CONTENT_WIDTH_TOKENS[prefs.content_width] || CONTENT_WIDTH_TOKENS.normal;
}

function adjustHex(hex, amount) {
  if (!hex || hex[0] !== "#" || hex.length !== 7) return hex;
  const clamp = function (v) {
    return Math.max(0, Math.min(255, v));
  };
  const r = clamp(parseInt(hex.slice(1, 3), 16) + amount);
  const g = clamp(parseInt(hex.slice(3, 5), 16) + amount);
  const b = clamp(parseInt(hex.slice(5, 7), 16) + amount);
  return (
    "#" +
    [r, g, b]
      .map(function (x) {
        return x.toString(16).padStart(2, "0");
      })
      .join("")
  );
}

function applyAccentCustom(el, prefs) {
  if (prefs.accent !== "custom" || !prefs.accent_color) return;
  const c = prefs.accent_color;
  el.style.setProperty("--color-accent", c);
  el.style.setProperty("--color-accent-hover", adjustHex(c, -18));
  el.style.setProperty("--color-accent-subtle", adjustHex(c, 120));
}

function applyInlineTokens(el, prefs) {
  const tokens = resolveDensityTokens(prefs);
  Object.keys(tokens).forEach(function (key) {
    el.style.setProperty(key, tokens[key]);
  });
  el.style.setProperty("--content-max", resolveContentMax(prefs));
  applyAccentCustom(el, prefs);
}

function syncSettingsPreview(prefs, effective) {
  const box = document.getElementById("settingsPreviewRoot");
  const meta = document.getElementById("settingsPreviewMeta");
  if (box) {
    box.dataset.themeEffective = effective;
    box.dataset.density = prefs.density || "normal";
    box.dataset.accent = prefs.accent || "blue";
    applyInlineTokens(box, prefs);
    applyAccentCustom(box, prefs);
  }
  if (meta) {
    const extra =
      prefs.density === "custom" || prefs.accent === "custom" || prefs.content_width === "custom"
        ? " · valores manuais activos"
        : "";
    meta.textContent =
      "Tema: " +
      prefs.theme +
      " (" +
      effective +
      ") · densidade: " +
      prefs.density +
      " · acento: " +
      (prefs.accent === "custom" ? prefs.accent_color : prefs.accent) +
      extra;
  }
}

function resolveEffectiveTheme(theme) {
  if (theme === "dark") return "dark";
  if (theme === "light") return "light";
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

function ensureFontLink(fontKey) {
  const href = FONT_CDN[fontKey];
  if (!href) return;
  const id = "get-font-" + fontKey;
  if (document.getElementById(id)) return;
  const link = document.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href = href;
  document.head.appendChild(link);
}

export function getAppearancePrefs() {
  return _prefs;
}

export function applyAppearance(prefs) {
  if (!prefs) return;
  _prefs = prefs;
  const root = document.documentElement;
  const effective = resolveEffectiveTheme(prefs.theme);
  root.dataset.theme = prefs.theme;
  root.dataset.themeEffective = effective;
  root.dataset.accent = prefs.accent === "custom" ? "custom" : prefs.accent;
  root.dataset.density = prefs.density;
  root.dataset.contentWidth = prefs.content_width === "custom" ? "custom" : prefs.content_width;
  root.dataset.font = prefs.font;
  let stack = FONT_STACKS[prefs.font] || FONT_STACKS.system;
  if (prefs.font === "custom" && prefs.font_family_custom) {
    stack = prefs.font_family_custom;
  }
  root.style.setProperty("--font-sans", stack);
  if (prefs.font === "atkinson" || prefs.font === "source_sans") {
    ensureFontLink(prefs.font);
  }
  applyInlineTokens(root, prefs);
  syncSettingsPreview(prefs, effective);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch (_e) {
    /* quota / private mode */
  }
}

function applyFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      applyAppearance(JSON.parse(raw));
      return true;
    }
  } catch (_e) {
    /* ignore */
  }
  return false;
}

function watchSystemTheme() {
  if (!window.matchMedia) return;
  _systemMq = window.matchMedia("(prefers-color-scheme: dark)");
  const handler = function () {
    if (_prefs && _prefs.theme === "system") {
      applyAppearance(_prefs);
    }
  };
  if (_systemMq.addEventListener) {
    _systemMq.addEventListener("change", handler);
  } else if (_systemMq.addListener) {
    _systemMq.addListener(handler);
  }
}

export function hydrateAppearanceFromStorage() {
  applyFromStorage();
}

export async function initAppearance() {
  applyFromStorage();
  watchSystemTheme();
  try {
    const res = await fetch("/api/ui-preferences");
    if (res.ok) {
      const prefs = await res.json();
      applyAppearance(prefs);
    }
  } catch (_e) {
    /* offline */
  }
}

export async function saveAppearance(patch) {
  const res = await fetch("/api/ui-preferences", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const body = await res.json().catch(function () {
      return {};
    });
    throw new Error(body.detail || res.statusText);
  }
  const prefs = await res.json();
  applyAppearance(prefs);
  document.dispatchEvent(new CustomEvent("get:appearance-changed", { detail: prefs }));
  return prefs;
}

export async function resetAppearance() {
  return saveAppearance({ reset_defaults: true });
}

export function toggleManualSettingsVisibility() {
  const accent = document.getElementById("uiAccent")?.value;
  const density = document.getElementById("uiDensity")?.value;
  const font = document.getElementById("uiFont")?.value;
  const cw = document.getElementById("uiContentWidth")?.value;
  const accentCustom = document.getElementById("uiManualAccent");
  const sizes = document.getElementById("uiManualSizes");
  const sizesFields = document.getElementById("uiManualSizesFields");
  const fontCustom = document.getElementById("uiManualFont");
  const cwCustom = document.getElementById("uiManualContentWidth");
  if (accentCustom) accentCustom.hidden = accent !== "custom";
  if (sizes) sizes.hidden = density !== "custom";
  if (sizesFields) sizesFields.hidden = density !== "custom";
  if (fontCustom) fontCustom.hidden = font !== "custom";
  if (cwCustom) cwCustom.hidden = cw !== "custom";
}