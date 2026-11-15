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

function nodePrefix(node) {
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
    lines.push({ node: node, line: prefix + nodePrefix(node) });
    const nextAncestors = ancestors.concat([!last]);
    walkTree(children, node.id, nextAncestors, lines);
  });
}

export function mountDocumentTree(container, nodes, options) {
  const selectedId = options.selectedId;
  const onSelect = options.onSelect;
  const onMove = options.onMove;

  container.replaceChildren();
  const pre = document.createElement("div");
  pre.className = "tree-ascii";

  if (!nodes.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Nenhum nó documental.";
    container.appendChild(empty);
    return;
  }

  const kids = childrenByParent(nodes);
  const lines = [];
  walkTree(kids, "", [], lines);

  lines.forEach(function (entry) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tree-line";
    if (entry.node.id === selectedId) btn.classList.add("is-selected");
    if (entry.node.depth_warning) btn.style.color = "#fca5a5";
    btn.textContent = entry.line;
    btn.addEventListener("click", function () {
      onSelect(entry.node);
    });
    pre.appendChild(btn);
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
    }
  }
  container.appendChild(actions);
}

export function mountTechnicalTree(container, instances) {
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
    const line = document.createElement("div");
    line.className = "tree-line";
    line.style.cursor = "default";
    line.textContent = entry.line.replace(nodePrefix(entry.node), code + kind + " — " + entry.node.title);
    pre.appendChild(line);
  });

  container.appendChild(pre);
}