import { attachFieldHelp, openHelpModal } from "./field-help.js";
import { createHelpIcon } from "./help-icon.js";

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}

function sectionSummary(title, fieldKey) {
  const summary = el("summary", "dp-section-summary", title);
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tip-btn field-help-btn";
  btn.setAttribute("aria-label", "Ajuda: " + title);
  btn.replaceChildren(createHelpIcon("help-icon--field"));
  btn.addEventListener("click", function (ev) {
    ev.preventDefault();
    ev.stopPropagation();
    openHelpModal(fieldKey);
  });
  summary.appendChild(btn);
  return summary;
}

/** @typedef {"string" | "text" | "prompt_answer"} ListItemKind */

function defaultListItem(kind) {
  if (kind === "text") return { text: "" };
  if (kind === "prompt_answer") return { prompt: "", answer: "" };
  return "";
}

function textItemDisplay(item) {
  if (typeof item === "string") return item;
  if (item && typeof item.text === "string") return item.text;
  if (item && typeof item.prompt === "string" && item.text == null) return item.prompt;
  return "";
}

function promptAnswerFromItem(item) {
  if (!item || typeof item !== "object") return { prompt: "", answer: "" };
  return {
    prompt: typeof item.prompt === "string" ? item.prompt : textItemDisplay(item),
    answer: typeof item.answer === "string" ? item.answer : "",
  };
}

function listEditor(parent, label, fieldKey, items, onChange, itemKind) {
  const wrap = el("div", "dp-list-editor");
  const lbl = el("label", "field-label", label);
  wrap.appendChild(lbl);
  attachFieldHelp(wrap, fieldKey, {});
  const list = el("div", "dp-list-items");
  wrap.appendChild(list);

  function render() {
    list.replaceChildren();
    items.forEach(function (item, index) {
      const row = el("div", "dp-list-row");
      const del = el("button", "secondary dp-list-del", "−");
      del.type = "button";
      del.setAttribute("aria-label", "Remover linha");
      del.title = "Remover";
      del.addEventListener("click", function () {
        items.splice(index, 1);
        render();
        onChange();
      });
      row.appendChild(del);
      if (itemKind === "prompt_answer") {
        const pa = promptAnswerFromItem(item);
        const promptInp = document.createElement("input");
        promptInp.value = pa.prompt;
        promptInp.placeholder = "Pergunta ou tema";
        const answerInp = document.createElement("input");
        answerInp.value = pa.answer;
        answerInp.placeholder = "Resposta esperada (opcional)";
        function syncPromptAnswer() {
          items[index] = { prompt: promptInp.value, answer: answerInp.value };
          onChange();
        }
        promptInp.addEventListener("change", syncPromptAnswer);
        answerInp.addEventListener("change", syncPromptAnswer);
        row.appendChild(promptInp);
        row.appendChild(answerInp);
      } else if (itemKind === "text") {
        const inp = document.createElement("input");
        inp.value = textItemDisplay(item);
        inp.placeholder = "Texto";
        inp.addEventListener("change", function () {
          items[index] = { text: inp.value };
          onChange();
        });
        row.appendChild(inp);
      } else {
        const inp = document.createElement("input");
        inp.value = typeof item === "string" ? item : String(item || "");
        inp.addEventListener("change", function () {
          items[index] = inp.value;
          onChange();
        });
        row.appendChild(inp);
      }
      list.appendChild(row);
    });
    const add = el("button", "secondary", "+");
    add.type = "button";
    add.addEventListener("click", function () {
      items.push(defaultListItem(itemKind));
      render();
      onChange();
    });
    list.appendChild(add);
  }
  render();
  parent.appendChild(wrap);
}

