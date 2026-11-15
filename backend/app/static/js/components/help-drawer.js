/** Gaveta de ajuda à direita (padrão da app). */

let _drawerEl = null;
let _drawerBody = null;
let _drawerTitle = null;
let _backdropEl = null;
let _drawerCloseBtn = null;
let _lastTrigger = null;
let _keydownWired = false;

export function initGlobalHelpDrawer() {
  if (_drawerEl) return;

  _backdropEl = document.createElement("div");
  _backdropEl.id = "getHelpDrawerBackdrop";
  _backdropEl.className = "help-drawer-backdrop";
  _backdropEl.hidden = true;
  _backdropEl.addEventListener("click", closeHelpDrawer);

  _drawerEl = document.createElement("aside");
  _drawerEl.id = "getHelpDrawer";
  _drawerEl.className = "help-drawer help-drawer--global";
  _drawerEl.setAttribute("aria-hidden", "true");
  _drawerEl.setAttribute("aria-label", "Ajuda contextual");

  const header = document.createElement("header");
  header.className = "help-drawer__header";

  _drawerTitle = document.createElement("h3");
  _drawerTitle.id = "getHelpDrawerTitle";

  _drawerCloseBtn = document.createElement("button");
  _drawerCloseBtn.type = "button";
  _drawerCloseBtn.id = "getHelpDrawerClose";
  _drawerCloseBtn.className = "help-drawer__close ghost";
  _drawerCloseBtn.textContent = "Fechar";
  _drawerCloseBtn.addEventListener("click", closeHelpDrawer);

  header.appendChild(_drawerTitle);
  header.appendChild(_drawerCloseBtn);

  _drawerBody = document.createElement("div");
  _drawerBody.id = "getHelpDrawerBody";
  _drawerBody.className = "help-drawer__body field-help-modal";

  _drawerEl.appendChild(header);
  _drawerEl.appendChild(_drawerBody);

  document.body.appendChild(_backdropEl);
  document.body.appendChild(_drawerEl);

  if (!_keydownWired) {
    _keydownWired = true;
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && _drawerEl?.classList.contains("is-open")) {
        ev.preventDefault();
        closeHelpDrawer();
      }
    });
  }
}

export function openHelpDrawer({ title, content, trigger }) {
  initGlobalHelpDrawer();
  closeLocalHelpDrawers();
  _lastTrigger = trigger || null;
  _drawerTitle.textContent = title || "Ajuda";
  _drawerBody.replaceChildren();
  if (content) {
    if (content instanceof DocumentFragment) {
      _drawerBody.appendChild(content);
    } else if (content.nodeType === 1) {
      _drawerBody.appendChild(content);
    } else if (typeof content === "function") {
      content(_drawerBody);
    }
  }
  _drawerEl.classList.add("is-open");
  _drawerEl.setAttribute("aria-hidden", "false");
  _backdropEl.hidden = false;
  _drawerCloseBtn.focus();
}

export function closeHelpDrawer() {
  if (_drawerEl) {
    _drawerEl.classList.remove("is-open");
    _drawerEl.setAttribute("aria-hidden", "true");
    _drawerBody?.replaceChildren();
  }
  if (_backdropEl) _backdropEl.hidden = true;
  if (_lastTrigger) {
    _lastTrigger.focus();
    _lastTrigger = null;
  }
}

function closeLocalHelpDrawers() {
  document.querySelectorAll(".help-drawer--local.is-open").forEach(function (el) {
    el.classList.remove("is-open");
    el.setAttribute("aria-hidden", "true");
    const openBtn = el.closest(".help-drawer-host")?.querySelector(".help-drawer-open");
    if (openBtn) openBtn.hidden = false;
  });
}

/** Gaveta local (ex.: ajuda à preparação do bloco dentro do ecrã). */
export function wireLocalHelpDrawer(hostEl, { aside, openBtn, closeBtn }) {
  if (!hostEl || !aside || !openBtn) return;

  hostEl.classList.add("help-drawer-host");

  function setOpen(open) {
    aside.classList.toggle("is-open", open);
    aside.setAttribute("aria-hidden", open ? "false" : "true");
    openBtn.hidden = open;
    openBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      closeHelpDrawer();
      closeBtn?.focus();
    }
  }

  setOpen(false);
  openBtn.addEventListener("click", function () {
    setOpen(true);
  });
  closeBtn?.addEventListener("click", function () {
    setOpen(false);
    openBtn.focus();
  });
}