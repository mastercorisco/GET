import { initRouter } from "./router.js";
import { createShell } from "./shell.js";
import { initLegacyApp } from "./app/legacy-logic.js";
import { mountDocumentTree, mountTechnicalTree } from "./components/tree.js";
import { wireTips } from "./components/tip.js";
import { applyFriendlySelectLabels } from "./labels.js";
import { initBackupsView } from "./views/backups.js";

const router = initRouter({
  onRouteChange: function (routeId) {
    if (routeId === "backups") {
      document.dispatchEvent(new CustomEvent("get:workspace-open"));
    }
  },
});
const shell = createShell(router);

initLegacyApp({
  mountDocumentTree: mountDocumentTree,
  mountTechnicalTree: mountTechnicalTree,
  onWorkspaceChange: function (data) {
    shell.onWorkspaceChange(data);
    document.dispatchEvent(new CustomEvent("get:workspace-open", { detail: data }));
    if (data) {
      wireProjectWatcher();
    }
  },
});

applyFriendlySelectLabels();
wireTips();

const pActive = document.getElementById("pActive");
if (pActive) {
  pActive.addEventListener("change", function () {
    const opt = pActive.options[pActive.selectedIndex];
    shell.setActiveProjectName(opt ? opt.textContent : "");
  });
}

const expBaselineMeta = document.getElementById("expBaselineMeta");
if (expBaselineMeta) {
  const observer = new MutationObserver(function () {
    const text = expBaselineMeta.textContent || "";
    const ok = /publicad|baseline/i.test(text) && !/desconhecida/i.test(text);
    shell.setBaselineState(ok ? "Baseline: publicada" : "Baseline: pendente", ok);
  });
  observer.observe(expBaselineMeta, { childList: true, characterData: true, subtree: true });
}

initBackupsView();

function wireProjectWatcher() {
  applyFriendlySelectLabels();
}