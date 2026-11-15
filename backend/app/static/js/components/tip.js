/** Botão (i) + popover de ajuda contextual. */

export const TIPS = {
  rootPath:
    "Pasta no disco onde ficam get.db, backups, exportações e importações — separada do código da aplicação.",
  userName: "Nome registado na proveniência das revisões (utilizador local único no MVP).",
  kDraft:
    "O rascunho é editável. Só ao «Concluir revisão» é criada uma revisão imutável na base de dados.",
  baseline:
    "Congela códigos documentais e revisões activas. Publique a baseline antes de exportar o pacote mestre.",
  expProfile:
    "Discussão inclui mais contexto para iteração com LLM; Redação limita o que sai no texto final.",
  impOmission:
    "Campos omitidos no JSON devolvido NÃO significam eliminação — só propostas explícitas removem conteúdo.",
  expZip:
    "Gera um ZIP com JSON, Markdown derivado e validation.json para arquivo ou partilha manual.",
  docTree:
    "Seleccione um nó na árvore para associar unidades de conhecimento ou exportar o fascículo.",
  exportCode:
    "Código legível usado nas exportações JSON (ex. function_id); o UUID interno mantém-se na base de dados.",
  wbValidate:
    "Valida cabeçalhos e linhas do modelo Excel v1. Não escreve na base de dados.",
};

export function createTipButton(tipId) {
  const text = TIPS[tipId];
  if (!text) return null;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tip-btn";
  btn.setAttribute("aria-label", "Ajuda");
  btn.textContent = "i";
  btn.addEventListener("click", function (ev) {
    ev.preventDefault();
    ev.stopPropagation();
    closeAllTips();
    const pop = document.createElement("div");
    pop.className = "tip-popover";
    pop.setAttribute("role", "tooltip");
    pop.textContent = text;
    const rect = btn.getBoundingClientRect();
    pop.style.position = "fixed";
    pop.style.top = rect.bottom + 6 + "px";
    pop.style.left = Math.min(rect.left, window.innerWidth - 340) + "px";
    document.body.appendChild(pop);
    pop.dataset.tipPopover = "1";
    const close = function () {
      pop.remove();
      document.removeEventListener("click", onDoc, true);
    };
    const onDoc = function (e) {
      if (!pop.contains(e.target) && e.target !== btn) close();
    };
    setTimeout(function () {
      document.addEventListener("click", onDoc, true);
    }, 0);
  });
  return btn;
}

function closeAllTips() {
  document.querySelectorAll("[data-tip-popover]").forEach(function (el) {
    el.remove();
  });
}

export function wireTips() {
  const map = [
    ["label[for='rootPath']", "rootPath"],
    ["label[for='userName']", "userName"],
    ["#view-export .card h2", "baseline"],
    ["label[for='expProfile']", "expProfile"],
    ["#view-import .lead", "impOmission"],
    ["label[for='iKind']", "exportCode"],
    ["#view-workbook .lead", "wbValidate"],
  ];
  map.forEach(function (row) {
    const anchor = document.querySelector(row[0]);
    const tip = createTipButton(row[1]);
    if (anchor && tip) anchor.appendChild(tip);
  });
}