function refIdListEditor(parent, label, fieldKey, selectedIds, loadOptions, onChange) {
  const wrap = el("div", "dp-list-editor");
  wrap.appendChild(el("label", "field-label", label));
  attachFieldHelp(wrap, fieldKey, {});
  const list = el("div", "dp-list-items");
  wrap.appendChild(list);
  const loading = el("p", "field-microhelp", "A carregar opções…");
  list.appendChild(loading);
  let options = [];

  function optionLabel(opt) {
    return opt && opt.label ? opt.label : opt.id;
  }

  function render() {
    list.replaceChildren();
    selectedIds.forEach(function (id, index) {
      const row = el("div", "dp-list-row");
      const del = el("button", "secondary dp-list-del", "−");
      del.type = "button";
      del.setAttribute("aria-label", "Remover");
      del.addEventListener("click", function () {
        selectedIds.splice(index, 1);
        render();
        onChange();
      });
      row.appendChild(del);
      const sel = document.createElement("select");
      sel.className = "dp-ref-select";
      const blank = document.createElement("option");
      blank.value = "";
      blank.textContent = "— seleccionar —";
      sel.appendChild(blank);
      options.forEach(function (opt) {
        const o = document.createElement("option");
        o.value = opt.id;
        o.textContent = optionLabel(opt);
        if (opt.id === id) o.selected = true;
        sel.appendChild(o);
      });
      if (id && !options.some(function (o) {
        return o.id === id;
      })) {
        const orphan = document.createElement("option");
        orphan.value = id;
        orphan.textContent = id.slice(0, 8) + "… (fora da lista)";
        orphan.selected = true;
        sel.appendChild(orphan);
      }
      sel.addEventListener("change", function () {
        if (!sel.value) {
          selectedIds.splice(index, 1);
        } else {
          selectedIds[index] = sel.value;
        }
        render();
        onChange();
      });
      row.appendChild(sel);
      list.appendChild(row);
    });
    const add = el("button", "secondary", "+");
    add.type = "button";
    add.addEventListener("click", function () {
      const unused = options.find(function (opt) {
        return selectedIds.indexOf(opt.id) < 0;
      });
      selectedIds.push(unused ? unused.id : "");
      render();
      if (unused) onChange();
    });
    list.appendChild(add);
    if (!options.length) {
      list.appendChild(
        el("p", "field-microhelp", "Nenhuma opção — crie unidades na Biblioteca ou no projecto.")
      );
    }
  }

  const loader = typeof loadOptions === "function" ? loadOptions() : Promise.resolve([]);
  Promise.resolve(loader)
    .then(function (opts) {
      options = opts || [];
      render();
    })
    .catch(function () {
      options = [];
      render();
    });

  parent.appendChild(wrap);
}

const PREMISE_IMPORTANCE = ["mandatory", "recommended", "informative"];
const PREMISE_SOURCE = [
  "project_decision",
  "functional_requirement",
  "standard",
  "existing_document",
  "operational_experience",
  "technical_recommendation",
  "unconfirmed_information",
];
const PREMISE_CONFIDENCE = ["confirmed", "provisional", "unverified"];

function fillSelect(sel, values) {
  values.forEach(function (v) {
    const o = document.createElement("option");
    o.value = v;
    o.textContent = v;
    sel.appendChild(o);
  });
}

function renderPointPremises(inner, pointId, hooks) {
  const note = el(
    "p",
    "field-microhelp",
    "Premissas do projecto, fascículo e bloco aplicam-se na exportação. Aqui regista condições específicas deste ponto."
  );
  inner.appendChild(note);
  const list = el("div", "be-premise-list dp-premise-list");
  inner.appendChild(list);

  const stmtBlock = el("div", "field-block");
  const stmtLbl = el("label", "field-label", "Nova premissa");
  stmtLbl.setAttribute("for", "dp-" + pointId + "-premise-statement");
  const stmt = document.createElement("textarea");
  stmt.id = "dp-" + pointId + "-premise-statement";
  stmt.rows = 2;
  stmtBlock.appendChild(stmtLbl);
  stmtBlock.appendChild(stmt);
  attachFieldHelp(stmtBlock, "premise.statement", { inputEl: stmt });
  inner.appendChild(stmtBlock);

  const attrs = el("div", "be-premise-attrs");
  const impRow = el("div", "be-field-row");
  impRow.appendChild(el("label", "", "Importância"));
  const impSel = document.createElement("select");
  impSel.id = "dp-" + pointId + "-premise-importance";
  fillSelect(impSel, PREMISE_IMPORTANCE);
  impRow.appendChild(impSel);
  attrs.appendChild(impRow);
  const srcRow = el("div", "be-field-row");
  srcRow.appendChild(el("label", "", "Origem"));
  const srcSel = document.createElement("select");
  srcSel.id = "dp-" + pointId + "-premise-source";
  fillSelect(srcSel, PREMISE_SOURCE);
  srcRow.appendChild(srcSel);
  attrs.appendChild(srcRow);
  const confRow = el("div", "be-field-row");
  confRow.appendChild(el("label", "", "Confiança"));
  const confSel = document.createElement("select");
  confSel.id = "dp-" + pointId + "-premise-confidence";
  fillSelect(confSel, PREMISE_CONFIDENCE);
  confRow.appendChild(confSel);
  attrs.appendChild(confRow);
  inner.appendChild(attrs);

  function refreshList() {
    if (!hooks.listPremises) {
      list.replaceChildren(el("p", "field-microhelp", "Carregar premissas indisponível."));
      return;
    }
    hooks.listPremises(pointId).then(function (rows) {
      list.replaceChildren();
      (rows || []).forEach(function (prem) {
        const row = el("div", "be-premise-row list-item-row");
        const text = el("span", "", "[" + prem.importance + "] " + prem.statement + " (" + prem.confidence + ")");
        row.appendChild(text);
        const delBtn = el("button", "secondary danger", "Apagar");
        delBtn.type = "button";
        delBtn.addEventListener("click", function () {
          if (!window.confirm("Apagar esta premissa?")) return;
          hooks.deletePremise(prem.id).then(refreshList);
        });
        row.appendChild(delBtn);
        list.appendChild(row);
      });
    });
  }

  const addBtn = el("button", "secondary", "Adicionar premissa");
  addBtn.type = "button";
  addBtn.addEventListener("click", function () {
    const statement = stmt.value.trim();
    if (!statement || !hooks.createPremise) return;
    hooks
      .createPremise(pointId, {
        statement: statement,
        importance: impSel.value,
        source_type: srcSel.value,
        confidence: confSel.value,
      })
      .then(function () {
        stmt.value = "";
        refreshList();
      });
  });
  inner.appendChild(addBtn);
  refreshList();
}

