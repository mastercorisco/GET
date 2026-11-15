/** Ícone partilhado de ajuda contextual (gavetas, botões, campo «i»). */

const HELP_ICON_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<circle cx="12" cy="12" r="9.25" fill="currentColor" fill-opacity="0.12"/>' +
  '<circle cx="12" cy="12" r="9.25"/>' +
  '<path d="M9.75 9.5a2.35 2.35 0 0 1 4.13 1.4c0 1.35-1.63 1.7-2.38 2.55-.35.4-.5.75-.5 1.05"/>' +
  '<circle cx="12" cy="16.75" r="0.85" fill="currentColor" stroke="none"/>' +
  "</svg>";

export function createHelpIcon(extraClass) {
  const span = document.createElement("span");
  span.className = "help-icon" + (extraClass ? " " + extraClass : "");
  span.innerHTML = HELP_ICON_SVG;
  return span;
}

export function setHelpTriggerLabel(button, label) {
  if (!button) return;
  button.classList.add("help-trigger");
  button.replaceChildren();
  button.appendChild(createHelpIcon());
  const text = document.createElement("span");
  text.className = "help-trigger__label";
  text.textContent = label;
  button.appendChild(text);
}

export function ensureHelpDrawerTitleIcon(titleEl) {
  if (!titleEl || titleEl.querySelector(".help-icon")) return;
  titleEl.classList.add("help-drawer__title");
  const textSpan =
    titleEl.querySelector(".help-drawer__title-text") ||
    (function () {
      const moved = document.createElement("span");
      moved.className = "help-drawer__title-text";
      moved.textContent = titleEl.textContent;
      titleEl.textContent = "";
      titleEl.appendChild(moved);
      return moved;
    })();
  titleEl.insertBefore(createHelpIcon("help-icon--header"), textSpan);
  return textSpan;
}