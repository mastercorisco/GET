import { labelFromMap, NODE_TYPE_LABELS, TECH_KIND_LABELS } from "../labels.js";

function childrenByParent(nodes) {
  const kids = new Map();
  nodes.forEach(function (n) {
    const pid = n.parent_id || "";
    if (!kids.has(pid)) kids.set(pid, []);
    kids.get(pid).push(n);
  });
  kids.forEach(function (list) {
    list.sort(function (a, b) {
      return a.sort_key - b.sort_key || a.display_code.localeCompare(b.display_code);
    });
  });
  return kids;
}

function nodeLineLabel(node) {
  const t = labelFromMap(NODE_TYPE_LABELS, node.node_type);
  return node.display_code + "  " + t + " — " + node.title;
}

function walkTree(children, parentId, ancestors, lines) {
  const list = children.get(parentId || "") || [];
  list.forEach(function (node, index) {
    const last = index === list.length - 1;
    let prefix = "";
    if (ancestors.length) {
      prefix = ancestors.map(function (hasSibling) {
        return hasSibling ? "│   " : "    ";
      }).join("");
      prefix += last ? "└── " : "├── ";
    }
    lines.push({ node: node, line: prefix + nodeLineLabel(node) });
    const nextAncestors = ancestors.concat([!last]);
    walkTree(children, node.id, nextAncestors, lines);
  });
}

const EXPAND_ALL_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 7v10"/><path d="m5 10 3 3 3-3"/><path d="M16 7v10"/><path d="m13 10 3 3 3-3"/></svg>';
const COLLAPSE_ALL_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 17V7"/><path d="m5 14 3-3 3 3"/><path d="M16 17V7"/><path d="m13 14 3-3 3 3"/></svg>';

let docTreeExpandedProjectId = null;
let docTreeExpandedFascicles = new Set();

function syncDocTreeProject(projectId) {
  if (projectId && projectId !== docTreeExpandedProjectId) {
    docTreeExpandedProjectId = projectId;
    docTreeExpandedFascicles = new Set();
  }
}

function iconToolButton(className, label, svg) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = className;
  btn.setAttribute("aria-label", label);
  btn.title = label;
  btn.innerHTML = svg;
  return btn;
}

