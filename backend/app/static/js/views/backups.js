import { apiErrorMessage } from "../api/client.js";

function formatDate(iso) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleString("pt-PT");
  } catch (_e) {
    return String(iso);
  }
}

function shortPath(filePath) {
  if (!filePath) return "";
  const parts = String(filePath).replace(/\\/g, "/").split("/");
  return parts.length > 2 ? "…/" + parts.slice(-2).join("/") : filePath;
}

function addDetailRow(dl, label, value) {
  const dt = document.createElement("dt");
  dt.textContent = label;
  const dd = document.createElement("dd");
  dd.textContent = value == null || value === "" ? "—" : String(value);
  dl.appendChild(dt);
  dl.appendChild(dd);
}

function fillDetailPanel(panel, row, previewApi) {
  panel.replaceChildren();
  const dl = document.createElement("dl");
  addDetailRow(dl, "ID", row.id);
  addDetailRow(dl, "Tier", row.tier);
  addDetailRow(dl, "Criado", formatDate(row.created_at));
  addDetailRow(dl, "Ficheiro", row.file_path);
  addDetailRow(dl, "sha256", row.sha256);
  const meta = row.preview_meta_json || {};
  if (meta.workspace_settings_rows != null) {
    addDetailRow(dl, "workspace_settings (ao criar)", meta.workspace_settings_rows);
  }
  if (meta.backup_record_rows != null) {
    addDetailRow(dl, "backup_record (ao criar)", meta.backup_record_rows);
  }
  if (previewApi) {
    addDetailRow(dl, "workspace_settings (ficheiro)", previewApi.workspace_settings_rows);
    addDetailRow(dl, "backup_record (ficheiro)", previewApi.backup_record_rows);
    if (previewApi.file_path && previewApi.file_path !== row.file_path) {
      addDetailRow(dl, "Caminho no ficheiro", previewApi.file_path);
    }
  }
  panel.appendChild(dl);
}

