/** Rótulos amigáveis para enums expostos na UI (valor API inalterado). */

export const NODE_TYPE_LABELS = {
  fascicle: "Fascículo",
  block: "Bloco",
  section: "Secção",
  subsection: "Subsecção",
};

export const TECH_KIND_LABELS = {
  system: "Sistema",
  equipment: "Equipamento",
  function: "Função",
};

export const EXPORT_PROFILE_LABELS = {
  discussion: "Discussão (evolução com LLM)",
  redaction: "Redação (texto aprovado)",
};

export const ASSOC_ROLE_LABELS = {
  mandatory_content: "Conteúdo obrigatório",
  supporting_context: "Contexto de apoio",
  constraint: "Condicionante",
  example: "Exemplo",
  cross_reference: "Referência cruzada",
  verification_basis: "Base de verificação",
  open_issue: "Questão em aberto",
  excluded_content: "Conteúdo excluído",
};

export const PROFILE_TYPE_LABELS = {
  control_function: "Função de controlo",
  interface: "Interface",
  requirement: "Requisito",
  decision: "Decisão",
  open_question: "Questão em aberto",
};

export const CONTRACTUAL_ROLE_LABELS = {
  informative_reference: "Referência informativa",
  design_basis: "Base de concepção",
  contractual_requirement: "Requisito contratual",
  compliance_target: "Objectivo de conformidade",
  guidance_only: "Apenas orientação",
};

export function labelFromMap(map, value) {
  return map[value] || value;
}

export function applyFriendlySelectLabels() {
  document.querySelectorAll("select").forEach(function (sel) {
    const id = sel.id || "";
    let map = null;
    if (id === "docType") map = NODE_TYPE_LABELS;
    if (id === "iKind") map = TECH_KIND_LABELS;
    if (id === "expProfile") map = EXPORT_PROFILE_LABELS;
    if (id === "docAssocRole") map = ASSOC_ROLE_LABELS;
    if (id === "kProfileType" || id === "pkProfileType") map = PROFILE_TYPE_LABELS;
    if (id === "projRefRole") map = CONTRACTUAL_ROLE_LABELS;
    if (!map) return;
    Array.from(sel.options).forEach(function (opt) {
      opt.textContent = labelFromMap(map, opt.value) + " (" + opt.value + ")";
    });
  });
}