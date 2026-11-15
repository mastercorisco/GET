/** @deprecated — use help-ui wireDeclarativeHelp + data-help-key no HTML. */
import { wireDeclarativeHelp } from "./help-ui.js";

export function wireTips() {
  wireDeclarativeHelp(document);
}

export function createTipButton() {
  return null;
}