export function initBackupsView() {
  const listEl = document.getElementById("backupList");
  const createBtn = document.getElementById("backupCreateCritical");
  const statusEl = document.getElementById("backupStatus");
  if (!listEl || !createBtn) return;

  let expandedId = null;

  function setStatus(msg, isError) {
    if (!statusEl) return;
    statusEl.hidden = !msg;
    statusEl.textContent = msg || "";
    statusEl.className = "backups-panel__status" + (isError ? " error" : "");
  }

  function collapseAll(exceptId) {
    listEl.querySelectorAll(".backup-item").forEach(function (wrap) {
      const id = wrap.dataset.backupId;
      const open = exceptId != null && id === exceptId;
      wrap.classList.toggle("is-expanded", open);
      const detail = wrap.querySelector(".backup-row__detail");
      const detBtn = wrap.querySelector("[data-action='details']");
      if (detail) detail.hidden = !open;
      if (detBtn) detBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    expandedId = exceptId != null ? exceptId : null;
  }

  function toggleRow(wrap, row) {
    const detail = wrap.querySelector(".backup-row__detail");
    if (!detail) return;

    const isOpen = expandedId === row.id && !detail.hidden;
    if (isOpen) {
      collapseAll(null);
      setStatus("");
      return;
    }

    collapseAll(row.id);
    fillDetailPanel(detail, row, null);
    detail.hidden = false;

    setStatus("A carregar…");
    fetch("/api/backups/" + encodeURIComponent(row.id) + "/preview")
      .then(function (res) {
        return res.json().then(function (b) {
          return { ok: res.ok, body: b };
        });
      })
      .then(function (result) {
        if (!result.ok) {
          throw new Error(apiErrorMessage(result.body, "Falha ao ler o ficheiro de backup."));
        }
        if (expandedId === row.id) {
          fillDetailPanel(detail, row, result.body);
        }
        setStatus("");
      })
      .catch(function (err) {
        setStatus(err.message, true);
      });
  }

  async function refresh() {
    try {
      setStatus("");
      expandedId = null;
      const res = await fetch("/api/backups");
      const body = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(apiErrorMessage(body, "Falha ao listar backups."));
      listEl.replaceChildren();
      if (!body.length) {
        const p = document.createElement("p");
        p.className = "empty-state";
        p.style.fontSize = "0.85rem";
        p.textContent = "Nenhum backup registado.";
        listEl.appendChild(p);
        return;
      }
      body.forEach(function (row) {
        const wrap = document.createElement("div");
        wrap.className = "backup-item";
        wrap.dataset.backupId = row.id;

        const item = document.createElement("div");
        item.className = "backup-row";

        const main = document.createElement("div");
        main.className = "backup-row__main";

        const meta = row.preview_meta_json || {};
        const metaBit =
          meta.workspace_settings_rows != null ? " · ws=" + meta.workspace_settings_rows : "";

        const head = document.createElement("p");
        head.className = "backup-row__meta";
        head.textContent =
          row.tier + " · " + formatDate(row.created_at) + metaBit + " · " + shortPath(row.file_path);
        main.appendChild(head);

        const sha = document.createElement("p");
        sha.className = "backup-row__sha";
        sha.textContent = (row.sha256 || "").slice(0, 12) + "…";
        main.appendChild(sha);

        const actions = document.createElement("div");
        actions.className = "backup-row__actions";

        const detailsBtn = document.createElement("button");
        detailsBtn.type = "button";
        detailsBtn.className = "secondary";
        detailsBtn.dataset.action = "details";
        detailsBtn.setAttribute("aria-expanded", "false");
        detailsBtn.textContent = "Detalhes";
        detailsBtn.addEventListener("click", function () {
          toggleRow(wrap, row);
        });

        const restoreBtn = document.createElement("button");
        restoreBtn.type = "button";
        restoreBtn.className = "secondary";
        restoreBtn.textContent = "Restaurar";
        restoreBtn.addEventListener("click", function () {
          const ok = window.confirm(
            "Restaurar este backup?\n\nSubstitui get.db. Feche import/consolidate antes.\n\nCria backup pre_restore_guard_*."
          );
          if (!ok) return;
          setStatus("A restaurar…");
          fetch("/api/backups/" + encodeURIComponent(row.id) + "/restore?confirm=true", {
            method: "POST",
          })
            .then(function (res) {
              return res.json().then(function (b) {
                return { ok: res.ok, body: b };
              });
            })
            .then(function (result) {
              if (!result.ok) {
                throw new Error(apiErrorMessage(result.body, "Falha no restauro."));
              }
              setStatus("Restauro concluído. A recarregar…", false);
              window.setTimeout(function () {
                window.location.reload();
              }, 800);
            })
            .catch(function (err) {
              setStatus(err.message, true);
            });
        });

        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.className = "secondary danger backups-row__delete";
        deleteBtn.textContent = "Apagar";
        deleteBtn.addEventListener("click", function () {
          const ok = window.confirm(
            "Apagar este backup?\n\nRemove o registo e o ficheiro .db no disco. Não afecta a base actual do workspace."
          );
          if (!ok) return;
          setStatus("A apagar…");
          const discardUrl = "/api/backups/" + encodeURIComponent(row.id) + "/discard";
          fetch(discardUrl, { method: "POST" })
            .then(function (res) {
              if (res.status === 204) return null;
              return res.json().then(function (b) {
                const msg = apiErrorMessage(b, "Falha ao apagar backup.");
                if (res.status === 404 && (msg === "Not Found" || msg === "not found")) {
                  throw new Error(
                    "Servidor desatualizado (rota de apagar backup em falta). Reinicie o Arranque GET.bat e Ctrl+F5."
                  );
                }
                throw new Error(msg);
              });
            })
            .then(function () {
              if (expandedId === row.id) expandedId = null;
              setStatus("Backup apagado.");
              return refresh();
            })
            .catch(function (err) {
              setStatus(err.message, true);
            });
        });

        actions.appendChild(detailsBtn);
        actions.appendChild(restoreBtn);
        actions.appendChild(deleteBtn);
        item.appendChild(main);
        item.appendChild(actions);

        const detail = document.createElement("div");
        detail.className = "backup-row__detail";
        detail.hidden = true;

        wrap.appendChild(item);
        wrap.appendChild(detail);
        listEl.appendChild(wrap);
      });
    } catch (err) {
      setStatus(err.message, true);
    }
  }

  createBtn.addEventListener("click", function () {
    setStatus("");
    fetch("/api/backups", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tier: "critical" }),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (result) {
        if (!result.ok) throw new Error(apiErrorMessage(result.body, "Falha ao criar backup."));
        setStatus("Backup crítico criado.");
        return refresh();
      })
      .catch(function (err) {
        setStatus(err.message, true);
      });
  });

  document.addEventListener("get:workspace-open", refresh);
}