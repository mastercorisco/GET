import { createDevelopmentPointCard } from "../components/development-point-card.js";
import { loadHelpCatalog, setHelpLevel } from "../components/field-help.js";

let activeBlockId = null;

async function api(path, options, fallback) {
  const res = await fetch(path, options || {});
  const body = res.ok ? await res.json().catch(function () { return null; }) : await res.json().catch(function () { return {}; });
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
      "/api/blocks/" + activeBlockId + "/exchange-package?include_draft=" + (inc ? "true" : "false"),
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
      "/api/blocks/" + activeBlockId + "/exchange-package?include_draft=" + (inc ? "true" : "false"),
      { method: "POST" },
      "Falha ao exportar."
    ).then(function (data) {
      const st = document.getElementById("beStatus");
      if (st) st.textContent = "Exportado: " + data.file_path;
    });
  });

  loadHelpCatalog();
  api("/api/workspace/preferences", {}, "").then(function (prefs) {
    setHelpLevel(prefs.help_level);
  }).catch(function () {});

  api("/api/catalogs/development-point-templates", {}, "").then(function (data) {
    const sel = document.getElementById("beTemplate");
    if (!sel) return;
    (data.templates || []).forEach(function (t) {
      const o = document.createElement("option");
      o.value = t.id;
      o.textContent = t.name;
      sel.appendChild(o);
    });
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
}

function refreshBlockEditor() {
  const root = document.getElementById("block-editor-root");
  if (!root || !activeBlockId) {
    if (root) root.textContent = "Seleccione um bloco na estrutura documental.";
    return;
  }
  api("/api/blocks/" + activeBlockId, {}, "Falha ao carregar bloco.").then(function (data) {
    const hdr = document.getElementById("beHeader");
    const b = data.block;
  if (hdr) {
      hdr.textContent =
        b.display_code + " — " + b.title + " · " + b.block_status;
    }
    document.getElementById("beObjective").value = b.objective || "";
    document.getElementById("beScope").value = b.scope || "";

    const list = document.getElementById("bePointList");
    list.replaceChildren();
    const hooks = {
      loadDetail: function (id) {
        return api("/api/development-points/" + id, {}, "Falha ao carregar ponto.");
      },
      savePoint: function (id, patch) {
        return api("/api/development-points/" + id, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(patch),
        }, "Falha ao guardar.");
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
  });

  const obj = document.getElementById("beObjective");
  const sc = document.getElementById("beScope");
  function saveHeader() {
    api(
      "/api/blocks/" + activeBlockId,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ objective: obj.value, scope: sc.value }),
      },
      "Falha ao guardar bloco."
    );
  }
  obj.onchange = saveHeader;
  sc.onchange = saveHeader;
}