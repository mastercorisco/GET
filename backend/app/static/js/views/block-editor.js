import { createDevelopmentPointCard } from "../components/development-point-card.js";
import { wireLocalHelpDrawer } from "../components/help-drawer.js";
import { ensureHelpDrawerTitleIcon, setHelpTriggerLabel } from "../components/help-icon.js";
import { applyPackageBriefTemplate } from "../components/package-brief-notes.js";
import { wireDeclarativeHelp } from "../components/help-ui.js";
import {
  initBlockPrepPanel,
  loadBlockValidation,
  refreshBlockPrepPanel,
} from "./block-prep-panel.js";

let activeBlockId = null;
let headerWired = false;
let _templates = [];
let lastBlockPackageExport = null;

function copyTextToClipboard(text, statusEl, okMsg) {
  if (!text) return Promise.reject(new Error("Sem brief para copiar."));
  const done = function () {
    if (statusEl) statusEl.textContent = okMsg || "Brief copiado.";
  };
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text).then(done);
  }
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.select();
  try {
    if (!document.execCommand("copy")) throw new Error("Cópia não suportada neste browser.");
    done();
    return Promise.resolve();
  } finally {
    document.body.removeChild(ta);
  }
}

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
  const openBtn = document.getElementById("bePrepHelpOpen");
  if (openBtn) setHelpTriggerLabel(openBtn, "Ajuda à preparação");
  const asideHeader = document.querySelector("#blockPrepAside .help-drawer__header h3");
  if (asideHeader) ensureHelpDrawerTitleIcon(asideHeader);
  wireLocalHelpDrawer(host, {
    aside: document.getElementById("blockPrepAside"),
    openBtn: openBtn,
    closeBtn: document.getElementById("bePrepHelpClose"),
  });
}

export function initBlockEditor(router) {
  const root = document.getElementById("block-editor-root");
  if (!root) return;

  document.addEventListener("get:package-consolidated", function (ev) {
    if ((ev.detail && ev.detail.scope_kind) !== "block") return;
    if (activeBlockId) refreshBlockEditor();
  });

  initBlockPrepHelpDrawer();
  initBlockPrepPanel(router);
  applyPackageBriefTemplate("bePkgBriefNotes", "initBlockEditor");

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
  function downloadPackage(filename, text) {
    const blob = new Blob([text], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "GET-bloco.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  function setBeStatus(text, isError) {
    const st = document.getElementById("beStatus");
    if (!st) return;
    st.textContent = text || "";
    st.classList.toggle("be-status--error", !!isError);
    if (text) {
      st.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  function ensureBaselineForPackage(projectId) {
    return api("/api/projects/" + projectId + "/baselines/latest", {}, "Falha ao verificar baseline.").then(
      function (baseline) {
        if (baseline && baseline.id) return baseline;
        const ok = window.confirm(
          "Não há baseline publicada neste projecto. O GET-PACKAGE precisa de uma baseline " +
            "(códigos documentais e conhecimento fixados) para a reimportação.\n\n" +
            "Publicar baseline agora e continuar a exportação?"
        );
        if (!ok) {
          return Promise.reject(
            new Error(
              "Exportação cancelada. Publique uma baseline em Exportar → Publicar baseline " +
                "e volte a exportar o pacote."
            )
          );
        }
        return api(
          "/api/projects/" + projectId + "/baselines/publish",
          { method: "POST" },
          "Falha ao publicar baseline."
        ).then(function (published) {
          document.dispatchEvent(
            new CustomEvent("get:baseline-published", { detail: { project_id: projectId, baseline: published } })
          );
          return published;
        });
      }
    );
  }

  function runBlockPackageExport() {
    if (!activeBlockId) return Promise.reject(new Error("Sem bloco activo."));
    const projectId = document.getElementById("pActive")?.value;
    if (!projectId) return Promise.reject(new Error("Sem projecto."));
    const notesEl = document.getElementById("bePkgBriefNotes");
    const llmNotes = notesEl && notesEl.value ? notesEl.value.trim() : null;
    return ensureBaselineForPackage(projectId).then(function () {
      return api(
      "/api/projects/" + projectId + "/packages/export",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scope_kind: "block",
          node_id: activeBlockId,
          profile: "discussion",
          llm_notes: llmNotes || null,
        }),
      },
        "Falha ao exportar pacote."
      );
    }).then(function (row) {
      lastBlockPackageExport = {
        brief: row.brief || "",
        body: row.body,
        export_id: row.export_id,
      };
      const copyBtn = document.getElementById("bePkgCopyBrief");
      if (copyBtn) copyBtn.disabled = !lastBlockPackageExport.brief;
      downloadPackage(row.filename, row.body);
      setBeStatus("Pacote exportado: " + row.file_path, false);
      return lastBlockPackageExport;
    });
  }

  document.getElementById("bePkgExport")?.addEventListener("click", function () {
    setBeStatus("A exportar pacote…", false);
    runBlockPackageExport().catch(function (err) {
      setBeStatus(err.message, true);
    });
  });

  document.getElementById("bePkgCopyBrief")?.addEventListener("click", function () {
    const st = document.getElementById("beStatus");
    const doCopy = function (exp) {
      copyTextToClipboard(exp.brief, st, "Brief copiado — cole na LLM junto com o JSON.").catch(function (err) {
        if (st) st.textContent = err.message;
      });
    };
    if (lastBlockPackageExport && lastBlockPackageExport.brief) {
      doCopy(lastBlockPackageExport);
      return;
    }
    runBlockPackageExport()
      .then(doCopy)
      .catch(function (err) {
        if (st) st.textContent = err.message;
      });
  });

  document.getElementById("bePkgImportBtn")?.addEventListener("click", function () {
    document.getElementById("bePkgImport")?.click();
  });

  document.getElementById("bePkgImport")?.addEventListener("change", function (ev) {
    if (!activeBlockId) return;
    const projectId = document.getElementById("pActive")?.value;
    const input = ev.target;
    if (!projectId || !input.files?.length) return;
    const file = input.files[0];
    const form = new FormData();
    form.append("file", file, file.name);
    fetch("/api/projects/" + projectId + "/packages/import", { method: "POST", body: form })
      .then(function (res) {
        return res.json().then(function (payload) {
          if (!res.ok) throw new Error(payload.detail || "Ficheiro incompatível.");
          return payload;
        });
      })
      .then(function (payload) {
        const st = document.getElementById("beStatus");
        if (st) st.textContent = "Pacote importado. A abrir Reimportar…";
        input.value = "";
        document.dispatchEvent(
          new CustomEvent("get:package-imported", {
            detail: {
              import_id: payload.import_id,
              project_id: projectId,
              scope_kind: payload.scope_kind || "block",
              auto_review: true,
            },
          })
        );
      })
      .catch(function (err) {
        const st = document.getElementById("beStatus");
        if (st) st.textContent = err.message;
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
      if (st) {
        st.textContent =
          "JSON: " +
          data.file_path +
          (data.markdown_path ? " | MD: " + data.markdown_path : "");
      }
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

  const beRoot = document.getElementById("block-editor-root");
  const pkgBriefLabel = beRoot && beRoot.querySelector('label[data-help-key="block.package_brief"]');
  if (pkgBriefLabel) {
    pkgBriefLabel.querySelector(".field-help-btn")?.remove();
    delete pkgBriefLabel.dataset.helpWired;
  }
  wireDeclarativeHelp(beRoot);
  applyPackageBriefTemplate("bePkgBriefNotes", "refreshBlockEditor");

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
        onPointSaved: function () {
          loadBlockValidation(activeBlockId);
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