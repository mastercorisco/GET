import { createDevelopmentPointCard } from "../components/development-point-card.js";
import { wireDeclarativeHelp } from "../components/help-ui.js";
import {
  initBlockPrepPanel,
  loadBlockValidation,
  refreshBlockPrepPanel,
} from "./block-prep-panel.js";

let activeBlockId = null;
let headerWired = false;
let _templates = [];

async function api(path, options, fallback) {
  const res = await fetch(path, options || {});
  const body = res.ok
    ? await res.json().catch(function () {
        return null;
      })
    : await res.json().catch(function () {
        return {};
      });
  if (!res.ok) {
    throw new Error((body && body.detail) || fallback || res.statusText);
  }
  return body;
}

export function openBlockEditor(blockId, router) {
  activeBlockId = blockId;
  if (router && router.navigate) {
    router.navigate("block-editor");
  }
  refreshBlockEditor();
}

export function initBlockEditor(router) {
  const root = document.getElementById("block-editor-root");
  if (!root) return;

  initBlockPrepPanel(router);

  document.getElementById("beRefresh")?.addEventListener("click", refreshBlockEditor);
  document.getElementById("beNewPoint")?.addEventListener("click", function () {
    if (!activeBlockId) return;
    const tpl = document.getElementById("beTemplate")?.value || "";
    api(
      "/api/blocks/" + activeBlockId + "/development-points",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "", template_id: tpl || null }),
      },
      "Falha ao criar ponto."
    ).then(refreshBlockEditor);
  });
  document.getElementById("beExportPreview")?.addEventListener("click", function () {
    if (!activeBlockId) return;
    const inc = document.getElementById("beIncludeDraft")?.checked;
    api(
      "/api/blocks/" +
        activeBlockId +
        "/exchange-package?include_draft=" +
        (inc ? "true" : "false"),
      {},
      "Falha na pré-visualização."
    ).then(function (data) {
      const pre = document.getElementById("bePreview");
      if (pre) pre.textContent = JSON.stringify(data, null, 2);
    });
  });
  document.getElementById("beExportWrite")?.addEventListener("click", function () {
    if (!activeBlockId) return;
    const inc = document.getElementById("beIncludeDraft")?.checked;
    api(
      "/api/blocks/" +
        activeBlockId +
        "/exchange-package?include_draft=" +
        (inc ? "true" : "false"),
      { method: "POST" },
      "Falha ao exportar."
    ).then(function (data) {
      const st = document.getElementById("beStatus");
      if (st) st.textContent = "Exportado: " + data.file_path;
    });
  });

  document.getElementById("bePremiseAdd")?.addEventListener("click", function () {
    if (!activeBlockId) return;
    const statement = document.getElementById("bePremiseStatement")?.value?.trim();
    if (!statement) return;
    api(
      "/api/premises",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          owner_kind: "block",
          owner_id: activeBlockId,
          statement: statement,
          importance: document.getElementById("bePremiseImportance")?.value,
          source_type: document.getElementById("bePremiseSource")?.value,
          confidence: document.getElementById("bePremiseConfidence")?.value,
        }),
      },
      "Falha ao criar premissa."
    ).then(function () {
      const ta = document.getElementById("bePremiseStatement");
      if (ta) ta.value = "";
      refreshBlockPremises();
    });
  });

  api("/api/catalogs/development-point-templates", {}, "").then(function (data) {
    _templates = data.templates || [];
    const sel = document.getElementById("beTemplate");
    if (sel) {
      _templates.forEach(function (t) {
        const o = document.createElement("option");
        o.value = t.id;
        o.textContent = t.name;
        sel.appendChild(o);
      });
    }
    renderTemplateCards();
  });

  const list = document.getElementById("bePointList");
  if (list) {
    list.addEventListener("dragover", function (ev) {
      ev.preventDefault();
    });
    list.addEventListener("drop", function (ev) {
      ev.preventDefault();
      const dragged = ev.dataTransfer.getData("text/plain");
      const cards = [...list.querySelectorAll(".dp-card")];
      const order = cards.map(function (c) {
        return c.dataset.pointId;
      });
      const from = order.indexOf(dragged);
      if (from < 0) return;
      order.splice(from, 1);
      const target = ev.target.closest(".dp-card");
      if (target) {
        const to = order.indexOf(target.dataset.pointId);
        order.splice(to, 0, dragged);
      } else {
        order.push(dragged);
      }
      api(
        "/api/blocks/" + activeBlockId + "/development-points/reorder",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ point_ids: order }),
        },
        "Falha a reordenar."
      ).then(refreshBlockEditor);
    });
  }

  if (!headerWired) {
    headerWired = true;
    const obj = document.getElementById("beObjective");
    const sc = document.getElementById("beScope");
    const tgt = document.getElementById("beTargetOutput");
    function saveHeader() {
      if (!activeBlockId) return;
      let target_output = {};
      try {
        target_output = JSON.parse(tgt?.value || "{}");
      } catch (_e) {
        target_output = {};
      }
      api(
        "/api/blocks/" + activeBlockId,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            objective: obj?.value,
            scope: sc?.value,
            target_output: target_output,
          }),
        },
        "Falha ao guardar bloco."
      );
    }
    obj?.addEventListener("change", saveHeader);
    sc?.addEventListener("change", saveHeader);
    tgt?.addEventListener("change", saveHeader);
  }
}

