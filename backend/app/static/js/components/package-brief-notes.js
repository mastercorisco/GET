/** Modelo GET-PACKAGE para textarea bePkgBriefNotes / expPkgBriefNotes. */

let _templatePromise = null;

export function loadPackageBriefTemplate() {
  if (!_templatePromise) {
    _templatePromise = fetch("/api/packages/brief-contribution-template")
      .then(function (res) {
        return res.json().then(function (body) {
          if (!res.ok) {
            const detail = body && body.detail;
            throw new Error(typeof detail === "string" ? detail : "HTTP " + res.status);
          }
          return body;
        });
      })
      .catch(function (err) {
        _templatePromise = null;
        throw err;
      });
  }
  return _templatePromise;
}

/** Preenche se vazio; force=true substitui (ex. botão de ajuda). */
export function applyPackageBriefTemplate(textareaId, _phase, options) {
  const opts = options || {};
  const el = document.getElementById(textareaId);
  if (!el) return Promise.resolve(false);
  if ((el.value || "").trim() && !opts.force) return Promise.resolve(false);
  return loadPackageBriefTemplate()
    .then(function (data) {
      const tpl = (data && data.template) || "";
      if (!tpl) return false;
      if ((el.value || "").trim() && !opts.force) return false;
      el.value = tpl;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      return true;
    })
    .catch(function () {
      return false;
    });
}