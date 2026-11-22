export function createShell(router) {
  const els = {
    workspacePill: document.getElementById("status-workspace"),
    projectPill: document.getElementById("status-project"),
    baselinePill: document.getElementById("status-baseline"),
  };

  function onWorkspaceChange(data) {
    router.setWorkspaceOpen(!!data);
    if (!data) {
      if (els.workspacePill) els.workspacePill.textContent = "Workspace: fechado";
      if (els.projectPill) els.projectPill.textContent = "Projecto: —";
      if (els.baselinePill) {
        els.baselinePill.textContent = "Baseline: —";
        els.baselinePill.classList.remove("status-pill--ok");
      }
      return;
    }
    if (els.workspacePill) {
      els.workspacePill.textContent = "Workspace: " + shorten(data.root_path, 36);
      els.workspacePill.title = data.root_path;
    }
  }

  function setActiveProjectName(name) {
    if (!els.projectPill) return;
    const label = "Projecto: " + (name || "—");
    els.projectPill.textContent = label;
    els.projectPill.title = name ? label : "";
  }

  function setBaselineState(text, ok) {
    if (!els.baselinePill) return;
    els.baselinePill.textContent = text;
    els.baselinePill.classList.toggle("status-pill--ok", !!ok);
    els.baselinePill.classList.toggle("status-pill--warn", !ok);
  }

  return { onWorkspaceChange: onWorkspaceChange, setActiveProjectName: setActiveProjectName, setBaselineState: setBaselineState };
}

function shorten(text, max) {
  if (!text || text.length <= max) return text || "";
  return "…" + text.slice(-max + 1);
}