function renderTemplateCards() {
  const wrap = document.getElementById("beTemplateCards");
  const sel = document.getElementById("beTemplate");
  if (!wrap || !sel) return;
  wrap.replaceChildren();
  _templates.forEach(function (t) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "template-card secondary card-surface";
    card.dataset.templateId = t.id;
    const title = document.createElement("strong");
    title.textContent = t.name;
    card.appendChild(title);
    if (t.description) {
      const p = document.createElement("p");
      p.textContent = t.description;
      card.appendChild(p);
    }
    card.addEventListener("click", function () {
      sel.value = t.id;
      wrap.querySelectorAll(".template-card").forEach(function (c) {
        c.classList.toggle("is-selected", c.dataset.templateId === t.id);
      });
    });
    wrap.appendChild(card);
  });
}

function refreshBlockPremises() {
  if (!activeBlockId) return Promise.resolve();
  return api(
    "/api/premises?owner_kind=block&owner_id=" + encodeURIComponent(activeBlockId),
    {},
    ""
  ).then(function (rows) {
    const list = document.getElementById("bePremiseList");
    if (!list) return;
    list.replaceChildren();
    (rows || []).forEach(function (prem) {
      const row = document.createElement("p");
      row.className = "be-premise-row";
      row.textContent =
        "[" + prem.importance + "] " + prem.statement + " (" + prem.confidence + ")";
      list.appendChild(row);
    });
  });
}

function refreshBlockEditor() {
  const root = document.getElementById("block-editor-root");
  const empty = document.getElementById("beEmptyHint");
  const banner = document.getElementById("beEmptyBanner");
  if (!activeBlockId) {
    if (root) root.hidden = true;
    if (empty) empty.hidden = false;
    if (banner) banner.hidden = false;
    return;
  }
  if (root) root.hidden = false;
  if (empty) empty.hidden = true;

  wireDeclarativeHelp(document.getElementById("block-editor-root"));

  api("/api/blocks/" + activeBlockId, {}, "Falha ao carregar bloco.").then(function (data) {
    const hdr = document.getElementById("beHeader");
    const b = data.block;
    if (hdr) {
      hdr.textContent = b.display_code + " | " + b.title + " · " + b.block_status;
    }
    const obj = document.getElementById("beObjective");
    const sc = document.getElementById("beScope");
    const tgt = document.getElementById("beTargetOutput");
    if (obj) obj.value = b.objective || "";
    if (sc) sc.value = b.scope || "";
    if (tgt) {
      tgt.value = JSON.stringify(b.target_output || {}, null, 2);
    }

    const list = document.getElementById("bePointList");
    if (list) {
      list.replaceChildren();
      const hooks = {
        loadDetail: function (id) {
          return api("/api/development-points/" + id, {}, "Falha ao carregar ponto.");
        },
        savePoint: function (id, patch) {
          return api(
            "/api/development-points/" + id,
            {
              method: "PATCH",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(patch),
            },
            "Falha ao guardar."
          );
        },
        action: function (id, kind) {
          const path =
            kind === "duplicate"
              ? "/api/development-points/" + id + "/duplicate"
              : "/api/development-points/" + id + "/archive";
          return api(path, { method: "POST" }, "Falha na acção.").then(refreshBlockEditor);
        },
      };
      data.points.forEach(function (p) {
        list.appendChild(createDevelopmentPointCard(p, hooks));
      });
    }

    if (banner) {
      banner.hidden = data.points && data.points.length > 0;
    }

    refreshBlockPrepPanel(activeBlockId, null);
    loadBlockValidation(activeBlockId);
    refreshBlockPremises();
  });
}