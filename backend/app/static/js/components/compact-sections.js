/** Secções recolhíveis (<details class="compact-section">) e acções expandir/recolher. */

export function setCompactSectionsOpen(open, root) {
  const scope = root || document;
  scope.querySelectorAll("details.compact-section").forEach(function (det) {
    det.open = open;
  });
}

export function initCompactSections(root) {
  const scope = root || document;
  scope.querySelectorAll("[data-compact-expand]").forEach(function (btn) {
    if (btn.dataset.compactWired === "1") return;
    btn.dataset.compactWired = "1";
    btn.addEventListener("click", function () {
      const target = btn.dataset.compactTarget
        ? document.querySelector(btn.dataset.compactTarget)
        : scope;
      setCompactSectionsOpen(true, target || document);
    });
  });
  scope.querySelectorAll("[data-compact-collapse]").forEach(function (btn) {
    if (btn.dataset.compactWired === "1") return;
    btn.dataset.compactWired = "1";
    btn.addEventListener("click", function () {
      const target = btn.dataset.compactTarget
        ? document.querySelector(btn.dataset.compactTarget)
        : scope;
      setCompactSectionsOpen(false, target || document);
    });
  });
}