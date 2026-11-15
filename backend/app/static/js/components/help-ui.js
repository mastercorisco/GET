/** Ajuda contextual unificada (catálogo JSON + níveis essential/normal/detailed). */

let _catalog = null;
let _helpLevel = "normal";
let _openModal = null;
let _lastTrigger = null;

export function getHelpCatalog() {
  return _catalog;
}

export function getHelpLevel() {
  return _helpLevel;
}

export function setHelpLevel(level) {
  _helpLevel = level || (_catalog && _catalog.default_help_level) || "normal";
  document.dispatchEvent(
    new CustomEvent("get:help-level-changed", { detail: { level: _helpLevel } })
  );
}

/** Recoloca ajuda após mudança de nível (normal = só popup). */
export function rewireHelpAfterLevelChange(root) {
  const scope = root || document;
  scope.querySelectorAll(".field-microhelp").forEach(function (el) {
    el.remove();
  });
  scope.querySelectorAll("label[data-help-key]").forEach(function (label) {
    delete label.dataset.helpWired;
  });
  wireDeclarativeHelp(scope);
}

export async function loadHelpCatalog() {
  try {
    const res = await fetch("/api/catalogs/help");
    if (res.ok) {
      _catalog = await res.json();
    }
  } catch (_e) {
    _catalog = { fields: {}, screens: {}, concepts: {} };
  }
  return _catalog;
}

export async function initHelpSystem() {
  await loadHelpCatalog();
  try {
    const res = await fetch("/api/workspace/preferences");
    if (res.ok) {
      const prefs = await res.json();
      if (prefs.help_level) setHelpLevel(prefs.help_level);
    }
  } catch (_e) {
    /* workspace fechado */
  }
  wireDeclarativeHelp(document);
  const sel = document.getElementById("helpLevel");
  if (sel) {
    sel.value = _helpLevel;
    sel.addEventListener("change", function () {
      fetch("/api/workspace/preferences", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ help_level: sel.value }),
      })
        .then(function (r) {
          return r.ok ? r.json() : null;
        })
        .then(function (p) {
          if (p) setHelpLevel(p.help_level);
          rewireHelpAfterLevelChange(document);
        });
    });
  }
}

function fieldEntry(key) {
  const fields = (_catalog && _catalog.fields) || {};
  return (
    fields[key] || {
      label: key,
      short_help: "Ajuda não disponível para este campo.",
      definition: "",
      guiding_question: "",
      instructions: "",
      good_examples: [],
      bad_examples: [],
      tips: [],
      allow_use_example: false,
    }
  );
}

function inputForLabel(label) {
  const fid = label.getAttribute("for");
  if (fid) return document.getElementById(fid);
  let sib = label.nextElementSibling;
  while (sib && (sib.tagName === "BUTTON" || sib.classList.contains("field-microhelp"))) {
    sib = sib.nextElementSibling;
  }
  return sib;
}

function closeModal() {
  if (_openModal) {
    _openModal.remove();
    _openModal = null;
    document.removeEventListener("keydown", onEsc, true);
    document.removeEventListener("click", onOutside, true);
  }
  if (_lastTrigger) {
    _lastTrigger.focus();
    _lastTrigger = null;
  }
}

function onEsc(ev) {
  if (ev.key === "Escape") {
    ev.preventDefault();
    closeModal();
  }
}

function onOutside(ev) {
  if (_openModal && !_openModal.contains(ev.target) && ev.target !== _lastTrigger) {
    closeModal();
  }
}

function createHelpButton(fieldKey, inputEl, onUseExample) {
  const entry = fieldEntry(fieldKey);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tip-btn field-help-btn";
  btn.setAttribute("aria-label", "Ajuda: " + (entry.label || fieldKey));
  btn.textContent = "i";
  btn.addEventListener("click", function (ev) {
    ev.preventDefault();
    ev.stopPropagation();
    openHelpModal(fieldKey, { inputEl: inputEl, onUseExample: onUseExample, trigger: btn });
  });
  return btn;
}

