import { initRouter } from "./router.js";
import { createShell } from "./shell.js";
import { initLegacyApp } from "./app/legacy-logic.js";
import { mountDocumentTree, mountTechnicalTree } from "./components/tree.js";
import { initCompactSections } from "./components/compact-sections.js";
import {
  initHelpSystem,
  rewireHelpAfterLevelChange,
  wireDeclarativeHelp,
} from "./components/help-ui.js";
import { renderScreenGuide } from "./components/screen-guide.js";
import { applyFriendlySelectLabels } from "./labels.js";
import { hydrateAppearanceFromStorage, initAppearance } from "./components/appearance.js";
import { initBackupsView } from "./views/backups.js";
import { initWorkbookImport } from "./views/workbook-import.js";
import { initBlockEditor, openBlockEditor } from "./views/block-editor.js";
import { initSettingsView, setSettingsWorkspaceOpen } from "./views/settings.js";
import { initRouteTabs } from "./components/route-tabs.js";

hydrateAppearanceFromStorage();

const router = initRouter({
  onRouteChange: function (routeId) {
    renderScreenGuide(routeId);
    wireDeclarativeHelp(document);
    initRouteTabs(document.querySelector(".route-panel.is-active"));
    if (routeId === "backups") {
      document.dispatchEvent(new CustomEvent("get:workspace-open"));
    }
  },
});
const shell = createShell(router);

let _blockPrepHintShown = false;

initLegacyApp({
  mountDocumentTree: mountDocumentTree,
  mountTechnicalTree: mountTechnicalTree,
  onBlockSelect: function (blockId) {
    openBlockEditor(blockId, router);
    if (!_blockPrepHintShown) {
      _blockPrepHintShown = true;
      const st = document.getElementById("beStatus");
      if (st) {
        st.textContent =
          "Dica: use Preparação do bloco para definir pontos antes de exportar o pacote exchange.";
      }
    }
  },
  onWorkspaceChange: function (data) {
    shell.onWorkspaceChange(data);
    setSettingsWorkspaceOpen(!!data);
    document.dispatchEvent(new CustomEvent("get:workspace-open", { detail: data }));
    if (data) {
      wireProjectWatcher();
    }
  },
});

initAppearance();
initSettingsView(router);
setSettingsWorkspaceOpen(false);

applyFriendlySelectLabels();
initHelpSystem().then(function () {
  const hash =
    window.location.hash && window.location.hash.length > 1
      ? window.location.hash.slice(1)
      : "workspace";
  renderScreenGuide(hash);
  initRouteTabs(document.querySelector(".route-panel.is-active"));
});

document.addEventListener("get:help-level-changed", function () {
  rewireHelpAfterLevelChange(document);
});

initCompactSections(document);

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
initWorkbookImport(router);
initBlockEditor(router);

function wireProjectWatcher() {
  applyFriendlySelectLabels();
}