/** Abas internas por rota (library, project, etc.). */
export function initRouteTabs(root) {
  const scope = root || document;
  scope.querySelectorAll(".route-tab-bar").forEach(function (bar) {
    if (bar.dataset.routeTabsWired === "1") return;
    const panelRoot = bar.closest(".route-panel") || bar.parentElement;
    if (!panelRoot) return;
    const tabs = Array.from(bar.querySelectorAll(".route-tab"));
    const panels = tabs.map(function (tab) {
      const id = tab.dataset.routeTab;
      return panelRoot.querySelector('.route-tab-panel[data-route-tab="' + id + '"]');
    });

    function activate(index) {
      tabs.forEach(function (tab, i) {
        const on = i === index;
        tab.classList.toggle("is-active", on);
        tab.setAttribute("aria-selected", on ? "true" : "false");
        tab.tabIndex = on ? 0 : -1;
        if (panels[i]) panels[i].hidden = !on;
      });
      if (tabs[index]) tabs[index].focus({ preventScroll: true });
    }

    bar.setAttribute("role", "tablist");
    tabs.forEach(function (tab, i) {
      tab.setAttribute("role", "tab");
      tab.id = tab.id || "route-tab-" + (tab.dataset.routeTab || i);
      const panel = panels[i];
      if (panel) {
        panel.setAttribute("role", "tabpanel");
        panel.setAttribute("aria-labelledby", tab.id);
      }
      tab.addEventListener("click", function () {
        activate(i);
      });
      tab.addEventListener("keydown", function (ev) {
        if (ev.key === "ArrowRight") {
          ev.preventDefault();
          activate((i + 1) % tabs.length);
        } else if (ev.key === "ArrowLeft") {
          ev.preventDefault();
          activate((i - 1 + tabs.length) % tabs.length);
        }
      });
    });

    let initial = tabs.findIndex(function (t) {
      return t.classList.contains("is-active");
    });
    if (initial < 0) initial = 0;
    activate(initial);
    bar.dataset.routeTabsWired = "1";
  });
}