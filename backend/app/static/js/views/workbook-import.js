import { apiErrorMessage } from "../api/client.js";

const CONFIRM_PHRASE = "I_UNDERSTAND";

export function initWorkbookImport(router) {
  const tplLib = document.getElementById("wbTplLibrary");
  const tplProj = document.getElementById("wbTplProject");
  const validateBtn = document.getElementById("wbValidateBtn");
  const validateFile = document.getElementById("wbValidateFile");
  const validateOut = document.getElementById("wbValidateOut");
  const migrateFile = document.getElementById("wbMigrateFile");
  const migrateBtn = document.getElementById("wbMigrateBtn");
  const migrateOut = document.getElementById("wbMigrateOut");
  const applyBtn = document.getElementById("wbApplyBtn");
  const applyOut = document.getElementById("wbApplyOut");
  const applyConfirm = document.getElementById("wbApplyConfirm");
  const targetNew = document.getElementById("wbTargetNew");
  const targetExisting = document.getElementById("wbTargetExisting");
  const openProjectBtn = document.getElementById("wbOpenProjectBtn");
  const statusEl = document.getElementById("wbStatus");

  if (!tplLib || !migrateBtn) return;

  let lastRunId = null;
  let lastProjectId = null;

  function setStatus(msg, isError) {
    if (!statusEl) return;
    statusEl.hidden = !msg;
    statusEl.textContent = msg || "";
    statusEl.className = isError ? "error" : "";
  }

  function downloadTemplate(templateId) {
    window.location.href = "/api/workbook/templates/" + encodeURIComponent(templateId);
  }

  function renderIssues(container, body) {
    if (!container) return;
    container.hidden = false;
    const lines = [];
    lines.push("run_id: " + (body.run_id || "—"));
    lines.push("estado: " + (body.status || "—"));
    if (body.counts) {
      lines.push("contagens: " + JSON.stringify(body.counts));
    }
    const issues = body.issues || [];
    const errs = issues.filter(function (i) { return i.severity === "error"; });
    const warns = issues.filter(function (i) { return i.severity === "warning"; });
    lines.push("erros: " + errs.length + " · avisos: " + warns.length);
    issues.slice(0, 40).forEach(function (issue) {
      const loc = [issue.sheet, issue.row, issue.column].filter(Boolean).join(" · ");
      lines.push("[" + issue.severity + "] " + (loc ? loc + " — " : "") + issue.message);
    });
    if (issues.length > 40) lines.push("…");
    container.textContent = lines.join("\n");
  }

  tplLib.addEventListener("click", function () {
    downloadTemplate("library_import_v1");
  });
  tplProj.addEventListener("click", function () {
    downloadTemplate("project_import_v1");
  });

  validateBtn.addEventListener("click", function () {
    if (validateOut) validateOut.hidden = true;
    setStatus("");
    if (!validateFile.files || !validateFile.files.length) {
      setStatus("Seleccione um ficheiro .xlsx para validar.", true);
      return;
    }
    const form = new FormData();
    form.append("file", validateFile.files[0]);
    fetch("/api/workbook/validate", { method: "POST", body: form })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (result) {
        if (!result.ok) throw new Error(apiErrorMessage(result.body, "Validação falhou."));
        if (validateOut) {
          validateOut.hidden = false;
          validateOut.textContent = JSON.stringify(result.body, null, 2);
        }
        setStatus(result.body.valid ? "Estrutura válida." : "Estrutura com erros — veja o relatório.");
      })
      .catch(function (err) {
        setStatus(err.message, true);
      });
  });

  migrateBtn.addEventListener("click", function () {
    if (migrateOut) migrateOut.hidden = true;
    setStatus("");
    lastRunId = null;
    if (!migrateFile.files || !migrateFile.files.length) {
      setStatus("Seleccione o workbook para a pré-importação.", true);
      return;
    }
    const form = new FormData();
    form.append("file", migrateFile.files[0]);
    form.append("dry_run", "true");
    fetch("/api/workbook/migrate", { method: "POST", body: form })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (result) {
        if (!result.ok) throw new Error(apiErrorMessage(result.body, "Pré-importação falhou."));
        lastRunId = result.body.run_id;
        renderIssues(migrateOut, result.body);
        if (result.body.status !== "ready") {
          setStatus("Pré-importação bloqueada — corrija erros antes de consolidar.", true);
          return;
        }
        setStatus("Pré-importação concluída. Revise contagens e avisos; depois consolide.");
      })
      .catch(function (err) {
        setStatus(err.message, true);
      });
  });

  function selectedTarget() {
    return targetExisting && targetExisting.checked ? "existing_project" : "new_project";
  }

  applyBtn.addEventListener("click", function () {
    if (applyOut) applyOut.hidden = true;
    if (openProjectBtn) openProjectBtn.hidden = true;
    setStatus("");
    if (!lastRunId) {
      setStatus("Execute primeiro a pré-importação (dry-run).", true);
      return;
    }
    const confirm = (applyConfirm && applyConfirm.value.trim()) || "";
    if (confirm !== CONFIRM_PHRASE) {
      setStatus('Digite exactamente «' + CONFIRM_PHRASE + '» para confirmar.', true);
      return;
    }
    const payload = {
      run_id: lastRunId,
      confirm: confirm,
      target: selectedTarget(),
    };
    if (payload.target === "existing_project") {
      const pActive = document.getElementById("pActive");
      const projectId = pActive && pActive.value;
      if (!projectId) {
        setStatus("Seleccione o projecto activo no ecrã Projectos antes de consolidar.", true);
        return;
      }
      payload.project_id = projectId;
    }
    fetch("/api/workbook/migrate/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res.json().then(function (body) {
          return { ok: res.ok, body: body };
        });
      })
      .then(function (result) {
        if (!result.ok) throw new Error(apiErrorMessage(result.body, "Consolidação falhou."));
        lastProjectId = result.body.project_id;
        if (applyOut) {
          applyOut.hidden = false;
          applyOut.textContent = JSON.stringify(result.body, null, 2);
        }
        setStatus("Importação aplicada com sucesso.");
        if (openProjectBtn) openProjectBtn.hidden = false;
        document.dispatchEvent(new CustomEvent("get:workspace-open"));
      })
      .catch(function (err) {
        setStatus(err.message, true);
      });
  });

  if (openProjectBtn) {
    openProjectBtn.addEventListener("click", function () {
      if (router && lastProjectId) {
        const pActive = document.getElementById("pActive");
        if (pActive) {
          pActive.value = lastProjectId;
          pActive.dispatchEvent(new Event("change"));
        }
        router.navigate("project");
      }
    });
  }
}