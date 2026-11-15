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

function listEditor(parent, label, fieldKey, items, onChange, isObject) {
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
      const inp = document.createElement("input");
      if (isObject) {
        inp.value = item.prompt || item.text || JSON.stringify(item);
        inp.placeholder = "…";
        inp.addEventListener("change", function () {
          if (label.indexOf("quest") >= 0 || fieldKey.indexOf("open_questions") >= 0) {
            items[index] = { prompt: inp.value, answer: item.answer || "" };
          } else {
            items[index] = { text: inp.value };
          }
          onChange();
        });
      } else {
        inp.value = item;
        inp.addEventListener("change", function () {
          items[index] = inp.value;
          onChange();
        });
      }
      row.appendChild(inp);
      const del = el("button", "secondary", "−");
      del.type = "button";
      del.addEventListener("click", function () {
        items.splice(index, 1);
        render();
        onChange();
      });
      row.appendChild(del);
      list.appendChild(row);
    });
    const add = el("button", "secondary", "+");
    add.type = "button";
    add.addEventListener("click", function () {
      items.push(isObject ? { prompt: "", answer: "" } : "");
      render();
      onChange();
    });
    list.appendChild(add);
  }
  render();
  parent.appendChild(wrap);
}

export function createDevelopmentPointCard(point, hooks) {
  const card = el("article", "dp-card");
  card.draggable = true;
  card.dataset.pointId = point.id;

  const head = el("header", "dp-card-head");
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

  toggle.addEventListener("click", function () {
    const open = body.hidden;
    body.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open && !body.dataset.loaded) {
      hooks.loadDetail(point.id).then(function (detail) {
        body.dataset.loaded = "1";
        renderExpanded(body, detail, hooks);
      });
    }
  });

  card.addEventListener("dragstart", function (ev) {
    ev.dataTransfer.setData("text/plain", point.id);
    card.classList.add("is-dragging");
  });
  card.addEventListener("dragend", function () {
    card.classList.remove("is-dragging");
  });

  return card;
}

function renderExpanded(body, detail, hooks) {
  body.replaceChildren();
  const lists = detail.lists || {};

  function flush() {
    const patch = {
      title: body.querySelector("#dp-" + detail.id + "-title")?.value,
      core_idea: body.querySelector("#dp-" + detail.id + "-core_idea")?.value,
      intended_outcome: body.querySelector("#dp-" + detail.id + "-intended_outcome")?.value,
      llm_freedom: body.querySelector("#dp-" + detail.id + "-llm_freedom")?.value,
      status: body.querySelector("#dp-" + detail.id + "-status")?.value,
      lists: lists,
    };
    hooks.savePoint(detail.id, patch);
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
    listEditor(inner, "Orientações", "development_point.development_guidance", lists.development_guidance, flush, false);
  });

  makeSection("Premissas", "development_point.premises", function (inner) {
    const note = el("p", "field-microhelp", "Premissas do bloco e do projecto aplicam-se na exportação. Registe premissas específicas do ponto quando necessário.");
    inner.appendChild(note);
  });

  makeSection("Obrigatórios", "development_point.must_include", function (inner) {
    if (!lists.must_include) lists.must_include = [];
    listEditor(inner, "Elementos obrigatórios", "development_point.must_include", lists.must_include, flush, true);
  });

  makeSection("Limites", "development_point.limits_and_exclusions", function (inner) {
    if (!lists.limits_and_exclusions) lists.limits_and_exclusions = [];
    listEditor(
      inner,
      "Limites e exclusões",
      "development_point.limits_and_exclusions",
      lists.limits_and_exclusions,
      flush,
      true
    );
  });

  makeSection("Conhecimento e referências", "development_point.questions_to_answer", function (inner) {
    if (!lists.knowledge_item_ids) lists.knowledge_item_ids = [];
    if (!lists.reference_ids) lists.reference_ids = [];
    listEditor(inner, "IDs unidades de conhecimento", "development_point.questions_to_answer", lists.knowledge_item_ids, flush, false);
    listEditor(inner, "IDs referências", "development_point.questions_to_answer", lists.reference_ids, flush, false);
  });

  makeSection("Questões", "development_point.open_questions", function (inner) {
    if (!lists.open_questions) lists.open_questions = [];
    if (!lists.questions_to_answer) lists.questions_to_answer = [];
    listEditor(inner, "Questões pendentes", "development_point.open_questions", lists.open_questions, flush, true);
    listEditor(
      inner,
      "Perguntas a responder",
      "development_point.questions_to_answer",
      lists.questions_to_answer,
      flush,
      true
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
      false
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
    stSel.addEventListener("change", flush);
    stBlock.appendChild(stSel);
    attachFieldHelp(stBlock, "development_point.status", { inputEl: stSel });
    inner.appendChild(stBlock);
  });

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