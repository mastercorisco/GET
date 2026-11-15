import { createDevelopmentPointCard } from "../components/development-point-card.js";
import { wireLocalHelpDrawer } from "../components/help-drawer.js";
import { wireDeclarativeHelp } from "../components/help-ui.js";
import {
  initBlockPrepPanel,
  loadBlockValidation,
  refreshBlockPrepPanel,
} from "./block-prep-panel.js";

let activeBlockId = null;
let headerWired = false;
let _templates = [];

const TARGET_OUTPUT_PRESETS = [
  {
    label: "— Não definido —",
    value: {},
    description: "Sem indicação de formato; a LLM desenvolve só a partir dos pontos.",
  },
  {
    label: "Secção de especificação (capítulo ESF)",
    value: {
      format: "spec_section",
      language: "pt-PT",
      tone: "formal_technical",
    },
    description:
      "Capítulo para o fascículo: estrutura de ESF com títulos e requisitos em prosa técnica.",
  },
  {
    label: "Especificação técnica aprofundada",
    value: {
      format: "technical_specification",
      language: "pt-PT",
      tone: "formal_technical",
      indicative_length_words: 1200,
    },
    description:
      "Documento formal mais longo (~1200 palavras indicativas); não é só um capítulo curto.",
  },
  {
    label: "Tabela de requisitos",
    value: {
      format: "requirements_table",
      language: "pt-PT",
      tone: "formal_technical",
    },
    description: "Saída tabular (requisito, critério, notas) para rastreabilidade e revisão.",
  },
  {
    label: "Texto funcional (narrativa)",
    value: {
      format: "functional_narrative",
      language: "pt-PT",
      tone: "clear_operational",
    },
    description:
      "Narrativa sobre comportamento e operação; menos rigor de capítulo ESF.",
  },
  {
    label: "Esboço para discussão (perfil discussion)",
    value: {
      format: "discussion_outline",
      language: "pt-PT",
      tone: "collaborative",
      indicative_length_words: 400,
    },
    description:
      "Resposta breve para iterar ideias com a LLM antes da redação final.",
  },
];

/** Dados antigos com `kind: spec_section` alinham ao preset `format`. */
function normalizeTargetOutputForUi(obj) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) return {};
  if (Object.keys(obj).length === 1 && obj.kind === "spec_section") {
    return { format: "spec_section" };
  }
  return obj;
}

function stableTargetOutputKey(obj) {
  const normalized = obj && typeof obj === "object" && !Array.isArray(obj) ? obj : {};
  const sorted = {};
  Object.keys(normalized)
    .sort()
    .forEach(function (k) {
      sorted[k] = normalized[k];
    });
  return JSON.stringify(sorted);
}

function parseTargetOutputSelectValue(raw) {
  try {
    const parsed = JSON.parse(raw || "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : {};
  } catch (_e) {
    return {};
  }
}

function isKnownTargetOutputKey(key) {
  if (key === "{}") return true;
  return TARGET_OUTPUT_PRESETS.some(function (p) {
    return stableTargetOutputKey(p.value) === key;
  });
}

function resolveTargetOutputSelectKey(currentObj) {
  const normalized = normalizeTargetOutputForUi(currentObj);
  const exact = stableTargetOutputKey(normalized);
  if (isKnownTargetOutputKey(exact)) return exact;
  const fmt = normalized.format;
  if (fmt) {
    const candidates = TARGET_OUTPUT_PRESETS.filter(function (p) {
      return p.value.format === fmt;
    });
    if (candidates.length === 1) {
      return stableTargetOutputKey(candidates[0].value);
    }
    if (candidates.length > 1 && Object.keys(normalized).length === 1) {
      return stableTargetOutputKey(candidates[0].value);
    }
  }
  return exact;
}

function updateTargetOutputHint(select) {
  const hint = document.getElementById("beTargetOutputHint");
  if (!hint || !select) return;
  const key = select.value;
  const preset = TARGET_OUTPUT_PRESETS.find(function (p) {
    return stableTargetOutputKey(p.value) === key;
  });
  if (preset?.description) {
    hint.textContent = preset.description;
    hint.hidden = false;
  } else if (key !== "{}") {
    hint.textContent = "Valor guardado que não corresponde a um formato standard.";
    hint.hidden = false;
  } else {
    hint.hidden = true;
    hint.textContent = "";
  }
}

function syncTargetOutputSelect(select, currentObj) {
  if (!select) return;
  if (!select.dataset.presetsBuilt) {
    select.replaceChildren();
    TARGET_OUTPUT_PRESETS.forEach(function (p) {
      const opt = document.createElement("option");
      opt.value = stableTargetOutputKey(p.value);
      opt.textContent = p.label;
      select.appendChild(opt);
    });
    select.dataset.presetsBuilt = "1";
  }
  select.querySelectorAll("option[data-custom]").forEach(function (o) {
    o.remove();
  });
  const normalized = normalizeTargetOutputForUi(currentObj);
  const storedKey = stableTargetOutputKey(normalized);
  const resolvedKey = resolveTargetOutputSelectKey(currentObj);
  if (!isKnownTargetOutputKey(storedKey) && storedKey !== "{}") {
    const opt = document.createElement("option");
    opt.value = storedKey;
    opt.textContent = "Personalizado (valor guardado)";
    opt.dataset.custom = "1";
    select.appendChild(opt);
    select.value = storedKey;
  } else {
    select.value = resolvedKey;
  }
  updateTargetOutputHint(select);
}

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

function initBlockPrepHelpDrawer() {
  const host = document.getElementById("block-editor-root");
  wireLocalHelpDrawer(host, {
    aside: document.getElementById("blockPrepAside"),
    openBtn: document.getElementById("bePrepHelpOpen"),
    closeBtn: document.getElementById("bePrepHelpClose"),
  });
}

export function initBlockEditor(router) {
  const root = document.getElementById("block-editor-root");
  if (!root) return;

  initBlockPrepHelpDrawer();
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
    syncTargetOutputSelect(tgt, {});
    function saveHeader() {
      if (!activeBlockId) return;
      const target_output = parseTargetOutputSelectValue(tgt?.value);
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
    tgt?.addEventListener("change", function () {
      updateTargetOutputHint(tgt);
      saveHeader();
    });
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
      p.className = "template-card-desc";
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
      const row = document.createElement("div");
      row.className = "be-premise-row list-item-row";
      const text = document.createElement("span");
      text.textContent =
        "[" + prem.importance + "] " + prem.statement + " (" + prem.confidence + ")";
      row.appendChild(text);
      const del = document.createElement("button");
      del.type = "button";
      del.className = "secondary danger";
      del.textContent = "Apagar";
      del.addEventListener("click", function () {
        if (!window.confirm("Apagar esta premissa?")) return;
        api("/api/premises/" + prem.id, { method: "DELETE" }, "Falha ao apagar.").then(refreshBlockPremises);
      });
      row.appendChild(del);
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
    if (tgt) syncTargetOutputSelect(tgt, b.target_output || {});

    const countEl = document.getElementById("bePointsCount");
    if (countEl) {
      const n = data.points ? data.points.length : 0;
      countEl.textContent = n ? "(" + n + ")" : "(nenhum)";
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
          if (kind === "delete") {
            return api("/api/development-points/" + id, { method: "DELETE" }, "Falha ao eliminar.").then(
              refreshBlockEditor
            );
          }
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