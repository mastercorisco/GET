import { getHelpCatalog, getHelpLevel, openHelpModal, openMethodOverview } from "../components/help-ui.js";

let _blockId = null;
let _router = null;
let _methodBtnWired = false;

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
  const methodBtn = document.getElementById("prepMethodOpen");
  if (methodBtn && !_methodBtnWired) {
    methodBtn.addEventListener("click", function () {
      openMethodOverview({ trigger: methodBtn });
    });
    _methodBtnWired = true;
  }
}

export function refreshBlockPrepPanel(blockId, validation) {
  _blockId = blockId;
  const catalog = getHelpCatalog() || {};
  const wf = catalog.workflows || {};
  const concepts = catalog.concepts || {};
  const method = catalog.method || {};
  const helpLevel = getHelpLevel();

  const methodSummary = document.getElementById("prepMethodSummary");
  if (methodSummary && method.principle) {
    methodSummary.textContent = method.principle;
  }

  const flowEl = document.getElementById("prepMethodFlow");
  if (flowEl && method.flow_steps) {
    flowEl.replaceChildren();
    method.flow_steps.forEach(function (step, i) {
      const li = document.createElement("li");
      li.textContent = step;
      if (i < method.flow_steps.length - 1) {
        li.className = "method-flow-step";
      }
      flowEl.appendChild(li);
    });
  }

  const boundariesEl = document.getElementById("prepLlmBoundaries");
  if (boundariesEl && wf.method_llm_boundaries) {
    boundariesEl.replaceChildren();
    const ul = document.createElement("ul");
    ul.className = "prep-boundaries";
    wf.method_llm_boundaries.forEach(function (line) {
      const li = document.createElement("li");
      li.textContent = line;
      ul.appendChild(li);
    });
    boundariesEl.appendChild(ul);
  }

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
      p.textContent = c.role_in_get || c.summary || "";
      d.appendChild(p);
      if (helpLevel === "detailed" && c.not_this) {
        const nt = document.createElement("p");
        nt.className = "field-help-bad";
        nt.textContent = "Não é: " + c.not_this;
        d.appendChild(nt);
      }
      conceptsEl.appendChild(d);
    });
  }

  const guideEl = document.getElementById("prepExportKindGuide");
  const guide = workflows.export_kind_guide || [];
  if (guideEl && guide.length) {
    guideEl.replaceChildren();
    const gt = document.createElement("p");
    gt.className = "field-help-section-title";
    gt.textContent = "Qual exportação usar?";
    guideEl.appendChild(gt);
    if (method.export_decision_summary) {
      const sum = document.createElement("p");
      sum.className = "choice-hint";
      sum.textContent = method.export_decision_summary;
      guideEl.appendChild(sum);
    }
    const ul = document.createElement("ul");
    ul.className = "prep-export-guide";
    guide.forEach(function (row) {
      const li = document.createElement("li");
      li.textContent = row.need + " → " + row.use;
      ul.appendChild(li);
    });
    guideEl.appendChild(ul);
  }

  const exchEl = document.getElementById("prepExchangeSemantics");
  const sem = method.exchange_semantics || {};
  if (exchEl && Object.keys(sem).length) {
    exchEl.replaceChildren();
    const labels = {
      authoritative_content: "Autoritativo",
      supporting_context: "Suporte",
      unresolved_matters: "Em aberto",
      generation_instructions: "Instruções LLM",
    };
    Object.keys(labels).forEach(function (k) {
      if (!sem[k]) return;
      const dt = document.createElement("p");
      dt.className = "field-help-section-title";
      dt.textContent = labels[k];
      exchEl.appendChild(dt);
      const dd = document.createElement("p");
      dd.textContent = sem[k];
      exchEl.appendChild(dd);
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