export function createDevelopmentPointCard(point, hooks) {
  const card = el("article", "dp-card");
  card.dataset.pointId = point.id;

  const head = el("header", "dp-card-head");
  const dragHandle = el("span", "dp-card-drag-handle", "⠿");
  dragHandle.draggable = true;
  dragHandle.tabIndex = 0;
  dragHandle.setAttribute("role", "button");
  dragHandle.setAttribute("aria-label", "Arrastar para reordenar");
  dragHandle.title = "Arrastar para reordenar";
  const titleBit =
    point.title && String(point.title).trim()
      ? String(point.title).trim()
      : "(sem título)";
  const toggle = el("button", "dp-card-toggle", "#" + point.order + " · " + titleBit);
  toggle.type = "button";
  toggle.setAttribute("aria-expanded", "false");
  const overviewBtn = document.createElement("button");
  overviewBtn.type = "button";
  overviewBtn.className = "tip-btn field-help-btn";
  overviewBtn.setAttribute("aria-label", "Ajuda do ponto");
  overviewBtn.replaceChildren(createHelpIcon("help-icon--field"));
  overviewBtn.addEventListener("click", function (ev) {
    ev.preventDefault();
    ev.stopPropagation();
    openHelpModal("development_point.overview");
  });
  const meta = el(
    "span",
    "dp-card-meta",
    point.status + (point.needs_review ? " · rev" : "")
  );
  head.appendChild(dragHandle);
  head.appendChild(toggle);
  head.appendChild(meta);
  head.appendChild(overviewBtn);
  if (point.completeness_alerts && point.completeness_alerts.length) {
    const alert = el("span", "error", point.completeness_alerts.join(" · "));
    head.appendChild(alert);
  }
  card.appendChild(head);

  const body = el("div", "dp-card-body");
  body.hidden = true;
  card.appendChild(body);

  const ui = { card: card, meta: meta, toggle: toggle, head: head };

  toggle.addEventListener("click", function () {
    const open = body.hidden;
    body.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    card.classList.toggle("is-expanded", open);
    if (open && !body.dataset.loaded) {
      hooks.loadDetail(point.id).then(function (detail) {
        body.dataset.loaded = "1";
        renderExpanded(body, detail, hooks, ui);
        requestAnimationFrame(function () {
          body.scrollTop = 0;
          const canScroll = body.scrollHeight > body.clientHeight + 2;
          if (canScroll) body.focus({ preventScroll: true });
        });
      });
    } else if (open) {
      requestAnimationFrame(function () {
        body.scrollTop = 0;
      });
    }
  });

  dragHandle.addEventListener("dragstart", function (ev) {
    ev.dataTransfer.setData("text/plain", point.id);
    ev.dataTransfer.effectAllowed = "move";
    card.classList.add("is-dragging");
    if (typeof ev.dataTransfer.setDragImage === "function") {
      ev.dataTransfer.setDragImage(card, 24, 16);
    }
  });
  dragHandle.addEventListener("dragend", function () {
    card.classList.remove("is-dragging");
  });

  return card;
}

