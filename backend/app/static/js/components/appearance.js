/** Preferências de aparência (máquina local + /api/ui-preferences). */

const STORAGE_KEY = "get:ui-prefs";

const FONT_STACKS = {
  system: '"Segoe UI", system-ui, -apple-system, sans-serif',
  segoe: '"Segoe UI", system-ui, sans-serif',
  atkinson: '"Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif',
  source_sans: '"Source Sans 3", "Segoe UI", system-ui, sans-serif',
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
};

function applyInlineTokens(el, prefs) {
  const density = prefs.density || "normal";
  const tokens = DENSITY_TOKENS[density] || DENSITY_TOKENS.normal;
  Object.keys(tokens).forEach(function (key) {
    el.style.setProperty(key, tokens[key]);
  });
  const cw = CONTENT_WIDTH_TOKENS[prefs.content_width] || CONTENT_WIDTH_TOKENS.normal;
  el.style.setProperty("--content-max", cw);
}

function syncSettingsPreview(prefs, effective) {
  const box = document.getElementById("settingsPreviewRoot");
  const meta = document.getElementById("settingsPreviewMeta");
  if (box) {
    box.dataset.themeEffective = effective;
    box.dataset.density = prefs.density || "normal";
    box.dataset.accent = prefs.accent || "blue";
    applyInlineTokens(box, prefs);
  }
  if (meta) {
    meta.textContent =
      "Tema: " +
      prefs.theme +
      " (" +
      effective +
      ") · densidade: " +
      prefs.density +
      " · acento: " +
      prefs.accent;
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
  root.dataset.accent = prefs.accent;
  root.dataset.density = prefs.density;
  root.dataset.contentWidth = prefs.content_width;
  root.dataset.font = prefs.font;
  const stack = FONT_STACKS[prefs.font] || FONT_STACKS.system;
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