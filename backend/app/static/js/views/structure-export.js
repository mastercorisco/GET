import { apiErrorMessage } from "../api/client.js";

export function initStructureExportView() {
  const formatSel = document.getElementById("docExportFormat");
  const blockModel = document.getElementById("docExportBlockModel");
  const pointRadios = document.querySelectorAll('input[name="docExportPoints"]');
  const premises = document.getElementById("docExportPremises");
  const rootHint = document.getElementById("docExportRootHint");
  const btn = document.getElementById("docExportBtn");
  const statusEl = document.getElementById("docExportStatus");
  if (!formatSel || !btn) return;

  let selectedRootId = null;

  function setStatus(msg, isError) {
    if (!statusEl) return;
    statusEl.hidden = !msg;
    statusEl.textContent = msg || "";
    statusEl.className = isError ? "error" : "";
  }

  function refreshRootHint() {
    if (!rootHint) return;
    const meta = document.getElementById("docSelectedMeta");
    const code = meta && meta.dataset.displayCode;
    const title = meta && meta.textContent;
    if (selectedRootId && title) {
      rootHint.textContent = "Subárvore: " + title;
    } else {
      rootHint.textContent = "Raiz: projecto completo (nenhum nó seleccionado na árvore).";
    }
  }

  document.addEventListener("get:document-node-selected", function (ev) {
    const node = ev.detail && ev.detail.node;
    selectedRootId = node ? node.id : null;
    refreshRootHint();
  });

  function selectedPointDetail() {
    let val = "none";
    pointRadios.forEach(function (r) {
      if (r.checked) val = r.value;
    });
    return val;
  }

  btn.addEventListener("click", function () {
    setStatus("");
    const pActive = document.getElementById("pActive");
    const projectId = pActive && pActive.value;
    if (!projectId) {
      setStatus("Seleccione o projecto activo no ecrã Projectos.", true);
      return;
    }
    const detail = selectedPointDetail();
    const body = {
      format: formatSel.value,
      include_block_model: !!(blockModel && blockModel.checked),
      point_detail: detail,
      include_point_premises: !!(premises && premises.checked && detail === "full"),
    };
    if (selectedRootId) body.root_node_id = selectedRootId;

    fetch("/api/projects/" + encodeURIComponent(projectId) + "/document-structure/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (b) {
            throw new Error(apiErrorMessage(b, "Exportação falhou."));
          });
        }
        const disp = res.headers.get("Content-Disposition") || "";
        const match = /filename="([^"]+)"/.exec(disp);
        const fileName = match ? match[1] : "estrutura." + formatSel.value;
        return res.blob().then(function (blob) {
          return { blob: blob, fileName: fileName };
        });
      })
      .then(function (payload) {
        const url = URL.createObjectURL(payload.blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = payload.fileName;
        a.click();
        URL.revokeObjectURL(url);
        setStatus("Ficheiro transferido.");
      })
      .catch(function (err) {
        setStatus(err.message, true);
      });
  });

  refreshRootHint();
}