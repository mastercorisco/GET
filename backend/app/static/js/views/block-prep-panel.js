import { getHelpCatalog, openHelpModal } from "../components/help-ui.js";

let _blockId = null;
let _router = null;

export function initBlockPrepPanel(router) {
  _router = router;
  document.querySelectorAll(".prep-tab-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const tab = btn.dataset.prepTab;
      document.querySelectorAll(".prep-tab-btn").forEach(function (b) {
        b.classList.toggle("is-active", b.dataset.prepTab === tab);
      });
      document.querySelectorAll(".prep-tab-panel").forEach(function (p) {
        p.hidden = p.dataset.prepPanel !== tab;
      });
    });
  });
}

export function refreshBlockPrepPanel(blockId, validation) {
  _blockId = blockId;
  const catalog = getHelpCatalog() || {};
  const wf = catalog.workflows || {};
  const concepts = catalog.concepts || {};

  const checklist = document.getElementById("prepChecklist");
  if (checklist && wf.user_controls) {
    checklist.replaceChildren();
    wf.user_controls.forEach(function (item) {
      const li = document.createElement("li");
      li.textContent = item;
      checklist.appendChild(li);
    });
  }
  const llmRole = document.getElementById("prepLlmRole");
  if (llmRole) {
    llmRole.textContent = wf.llm_role || "";
  }

  const conceptsEl = document.getElementById("prepConcepts");
  if (conceptsEl) {
    conceptsEl.replaceChildren();
    Object.keys(concepts).forEach(function (key) {
      const c = concepts[key];
      const d = document.createElement("details");
      const s = document.createElement("summary");
      s.textContent = c.label || key;
      d.appendChild(s);
      const p = document.createElement("p");
      p.textContent = c.summary || "";
      d.appendChild(p);
      conceptsEl.appendChild(d);
    });
  }

  const valEl = document.getElementById("prepValidation");
  if (valEl && validation) {
    valEl.replaceChildren();
    const issues = validation.issues || [];
    if (!issues.length) {
      valEl.textContent = "Sem avisos ou erros.";
      return;
    }
    issues.forEach(function (issue) {
      const line = document.createElement("p");
      line.className =
        issue.severity === "error" ? "error" : issue.severity === "warning" ? "warn-line" : "";
      line.textContent = "[" + issue.severity + "] " + issue.message;
      if (issue.point_id) {
        line.dataset.pointId = issue.point_id;
        line.style.cursor = "pointer";
        line.addEventListener("click", function () {
          const card = document.querySelector('[data-point-id="' + issue.point_id + '"]');
          if (card) {
            const toggle = card.querySelector(".dp-card-toggle");
            if (toggle) toggle.click();
            card.scrollIntoView({ block: "nearest" });
          }
        });
      }
      valEl.appendChild(line);
    });
  }
}

export function loadBlockValidation(blockId) {
  if (!blockId) return Promise.resolve();
  return fetch("/api/blocks/" + blockId + "/validation")
    .then(function (r) {
      return r.ok ? r.json() : { issues: [] };
    })
    .then(function (data) {
      refreshBlockPrepPanel(blockId, data);
    });
}