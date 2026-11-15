const ROUTES = [
  { id: "workspace", label: "Preparar workspace", group: "Início" },
  { id: "workbook", label: "Modelo Excel", group: "Início" },
  { id: "library", label: "Biblioteca", group: "Conhecimento" },
  { id: "project", label: "Projecto (geral)", group: "Projecto" },
  { id: "project-structure", label: "Estrutura documental", group: "Projecto" },
  { id: "project-technical", label: "Árvore técnica", group: "Projecto" },
  { id: "export", label: "Exportar", group: "Ciclo LLM" },
  { id: "import", label: "Reimportar", group: "Ciclo LLM" },
  { id: "backups", label: "Backups", group: "Sistema" },
  { id: "diagnostics", label: "Diagnóstico", group: "Sistema" },
];

const BREADCRUMBS = {
  workspace: "Início / Workspace",
  workbook: "Início / Modelo Excel",
  library: "Biblioteca",
  project: "Projecto / Geral",
  "project-structure": "Projecto / Estrutura documental",
  "project-technical": "Projecto / Árvore técnica",
  export: "Exportar para LLM",
  import: "Reimportar e decidir",
  backups: "Sistema / Backups",
  diagnostics: "Sistema / Diagnóstico",
};

export function initRouter(options) {
  const nav = document.getElementById("app-nav");
  const main = document.getElementById("app-main");
  const breadcrumb = document.getElementById("app-breadcrumb");
  let current = "workspace";
  let workspaceOpen = false;

  function renderNav() {
    nav.replaceChildren();
    let lastGroup = "";
    ROUTES.forEach(function (route) {
      if (!workspaceOpen && route.id !== "workspace") return;
      if (route.group !== lastGroup) {
        const title = document.createElement("div");
        title.className = "nav-group-title";
        title.textContent = route.group;
        nav.appendChild(title);
        lastGroup = route.group;
      }
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "nav-link" + (route.id === current ? " is-active" : "");
      btn.textContent = route.label;
      btn.dataset.route = route.id;
      btn.addEventListener("click", function () {
        navigate(route.id);
      });
      nav.appendChild(btn);
    });
  }

  function navigate(routeId) {
    if (!ROUTES.some(function (r) {
      return r.id === routeId;
    })) return;
    current = routeId;
    main.querySelectorAll(".route-panel").forEach(function (panel) {
      panel.classList.toggle("is-active", panel.dataset.route === routeId);
    });
    nav.querySelectorAll(".nav-link").forEach(function (link) {
      link.classList.toggle("is-active", link.dataset.route === routeId);
    });
    if (breadcrumb) breadcrumb.textContent = BREADCRUMBS[routeId] || "";
    if (options.onRouteChange) options.onRouteChange(routeId);
    if (window.location.hash !== "#" + routeId) {
      history.replaceState(null, "", "#" + routeId);
    }
  }

  function setWorkspaceOpen(open) {
    workspaceOpen = open;
    nav.hidden = !open;
    if (open) {
      if (current === "workspace" && window.location.hash.length > 1) {
        const hash = window.location.hash.slice(1);
        if (BREADCRUMBS[hash]) current = hash;
      } else if (current === "workspace") {
        current = "library";
      }
    } else {
      current = "workspace";
    }
    renderNav();
    navigate(current);
  }

  const initial = window.location.hash ? window.location.hash.slice(1) : "workspace";
  renderNav();
  navigate(BREADCRUMBS[initial] ? initial : "workspace");

  return { navigate: navigate, setWorkspaceOpen: setWorkspaceOpen };
}