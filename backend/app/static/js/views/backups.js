import { apiErrorMessage } from "../api/client.js";

export function initBackupsView() {
  const listEl = document.getElementById("backupList");
  const createBtn = document.getElementById("backupCreateCritical");
  const statusEl = document.getElementById("backupStatus");
  if (!listEl || !createBtn) return;

  function setStatus(msg, isError) {
    if (!statusEl) return;
    statusEl.hidden = !msg;
    statusEl.textContent = msg || "";
    statusEl.className = isError ? "error" : "";
  }

  async function refresh() {
    try {
      const res = await fetch("/api/backups");
      const body = await res.json().catch(function () {
        return {};
      });
      if (!res.ok) throw new Error(apiErrorMessage(body, "Falha ao listar backups."));
      listEl.replaceChildren();
      if (!body.length) {
        const p = document.createElement("p");
        p.className = "empty-state";
        p.textContent = "Nenhum backup registado.";
        listEl.appendChild(p);
        return;
      }
      body.forEach(function (row) {
        const line = document.createElement("p");
        line.textContent = row.tier + " · " + row.created_at + " · " + (row.path || row.id);
        listEl.appendChild(line);
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