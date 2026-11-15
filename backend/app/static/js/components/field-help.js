/** Ajuda contextual a partir do catálogo JSON (microajuda + modal). */

let _catalog = null;
let _helpLevel = "normal";
let _openModal = null;
let _lastTrigger = null;

export function setHelpLevel(level) {
  _helpLevel = level || "normal";
}

export async function loadHelpCatalog() {
  try {
    const res = await fetch("/api/catalogs/help");
    if (res.ok) {
      _catalog = await res.json();
    }
  } catch (_e) {
    _catalog = { fields: {} };
  }
}

function fieldEntry(key) {
  const fields = (_catalog && _catalog.fields) || {};
  return fields[key] || {
    label: key,
    short_help: "Ajuda não disponível.",
  };
}

function closeModal() {
  if (_openModal) {
    _openModal.remove();
    _openModal = null;
    document.removeEventListener("keydown", onEsc, true);
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
    document.removeEventListener("click", onOutside, true);
  }
}

export function attachFieldHelp(container, fieldKey, options) {
  const entry = fieldEntry(fieldKey);
  const inputEl = options.inputEl;
  const onUseExample = options.onUseExample;

  if (_helpLevel !== "essential") {
    const micro = document.createElement("p");
    micro.className = "field-microhelp";
    micro.textContent = entry.short_help || "";
    container.appendChild(micro);
  }

  if (_helpLevel === "essential") {
    return;
  }

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tip-btn field-help-btn";
  btn.setAttribute("aria-label", "Ajuda: " + (entry.label || fieldKey));
  btn.textContent = "i";
  btn.addEventListener("click", function (ev) {
    ev.preventDefault();
    closeModal();
    _lastTrigger = btn;
    const dlg = document.createElement("div");
    dlg.className = "field-help-modal";
    dlg.setAttribute("role", "dialog");
    dlg.setAttribute("aria-modal", "true");
    dlg.tabIndex = -1;

    const title = document.createElement("h4");
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

    addSection("Definição", entry.definition);
    addSection("Pergunta orientadora", entry.guiding_question);
    if (_helpLevel === "detailed" && entry.tips && entry.tips.length) {
      addSection("Dicas", entry.tips.join(" "));
    }
    if (_helpLevel === "detailed" && entry.good_examples && entry.good_examples.length) {
      const good = document.createElement("ul");
      entry.good_examples.forEach(function (ex) {
        const li = document.createElement("li");
        li.textContent = typeof ex === "string" ? ex : ex.text;
        good.appendChild(li);
      });
      dlg.appendChild(good);
    }
    if (_helpLevel === "detailed" && entry.bad_examples && entry.bad_examples.length) {
      entry.bad_examples.forEach(function (ex) {
        const p = document.createElement("p");
        p.className = "field-help-bad";
        p.textContent = (ex.text || "") + (ex.reason ? " — " + ex.reason : "");
        dlg.appendChild(p);
      });
    }

    if (entry.allow_use_example && onUseExample && entry.good_examples && entry.good_examples.length) {
      const useBtn = document.createElement("button");
      useBtn.type = "button";
      useBtn.className = "secondary";
      useBtn.textContent = "Usar este exemplo como base";
      useBtn.addEventListener("click", function () {
        const sample = entry.good_examples[0];
        const text = typeof sample === "string" ? sample : sample.text;
        if (window.confirm("Adapte o exemplo ao seu contexto. Não copie sem rever.")) {
          onUseExample(text);
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
  });

  const labelRow = container.querySelector("label") || container;
  if (labelRow.tagName === "LABEL") {
    labelRow.appendChild(btn);
  } else {
    container.insertBefore(btn, container.firstChild);
  }
}