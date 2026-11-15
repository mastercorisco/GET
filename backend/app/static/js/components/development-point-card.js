import { attachFieldHelp } from "./field-help.js";

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}

function listEditor(parent, label, items, onChange, isObject) {
  const wrap = el("div", "dp-list-editor");
  const lbl = el("label", "field-label", label);
  wrap.appendChild(lbl);
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
          items[index] = isObject && label.indexOf("quest") >= 0
            ? { prompt: inp.value, answer: item.answer || "" }
            : { text: inp.value };
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
  const toggle = el("button", "dp-card-toggle", "#" + point.order + " — " + (point.title || "(sem título)"));
  toggle.type = "button";
  toggle.setAttribute("aria-expanded", "false");
  const meta = el(
    "span",
    "dp-card-meta",
    point.status + (point.needs_review ? " · revisão" : "") +
      " · P:" + (point.premise_count || 0) +
      " · Obr:" + (point.must_include_count || 0) +
      " · ?:" + (point.open_questions_count || 0) +
      " · CA:" + (point.acceptance_criteria_count || 0)
  );
  head.appendChild(toggle);
  head.appendChild(meta);
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

  function fieldBlock(fieldKey, labelText, value, multiline) {
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
    body.appendChild(block);
  }

  fieldBlock("title", "Título", detail.title, false);
  fieldBlock("core_idea", "Ideia central", detail.core_idea, true);
  fieldBlock("intended_outcome", "Resultado pretendido", detail.intended_outcome, true);

  const ffLbl = el("label", "field-label", "Liberdade da LLM");
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
  body.appendChild(ffLbl);
  body.appendChild(ffSel);

  const stLbl = el("label", "field-label", "Estado");
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
  body.appendChild(stLbl);
  body.appendChild(stSel);

  if (!lists.development_guidance) lists.development_guidance = [];
  listEditor(body, "Orientações", lists.development_guidance, flush, false);
  listEditor(body, "Elementos obrigatórios", lists.must_include, flush, true);
  listEditor(body, "Limites e exclusões", lists.limits_and_exclusions, flush, true);
  listEditor(body, "Questões pendentes", lists.open_questions, flush, true);
  listEditor(body, "Critérios de aceitação", lists.acceptance_criteria, flush, false);

  const actions = el("div", "dp-card-actions");
  [["Duplicar", "duplicate"], ["Arquivar", "archive"]].forEach(function (pair) {
    const b = el("button", "secondary", pair[0]);
    b.type = "button";
    b.addEventListener("click", function () {
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