export function mountDocumentTree(container, nodes, options) {
  const selectedId = options.selectedId;
  const onSelect = options.onSelect;
  const onMove = options.onMove;
  const onDelete = options.onDelete;
  const projectId = options.projectId || (nodes[0] && nodes[0].project_id) || null;

  syncDocTreeProject(projectId);

  container.replaceChildren();

  if (!nodes.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Nenhum nó documental.";
    container.appendChild(empty);
    return;
  }

  const kids = childrenByParent(nodes);
  const fascicleIds = nodes
    .filter(function (n) {
      return n.node_type === "fascicle";
    })
    .map(function (n) {
      return n.id;
    });

  const toolbar = document.createElement("div");
  toolbar.className = "doc-tree-toolbar";
  toolbar.appendChild(
    iconToolButton("icon-btn", "Expandir todos os fascículos", EXPAND_ALL_SVG)
  );
  toolbar.appendChild(
    iconToolButton("icon-btn", "Contrair todos os fascículos", COLLAPSE_ALL_SVG)
  );
  const expandAllBtn = toolbar.children[0];
  const collapseAllBtn = toolbar.children[1];
  expandAllBtn.addEventListener("click", function () {
    fascicleIds.forEach(function (id) {
      docTreeExpandedFascicles.add(id);
    });
    mountDocumentTree(container, nodes, options);
  });
  collapseAllBtn.addEventListener("click", function () {
    docTreeExpandedFascicles.clear();
    mountDocumentTree(container, nodes, options);
  });
  container.appendChild(toolbar);

  const pre = document.createElement("div");
  pre.className = "tree-ascii doc-tree-ascii";

  function appendNode(node, depth) {
    const childList = kids.get(node.id) || [];
    const isFascicle = node.node_type === "fascicle";
    const hasKids = childList.length > 0;
    const expanded = isFascicle && docTreeExpandedFascicles.has(node.id);

    const row = document.createElement("div");
    row.className = "doc-tree-row";
    row.style.paddingLeft = depth * 0.85 + "rem";

    if (isFascicle && hasKids) {
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "tree-expand";
      toggle.setAttribute("aria-label", expanded ? "Contrair blocos" : "Expandir blocos");
      toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
      toggle.textContent = expanded ? "−" : "+";
      toggle.addEventListener("click", function (ev) {
        ev.stopPropagation();
        if (expanded) {
          docTreeExpandedFascicles.delete(node.id);
        } else {
          docTreeExpandedFascicles.add(node.id);
        }
        mountDocumentTree(container, nodes, options);
      });
      row.appendChild(toggle);
    } else {
      const spacer = document.createElement("span");
      spacer.className = "tree-toggle-spacer";
      spacer.setAttribute("aria-hidden", "true");
      row.appendChild(spacer);
    }

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tree-line";
    if (node.id === selectedId) btn.classList.add("is-selected");
    if (node.depth_warning) btn.style.color = "#fca5a5";
    btn.textContent = nodeLineLabel(node);
    btn.addEventListener("click", function () {
      onSelect(node);
    });
    row.appendChild(btn);
    pre.appendChild(row);

    if (isFascicle && hasKids) {
      if (expanded) {
        childList.forEach(function (child) {
          appendSubtree(child, depth + 1);
        });
      }
      return;
    }
    childList.forEach(function (child) {
      appendSubtree(child, depth + 1);
    });
  }

  function appendSubtree(node, depth) {
    appendNode(node, depth);
  }

  const roots = kids.get("") || [];
  roots.forEach(function (root) {
    appendSubtree(root, 0);
  });

  container.appendChild(pre);

  const actions = document.createElement("div");
  actions.className = "tree-actions";
  if (selectedId) {
    const sel = nodes.find(function (n) {
      return n.id === selectedId;
    });
    if (sel) {
      const up = document.createElement("button");
      up.type = "button";
      up.className = "secondary";
      up.textContent = "Subir";
      up.addEventListener("click", function () {
        onMove(sel, "up");
      });
      const down = document.createElement("button");
      down.type = "button";
      down.className = "secondary";
      down.textContent = "Descer";
      down.addEventListener("click", function () {
        onMove(sel, "down");
      });
      actions.appendChild(up);
      actions.appendChild(down);
      if (onDelete) {
        const del = document.createElement("button");
        del.type = "button";
        del.className = "secondary danger";
        del.textContent = "Apagar nó";
        del.addEventListener("click", function () {
          onDelete(sel);
        });
        actions.appendChild(del);
      }
    }
  }
  container.appendChild(actions);
}

export function mountTechnicalTree(container, instances, options) {
  options = options || {};
  const onDelete = options.onDelete;
  container.replaceChildren();
  const pre = document.createElement("div");
  pre.className = "tree-ascii";

  if (!instances.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Nenhuma instância técnica.";
    container.appendChild(empty);
    return;
  }

  const mapped = instances.map(function (r) {
    return {
      id: r.id,
      parent_id: r.parent_id,
      sort_key: 0,
      display_code: r.export_code || "",
      node_type: r.kind,
      title: r.name,
      depth: r.depth,
    };
  });
  const kids = childrenByParent(mapped);
  const lines = [];
  walkTree(kids, "", [], lines);

  lines.forEach(function (entry) {
    const kind = labelFromMap(TECH_KIND_LABELS, entry.node.node_type);
    const code = entry.node.display_code ? entry.node.display_code + " " : "";
    const row = document.createElement("div");
    row.className = "list-item-row";
    const line = document.createElement("span");
    line.className = "tree-line";
    line.style.cursor = "default";
    line.textContent = entry.line.replace(nodeLineLabel(entry.node), code + kind + " — " + entry.node.title);
    row.appendChild(line);
    if (onDelete) {
      const inst = instances.find(function (r) {
        return r.id === entry.node.id;
      });
      if (inst) {
        const del = document.createElement("button");
        del.type = "button";
        del.className = "secondary danger";
        del.textContent = "Apagar";
        del.addEventListener("click", function () {
          onDelete(inst);
        });
        row.appendChild(del);
      }
    }
    pre.appendChild(row);
  });

  container.appendChild(pre);
}