export function openHelpModal(fieldKey, options) {
  options = options || {};
  const entry = fieldEntry(fieldKey);
  const inputEl = options.inputEl;
  const onUseExample = options.onUseExample;
  closeModal();
  _lastTrigger = options.trigger || null;

  const dlg = document.createElement("div");
  dlg.className = "field-help-modal field-help-modal--centered";
  dlg.setAttribute("role", "dialog");
  dlg.setAttribute("aria-modal", "true");
  dlg.setAttribute("aria-labelledby", "help-modal-title");
  dlg.tabIndex = -1;

  const title = document.createElement("h4");
  title.id = "help-modal-title";
  title.textContent = entry.label || fieldKey;
  dlg.appendChild(title);

  function addSection(heading, text) {
    if (!text) return;
    const h = document.createElement("p");
    h.className = "field-help-section-title";
    h.textContent = heading;
    dlg.appendChild(h);
    const p = document.createElement("p");
    p.textContent = text;
    dlg.appendChild(p);
  }

  if (_helpLevel !== "essential" && entry.short_help) {
    addSection("Resumo", entry.short_help);
  }
  addSection("Definição", entry.definition);
  addSection("Pergunta orientadora", entry.guiding_question);
  const instr = entry.instructions || (entry.tips && entry.tips[0]) || "";
  addSection("Instruções", typeof instr === "string" ? instr : instr.join(" "));

  const showAllExamples = _helpLevel === "detailed";
  const goods = entry.good_examples || [];
  const bads = entry.bad_examples || [];

  if (goods.length) {
    addSection("Exemplo correcto", "");
    const ul = document.createElement("ul");
    (showAllExamples ? goods : goods.slice(0, 1)).forEach(function (ex) {
      const li = document.createElement("li");
      li.textContent = typeof ex === "string" ? ex : ex.text;
      ul.appendChild(li);
    });
    dlg.appendChild(ul);
  }

  if (bads.length) {
    addSection("Exemplo incorrecto", "");
    (showAllExamples ? bads : bads.slice(0, 1)).forEach(function (ex) {
      const p = document.createElement("p");
      p.className = "field-help-bad";
      p.textContent = (ex.text || ex) + (ex.reason ? " — " + ex.reason : "");
      dlg.appendChild(p);
    });
  }

  if (_helpLevel === "detailed" && entry.tips && entry.tips.length > 1) {
    addSection("Dicas", entry.tips.join(" "));
  }

  if (entry.allow_use_example && onUseExample && goods.length) {
    const useBtn = document.createElement("button");
    useBtn.type = "button";
    useBtn.className = "secondary";
    useBtn.textContent = "Usar este exemplo como base";
    useBtn.addEventListener("click", function () {
      const sample = goods[0];
      const text = typeof sample === "string" ? sample : sample.text;
      if (window.confirm("Adapte o exemplo ao seu contexto. Não copie sem rever.")) {
        onUseExample(text);
        closeModal();
        if (inputEl) inputEl.focus();
      }
    });
    dlg.appendChild(useBtn);
  }

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.textContent = "Fechar";
  closeBtn.addEventListener("click", closeModal);
  dlg.appendChild(closeBtn);

  document.body.appendChild(dlg);
  _openModal = dlg;
  dlg.focus();
  document.addEventListener("keydown", onEsc, true);
  setTimeout(function () {
    document.addEventListener("click", onOutside, true);
  }, 0);
}

export function attachFieldHelp(container, fieldKey, options) {
  options = options || {};
  const entry = fieldEntry(fieldKey);
  const inputEl = options.inputEl;
  const onUseExample = options.onUseExample;

  let label = container.querySelector("label");
  if (!label && container.tagName === "LABEL") label = container;

  if (_helpLevel === "detailed") {
    const existing = container.querySelector(".field-microhelp");
    if (!existing && entry.short_help) {
      const micro = document.createElement("p");
      micro.className = "field-microhelp";
      micro.textContent = entry.short_help;
      container.appendChild(micro);
    }
  }

  const btn = createHelpButton(fieldKey, inputEl, onUseExample);
  if (label) {
    if (!label.querySelector(".field-help-btn")) {
      label.classList.add("field-label-row");
      label.appendChild(btn);
    }
  } else {
    container.insertBefore(btn, container.firstChild);
  }
}

export function wireDeclarativeHelp(root) {
  if (!root) return;
  root.querySelectorAll("label[data-help-key]").forEach(function (label) {
    const key = label.dataset.helpKey;
    if (!key || label.dataset.helpWired === "1") return;
    const input = inputForLabel(label);
    const wrap =
      label.parentElement && label.parentElement.classList.contains("field-wrap")
        ? label.parentElement
        : null;
    const onUse =
      input && (input.tagName === "INPUT" || input.tagName === "TEXTAREA")
        ? function (text) {
            input.value = text;
            input.dispatchEvent(new Event("change", { bubbles: true }));
          }
        : undefined;
    if (wrap) {
      attachFieldHelp(wrap, key, { inputEl: input, onUseExample: onUse });
    } else {
      attachFieldHelp(label.parentElement || label, key, {
        inputEl: input,
        onUseExample: onUse,
      });
    }
    label.dataset.helpWired = "1";
  });
}