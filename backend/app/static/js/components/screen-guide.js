import { getHelpCatalog } from "./help-ui.js";
import { openHelpDrawer } from "./help-drawer.js";
import { setHelpTriggerLabel } from "./help-icon.js";

const ROUTE_LABELS = {
  library: "Biblioteca",
  workbook: "Importação Excel",
  project: "Projecto",
  "project-structure": "Estrutura documental",
  "block-editor": "Preparação do bloco",
  export: "Exportar",
  import: "Reimportar",
};

function buildScreenGuideBody(meta) {
  const body = document.createElement("div");
  body.className = "field-help-modal--drawer-body";

  if (meta.audience_note) {
    const note = document.createElement("p");
    note.className = "screen-guide-audience";
    note.textContent = meta.audience_note;
    body.appendChild(note);
  }
  if (meta.objective) {
    const p = document.createElement("p");
    p.className = "lead";
    p.textContent = meta.objective;
    body.appendChild(p);
  }
  const stepItems = (meta.purpose_steps && meta.purpose_steps.length
    ? meta.purpose_steps
    : meta.steps) || [];
  if (stepItems.length) {
    const h = document.createElement("p");
    h.className = "field-help-section-title";
    h.textContent = "O que fazer e porquê";
    body.appendChild(h);
    const ol = document.createElement("ol");
    ol.className = "screen-guide-steps";
    stepItems.forEach(function (step) {
      const li = document.createElement("li");
      li.textContent = step;
      ol.appendChild(li);
    });
    body.appendChild(ol);
  }
  if (meta.next && ROUTE_LABELS[meta.next]) {
    const next = document.createElement("p");
    next.className = "screen-guide-next";
    next.textContent = "Seguinte sugerido: «" + ROUTE_LABELS[meta.next] + "» (menu lateral).";
    body.appendChild(next);
  }
  return body;
}

export function renderScreenGuide(routeId) {
  const catalog = getHelpCatalog();
  const screens = (catalog && catalog.screens) || {};
  const meta = screens[routeId];

  document.querySelectorAll(".help-screen-open").forEach(function (btn) {
    btn.remove();
  });

  document.querySelectorAll(".screen-guide-panel").forEach(function (el) {
    const rid = el.dataset.screenGuide;
    const active = rid === routeId;
    el.hidden = !active;
    el.replaceChildren();
    if (!active) return;
    if (rid === "block-editor" && meta && meta.empty_state) {
      const empty = document.createElement("p");
      empty.className = "screen-guide-empty";
      empty.id = "beEmptyBanner";
      empty.textContent = meta.empty_state;
      el.appendChild(empty);
    }
  });

  if (!meta) return;

  const panel = document.querySelector('.route-panel[data-route="' + routeId + '"]');
  if (!panel) return;

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "help-screen-open secondary";
  setHelpTriggerLabel(btn, "Guia: " + (meta.title || routeId));
  btn.addEventListener("click", function () {
    openHelpDrawer({
      title: "Guia: " + (meta.title || routeId),
      content: buildScreenGuideBody(meta),
      trigger: btn,
    });
  });
  panel.appendChild(btn);
}