function renderExpanded(body, detail, hooks, ui) {
  body.replaceChildren();
  const lists = detail.lists || {};

  function syncFromSaved(saved) {
    if (!saved || !ui) return;
    const status = saved.status || detail.status;
    ui.meta.textContent = status + (saved.needs_review ? " · rev" : "");
    const stSel = body.querySelector("#dp-" + detail.id + "-status");
    if (stSel && saved.status) stSel.value = saved.status;
    detail.status = status;
    const err = ui.head.querySelector(".dp-save-error");
    if (err) err.remove();
    if (typeof hooks.onPointSaved === "function") {
      hooks.onPointSaved(saved);
    }
  }

  function flush() {
    const patch = {
      title: body.querySelector("#dp-" + detail.id + "-title")?.value,
      core_idea: body.querySelector("#dp-" + detail.id + "-core_idea")?.value,
      intended_outcome: body.querySelector("#dp-" + detail.id + "-intended_outcome")?.value,
      llm_freedom: body.querySelector("#dp-" + detail.id + "-llm_freedom")?.value,
      status: body.querySelector("#dp-" + detail.id + "-status")?.value,
      lists: lists,
    };
    return hooks
      .savePoint(detail.id, patch)
      .then(syncFromSaved)
      .catch(function (err) {
        let errSpan = ui.head.querySelector(".dp-save-error");
        if (!errSpan) {
          errSpan = el("span", "error dp-save-error", err.message || "Falha ao guardar.");
          ui.head.appendChild(errSpan);
        } else {
          errSpan.textContent = err.message || "Falha ao guardar.";
        }
      });
  }

  function fieldBlock(parent, fieldKey, labelText, value, multiline) {
    const block = el("div", "field-block");
    const lbl = el("label", "field-label", labelText);
    block.appendChild(lbl);
    let input;
    if (multiline) {
      input = document.createElement("textarea");
      input.rows = 3;
    } else {
      input = document.createElement("input");
    }
    input.value = value || "";
    input.id = "dp-" + detail.id + "-" + fieldKey;
    block.appendChild(input);
    attachFieldHelp(block, "development_point." + fieldKey, {
      inputEl: input,
      onUseExample: function (text) {
        input.value = text;
        flush();
      },
    });
    input.addEventListener("change", flush);
    parent.appendChild(block);
  }

  function makeSection(title, fieldKey, builder, openDefault) {
    const det = el("details", "dp-section");
    if (openDefault) det.open = true;
    det.appendChild(sectionSummary(title, fieldKey));
    const inner = el("div", "dp-section-body");
    builder(inner);
    det.appendChild(inner);
    body.appendChild(det);
  }

  makeSection(
    "Ideia",
    "development_point.core_idea",
    function (inner) {
      fieldBlock(inner, "title", "Título", detail.title, false);
      fieldBlock(inner, "core_idea", "Ideia central", detail.core_idea, true);
      fieldBlock(inner, "intended_outcome", "Resultado pretendido", detail.intended_outcome, true);
    },
    true
  );

  makeSection("Orientações", "development_point.development_guidance", function (inner) {
    if (!lists.development_guidance) lists.development_guidance = [];
    listEditor(inner, "Orientações", "development_point.development_guidance", lists.development_guidance, flush, "string");
  });

  makeSection("Premissas", "development_point.premises", function (inner) {
    renderPointPremises(inner, detail.id, hooks);
  });

  makeSection("Obrigatórios", "development_point.must_include", function (inner) {
    if (!lists.must_include) lists.must_include = [];
    listEditor(inner, "Elementos obrigatórios", "development_point.must_include", lists.must_include, flush, "text");
  });

  makeSection("Limites", "development_point.limits_and_exclusions", function (inner) {
    if (!lists.limits_and_exclusions) lists.limits_and_exclusions = [];
    listEditor(
      inner,
      "Limites e exclusões",
      "development_point.limits_and_exclusions",
      lists.limits_and_exclusions,
      flush,
      "text"
    );
  });

  makeSection("Conhecimento e referências", "development_point.questions_to_answer", function (inner) {
    if (!lists.knowledge_item_ids) lists.knowledge_item_ids = [];
    if (!lists.reference_ids) lists.reference_ids = [];
    inner.appendChild(
      el(
        "p",
        "field-microhelp",
        "Associe unidades de conhecimento e referências já existentes (biblioteca ou projecto)."
      )
    );
    const loadKi = hooks.loadKnowledgePickList
      ? hooks.loadKnowledgePickList.bind(hooks)
      : function () {
          return Promise.resolve([]);
        };
    const loadRef = hooks.loadReferencePickList
      ? hooks.loadReferencePickList.bind(hooks)
      : function () {
          return Promise.resolve([]);
        };
    refIdListEditor(
      inner,
      "Unidades de conhecimento",
      "knowledge_item",
      lists.knowledge_item_ids,
      loadKi,
      flush
    );
    refIdListEditor(inner, "Referências", "reference", lists.reference_ids, loadRef, flush);
  });

  makeSection("Questões", "development_point.open_questions", function (inner) {
    if (!lists.open_questions) lists.open_questions = [];
    if (!lists.questions_to_answer) lists.questions_to_answer = [];
    listEditor(inner, "Questões pendentes", "development_point.open_questions", lists.open_questions, flush, "prompt_answer");
    listEditor(
      inner,
      "Perguntas a responder",
      "development_point.questions_to_answer",
      lists.questions_to_answer,
      flush,
      "prompt_answer"
    );
  });

  makeSection("Critérios", "development_point.acceptance_criteria", function (inner) {
    if (!lists.acceptance_criteria) lists.acceptance_criteria = [];
    listEditor(
      inner,
      "Critérios de aceitação",
      "development_point.acceptance_criteria",
      lists.acceptance_criteria,
      flush,
      "string"
    );
  });

  makeSection("Estado e LLM", "development_point.llm_freedom", function (inner) {
    const ffBlock = el("div", "field-block");
    const ffLbl = el("label", "field-label", "Liberdade da LLM");
    ffBlock.appendChild(ffLbl);
    const ffSel = document.createElement("select");
    ffSel.id = "dp-" + detail.id + "-llm_freedom";
    ["strict", "bounded", "exploratory"].forEach(function (v) {
      const o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      if (v === detail.llm_freedom) o.selected = true;
      ffSel.appendChild(o);
    });
    ffSel.addEventListener("change", flush);
    ffBlock.appendChild(ffSel);
    attachFieldHelp(ffBlock, "development_point.llm_freedom", { inputEl: ffSel });
    inner.appendChild(ffBlock);

    const stBlock = el("div", "field-block");
    const stLbl = el("label", "field-label", "Estado");
    stBlock.appendChild(stLbl);
    const stSel = document.createElement("select");
    stSel.id = "dp-" + detail.id + "-status";
    ["draft", "incomplete", "ready", "approved", "obsolete"].forEach(function (v) {
      const o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      if (v === detail.status) o.selected = true;
      stSel.appendChild(o);
    });
    stSel.addEventListener("change", function () {
      ui.meta.textContent = "A guardar…";
      flush();
    });
    stBlock.appendChild(stSel);
    attachFieldHelp(stBlock, "development_point.status", { inputEl: stSel });
    const autoHint = el(
      "p",
      "field-microhelp",
      "As alterações guardam ao sair de cada campo ou ao mudar o estado (não há botão OK)."
    );
    inner.appendChild(stBlock);
    inner.appendChild(autoHint);
  });

  syncFromSaved({ status: detail.status, needs_review: detail.needs_review });

  const actions = el("div", "dp-card-actions");
  [
    ["Duplicar", "duplicate"],
    ["Arquivar", "archive"],
    ["Eliminar", "delete"],
  ].forEach(function (pair) {
    const className = pair[1] === "delete" ? "secondary danger" : "secondary";
    const b = el("button", className, pair[0]);
    b.type = "button";
    b.addEventListener("click", function () {
      if (pair[1] === "delete" && !window.confirm("Eliminar este ponto de desenvolvimento?")) {
        return;
      }
      hooks.action(detail.id, pair[1]);
    });
    actions.appendChild(b);
  });
  body.appendChild(actions);

  (detail.validation_issues || []).forEach(function (issue) {
    const p = el("p", issue.severity === "error" ? "error" : "", issue.message);
    body.appendChild(p);
  });
}