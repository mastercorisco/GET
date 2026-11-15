import { getHelpCatalog } from "./help-ui.js";

const ROUTE_LABELS = {
  library: "Biblioteca",
  project: "Projecto",
  "project-structure": "Estrutura documental",
  "block-editor": "Preparação do bloco",
  export: "Exportar",
  import: "Reimportar",
};

export function renderScreenGuide(routeId) {
  const catalog = getHelpCatalog();
  const screens = (catalog && catalog.screens) || {};
  const meta = screens[routeId];
  document.querySelectorAll(".screen-guide-panel").forEach(function (el) {
    const rid = el.dataset.screenGuide;
    const active = rid === routeId;
    el.hidden = !active;
    if (!active || !meta) return;
    el.replaceChildren();
    el.classList.add("screen-guide-panel--compact");
    const details = document.createElement("details");
    details.className = "compact-section compact-section--screen-guide";
    const summary = document.createElement("summary");
    summary.textContent = "Guia: " + (meta.title || routeId);
    details.appendChild(summary);
    const body = document.createElement("div");
    body.className = "compact-section__body";
    if (meta.objective) {
      const p = document.createElement("p");
      p.className = "lead";
      p.textContent = meta.objective;
      body.appendChild(p);
    }
    if (meta.steps && meta.steps.length) {
      const ol = document.createElement("ol");
      ol.className = "screen-guide-steps";
      meta.steps.forEach(function (step) {
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
    details.appendChild(body);
    el.appendChild(details);
    if (rid === "block-editor" && meta.empty_state) {
      const empty = document.createElement("p");
      empty.className = "screen-guide-empty";
      empty.id = "beEmptyBanner";
      empty.textContent = meta.empty_state;
      el.appendChild(empty);
    }
  });
}