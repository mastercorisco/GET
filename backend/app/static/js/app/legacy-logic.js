import { applyPackageBriefTemplate } from "../components/package-brief-notes.js";

export function initLegacyApp(deps = {}) {
  const mountDocumentTree = deps.mountDocumentTree;
  const mountTechnicalTree = deps.mountTechnicalTree;
  const onWorkspaceChange = deps.onWorkspaceChange;
  const onBlockSelect = deps.onBlockSelect;
  const appRouter = deps.router;
const rootPath = document.getElementById("rootPath");
      const userName = document.getElementById("userName");
      const createBtn = document.getElementById("createBtn");
      const openBtn = document.getElementById("openBtn");
      const statusEl = document.getElementById("status");
      const errorEl = document.getElementById("error");
      const loadingEl = document.getElementById("loading");
      const stateEl = document.getElementById("state");
      const emptyEl = document.getElementById("empty");

      function apiErrorMessage(body, fallback) {
        if (body && typeof body === "object" && "detail" in body) {
          const detail = body.detail;
          if (typeof detail === "string") return detail;
          if (Array.isArray(detail)) return detail.map(function (item) { return JSON.stringify(item); }).join("; ");
        }
        return fallback;
      }

      function confirmDelete(message) {
        return window.confirm(message || "Confirma eliminação? Pode ser irreversível.");
      }

      const TRASH_ICON_SVG =
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>';

      function actionDeleteButton(label, onDelete, options) {
        const opts = options || {};
        const btn = document.createElement("button");
        btn.type = "button";
        if (opts.icon) {
          btn.className = "icon-btn icon-btn--danger";
          btn.setAttribute("aria-label", label || "Apagar");
          btn.innerHTML = TRASH_ICON_SVG;
        } else {
          btn.className = "secondary danger";
          btn.textContent = label || "Apagar";
        }
        btn.addEventListener("click", function () {
          if (opts.skipConfirm || confirmDelete()) onDelete();
        });
        return btn;
      }

      function setError(message) {
        if (!message) {
          errorEl.hidden = true;
          errorEl.textContent = "";
          return;
        }
        errorEl.hidden = false;
        errorEl.textContent = message;
      }

      function showWorkspace(data) {
        loadingEl.hidden = true;
        if (data) {
          stateEl.hidden = false;
          emptyEl.hidden = true;
          rootPath.value = data.root_path;
          userName.value = data.local_user_name || "local_user";
          syncButtons();
          stateEl.textContent = [
            "Workspace aberto",
            "Pasta: " + data.root_path,
            "Utilizador: " + data.local_user_name,
            "Base de dados: " + data.database_path,
            "Backups: " + data.backups_path,
            "Exportações: " + data.exports_path,
            "Importações: " + data.imports_path,
          ].join("\n");
          if (onWorkspaceChange) onWorkspaceChange(data);
          loadKnowledge().catch(function (err) { setKnowledgeError(err.message); });
          loadProjects().catch(function (err) { setProjectError(err.message); });
        } else {
          stateEl.hidden = true;
          emptyEl.hidden = false;
          if (onWorkspaceChange) onWorkspaceChange(null);
        }
      }

      function setProjectError(message) {
        const el = document.getElementById("pError");
        if (!message) { el.hidden = true; el.textContent = ""; return; }
        el.hidden = false;
        el.textContent = message;
      }

      function setDocError(message) {
        const el = document.getElementById("docError");
        if (!message) { el.hidden = true; el.textContent = ""; return; }
        el.hidden = false;
        el.textContent = message;
        el.scrollIntoView({ block: "nearest" });
        setProjectError(message);
      }

      function setDocStatus(message) {
        const el = document.getElementById("docStatus");
        if (!message) { el.hidden = true; el.textContent = ""; return; }
        el.hidden = false;
        el.textContent = message;
      }

      let projectDeleteInFlight = false;
      let projectCatalog = [];
      let selectedLibraryItemId = null;
      let selectedProjectItemId = null;
      let libraryTerms = [];
      let selectedDocumentNodeId = null;
      let selectedDocumentBlockId = null;

      function syncDocStructureSelection(node) {
        const meta = document.getElementById("docSelectedMeta");
        const prepWrap = document.getElementById("docBlockPrepWrap");
        const prepBtn = document.getElementById("docOpenBlockPrep");
        if (!node) {
          selectedDocumentBlockId = null;
          if (meta) {
            meta.textContent = "Nenhum nó seleccionado.";
            delete meta.dataset.nodeId;
            delete meta.dataset.displayCode;
          }
          document.dispatchEvent(
            new CustomEvent("get:document-node-selected", { detail: { node: null } })
          );
          if (prepWrap) prepWrap.hidden = true;
          if (prepBtn) prepBtn.disabled = true;
          return;
        }
        if (meta) {
          meta.textContent = node.display_code + " — " + node.title;
          meta.dataset.nodeId = node.id;
          meta.dataset.displayCode = node.display_code || "";
        }
        document.dispatchEvent(
          new CustomEvent("get:document-node-selected", { detail: { node: node } })
        );
        const isBlock = node.node_type === "block";
        selectedDocumentBlockId = isBlock ? node.id : null;
        if (prepWrap) prepWrap.hidden = !isBlock;
        if (prepBtn) {
          prepBtn.disabled = !isBlock;
          prepBtn.setAttribute("aria-label", isBlock ? "Abrir preparação do bloco " + node.display_code : "");
        }
      }
      let projectKnowledgeItems = [];

      async function loadProjects() {
        setProjectError("");
        const templates = await knowledgeRequest("/api/projects/templates", {}, "Falha ao listar modelos.");
        const versionSelect = document.getElementById("pTemplateVersion");
        versionSelect.replaceChildren();
        templates.forEach(function (tpl) {
          tpl.versions.forEach(function (ver) {
            const opt = document.createElement("option");
            opt.value = ver.id;
            opt.textContent = tpl.name + " (v" + ver.version + ")";
            versionSelect.appendChild(opt);
          });
        });
        projectCatalog = await knowledgeRequest("/api/projects", {}, "Falha ao listar projetos.");
        const mgmtCount = document.getElementById("pMgmtCount");
        if (mgmtCount) {
          const n = projectCatalog.length;
          mgmtCount.textContent = n ? "(" + n + " projectos)" : "";
        }
        const list = document.getElementById("pList");
        list.replaceChildren();
        if (!projectCatalog.length) {
          const p = document.createElement("p");
          p.textContent = "Nenhum projeto.";
          list.appendChild(p);
        } else {
          projectCatalog.forEach(function (p) {
            const row = document.createElement("div");
            row.className = "list-item-row";
            const line = document.createElement("span");
            line.textContent =
              p.name + " · modelo v" + p.template_version + " · biblioteca v" + p.library_version;
            row.appendChild(line);
            row.appendChild(
              actionDeleteButton(
                "Apagar projecto",
                function () {
                  if (projectDeleteInFlight) {
                    setProjectError("Apagar projecto em curso — aguarde.");
                    return;
                  }
                  if (
                    !confirmDelete(
                      "Apagar o projecto «" +
                        p.name +
                        "» e toda a estrutura, conhecimento, baselines e importações?"
                    )
                  ) {
                    return;
                  }
                  projectDeleteInFlight = true;
                  setProjectError("A apagar projecto… (projectos grandes podem demorar até um minuto)");
                  const deleteUrl = "/api/projects/" + p.id;
                  document.querySelectorAll(".project-list-panel .icon-btn--danger").forEach(function (b) {
                    b.disabled = true;
                  });
                  knowledgeRequest(deleteUrl, { method: "DELETE" }, "Falha ao apagar projecto.")
                    .then(function () {
                      if (selectedDocumentNodeId) {
                        selectedDocumentNodeId = null;
                        syncDocStructureSelection(null);
                      }
                      return loadProjects();
                    })
                    .catch(function (err) {
                      setProjectError(err.message);
                    })
                    .finally(function () {
                      projectDeleteInFlight = false;
                      document.querySelectorAll(".project-list-panel .icon-btn--danger").forEach(function (b) {
                        b.disabled = false;
                      });
                    });
                },
                { icon: true, skipConfirm: true }
              )
            );
            list.appendChild(row);
          });
        }
        const active = document.getElementById("pActive");
        active.replaceChildren();
        projectCatalog.forEach(function (p) {
          const opt = document.createElement("option");
          opt.value = p.id;
          opt.textContent = p.name;
          active.appendChild(opt);
        });
        if (projectCatalog.length) {
          active.value = projectCatalog[0].id;
          await loadProjectDetail(projectCatalog[0].id);
        } else {
          document.getElementById("iList").replaceChildren();
          document.getElementById("pkList").replaceChildren();
          document.getElementById("docList").replaceChildren();
          document.getElementById("docAssocList").replaceChildren();
        }
      }

      function renderDocumentTree(nodes) {
        const list = document.getElementById("docList");
        const warnEl = document.getElementById("docDepthWarn");
        const anyWarn = nodes.some(function (n) { return n.depth_warning; });
        warnEl.hidden = !anyWarn;

        const parentSelect = document.getElementById("docParent");
        parentSelect.replaceChildren();
        const rootOpt = document.createElement("option");
        rootOpt.value = "";
        rootOpt.textContent = "— raiz (só fascículo) —";
        parentSelect.appendChild(rootOpt);
        nodes.forEach(function (n) {
          const opt = document.createElement("option");
          opt.value = n.id;
          opt.textContent = n.display_code + " · " + n.title;
          parentSelect.appendChild(opt);
        });

        if (mountDocumentTree) {
          mountDocumentTree(list, nodes, {
            projectId: nodes.length ? nodes[0].project_id : null,
            selectedId: selectedDocumentNodeId,
            onSelect: function (node) {
              selectedDocumentNodeId = node.id;
              syncDocStructureSelection(node);
              loadDocumentAssociations(node.id).catch(function (err) { setProjectError(err.message); });
              renderDocumentTree(nodes);
            },
            onMove: function (node, direction) {
              moveDocumentNode(node.project_id, node.id, { direction: direction });
            },
            onDelete: function (node) {
              if (
                !confirmDelete(
                  "Apagar «" +
                    node.display_code +
                    "» e todos os subnós? Blocos com pontos de desenvolvimento serão removidos."
                )
              ) {
                return;
              }
              knowledgeRequest(
                "/api/projects/" + node.project_id + "/document-nodes/" + node.id,
                { method: "DELETE" },
                "Falha ao apagar nó."
              )
                .then(function () {
                  if (selectedDocumentNodeId === node.id) {
                    selectedDocumentNodeId = null;
                    syncDocStructureSelection(null);
                  }
                  return loadDocumentTree(node.project_id);
                })
                .catch(function (err) {
                  setProjectError(err.message);
                });
            },
          });
          return;
        }

        list.replaceChildren();
        if (!nodes.length) {
          const empty = document.createElement("p");
          empty.textContent = "Nenhum nó documental.";
          list.appendChild(empty);
        }
      }

      async function loadDocumentAssociations(nodeId) {
        const rows = await knowledgeRequest(
          "/api/document-nodes/" + nodeId + "/associations",
          {},
          "Falha ao listar associações."
        );
        const target = document.getElementById("docAssocList");
        target.replaceChildren();
        if (!rows.length) {
          const empty = document.createElement("p");
          empty.textContent = "Sem associações.";
          target.appendChild(empty);
          return;
        }
        rows.forEach(function (row) {
          const line = document.createElement("div");
          line.className = "list-item-row";
          const text = document.createElement("span");
          text.textContent =
            row.role +
            " → " +
            row.knowledge_item_id +
            (row.usage_instruction ? " · " + row.usage_instruction : "");
          line.appendChild(text);
          line.appendChild(
            actionDeleteButton("Apagar", function () {
              knowledgeRequest(
                "/api/document-nodes/associations/" + row.id,
                { method: "DELETE" },
                "Falha ao apagar associação."
              )
                .then(function () {
                  return loadDocumentAssociations(nodeId);
                })
                .catch(function (err) {
                  setProjectError(err.message);
                });
            })
          );
          target.appendChild(line);
        });
      }

      async function loadDocumentTree(projectId) {
        setDocError("");
        const data = await knowledgeRequest(
          "/api/projects/" + projectId + "/document-nodes",
          {},
          "Falha ao carregar estrutura documental."
        );
        if (selectedDocumentNodeId && !data.nodes.some(function (n) { return n.id === selectedDocumentNodeId; })) {
          selectedDocumentNodeId = null;
          syncDocStructureSelection(null);
          document.getElementById("docAssocList").replaceChildren();
        } else if (selectedDocumentNodeId) {
          const sel = data.nodes.find(function (n) { return n.id === selectedDocumentNodeId; });
          if (sel) syncDocStructureSelection(sel);
        }
        renderDocumentTree(data.nodes);
      }

      function moveDocumentNode(projectId, nodeId, body) {
        knowledgeRequest("/api/projects/" + projectId + "/document-nodes/" + nodeId + "/move", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }, "Falha ao mover nó.")
          .then(function () { return loadDocumentTree(projectId); })
          .catch(function (err) { setProjectError(err.message); });
      }

      async function loadProjectDetail(projectId) {
        const instances = await knowledgeRequest("/api/projects/" + projectId + "/instances", {}, "Falha ao listar instâncias.");
        const iList = document.getElementById("iList");
        if (mountTechnicalTree) {
          mountTechnicalTree(iList, instances, {
            onDelete: function (inst) {
              knowledgeRequest(
                "/api/projects/" + projectId + "/instances/" + inst.id,
                { method: "DELETE" },
                "Falha ao apagar instância."
              )
                .then(function () {
                  return loadProjectDetail(projectId);
                })
                .catch(function (err) {
                  setProjectError(err.message);
                });
            },
          });
        } else {
          iList.replaceChildren();
          instances.forEach(function (row) {
            const line = document.createElement("p");
            line.style.marginLeft = row.depth * 1.25 + "rem";
            line.textContent = row.kind + ": " + row.name + (row.export_code ? " [" + row.export_code + "]" : "");
            iList.appendChild(line);
          });
        }
        const parentSelect = document.getElementById("iParent");
        parentSelect.replaceChildren();
        const empty = document.createElement("option");
        empty.value = "";
        empty.textContent = "—";
        parentSelect.appendChild(empty);
        instances.forEach(function (row) {
          const opt = document.createElement("option");
          opt.value = row.id;
          opt.textContent = row.name;
          parentSelect.appendChild(opt);
        });
        const pk = await knowledgeRequest(
          "/api/knowledge?scope_type=project&scope_id=" + encodeURIComponent(projectId),
          {},
          "Falha ao listar conhecimento do projeto."
        );
        const libraryItems = await knowledgeRequest(
          "/api/knowledge?scope_type=library",
          {},
          "Falha ao listar biblioteca."
        );
        projectKnowledgeItems = pk.concat(libraryItems);
        const assocSelect = document.getElementById("docAssocItem");
        assocSelect.replaceChildren();
        const emptyItem = document.createElement("option");
        emptyItem.value = "";
        emptyItem.textContent = "—";
        assocSelect.appendChild(emptyItem);
        if (libraryItems.length) {
          const libGroup = document.createElement("optgroup");
          libGroup.label = "Biblioteca";
          libraryItems.forEach(function (item) {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.title;
            libGroup.appendChild(opt);
          });
          assocSelect.appendChild(libGroup);
        }
        if (pk.length) {
          const projGroup = document.createElement("optgroup");
          projGroup.label = "Projecto";
          pk.forEach(function (item) {
            const opt = document.createElement("option");
            opt.value = item.id;
            opt.textContent = item.title;
            projGroup.appendChild(opt);
          });
          assocSelect.appendChild(projGroup);
        }
        renderItems(document.getElementById("pkList"), pk, false);
        await loadDocumentTree(projectId);
        if (selectedDocumentNodeId) {
          await loadDocumentAssociations(selectedDocumentNodeId);
        }
        if (selectedProjectItemId) {
          const found = pk.find(function (i) { return i.id === selectedProjectItemId; });
          if (found) applyProfileToForm("pk", found);
        }
        try {
          await loadProjectReferences(projectId);
        } catch (err) {
          setProjectError(err.message);
        }
        try {
          await loadProjectTerminologyOverrides(projectId);
        } catch (err) {
          setProjectError(err.message);
        }
        try {
          await loadExportSection(projectId);
        } catch (err) {
          setProjectError(err.message);
        }
        try {
          await loadImportSection(projectId);
        } catch (err) {
          setProjectError(err.message);
        }
      }

      let activeMergeSessionId = null;
      let lastUploadedImportId = null;
      let lastUploadedImportIsPackage = false;
      let lastFasciclePackageExport = null;

      function downloadTextFile(filename, text) {
        const blob = new Blob([text], { type: "application/json;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename || "GET-pacote.json";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      }

      function copyPackageBrief(text) {
        if (!text) return Promise.reject(new Error("Sem brief para copiar."));
        const done = function () {
          setExportStatus("Brief copiado — cole na LLM junto com o JSON.");
        };
        if (navigator.clipboard && window.isSecureContext) {
          return navigator.clipboard.writeText(text).then(done);
        }
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try {
          if (!document.execCommand("copy")) throw new Error("Cópia não suportada neste browser.");
          done();
          return Promise.resolve();
        } finally {
          document.body.removeChild(ta);
        }
      }

      function setImportStatus(message) {
        const el = document.getElementById("impStatus");
        if (!message) {
          el.hidden = true;
          el.textContent = "";
          return;
        }
        el.hidden = false;
        el.textContent = message;
      }

      async function loadImportSection(projectId) {
        const list = document.getElementById("impList");
        const fascicleSelect = document.getElementById("impFascicle");
        list.replaceChildren();
        fascicleSelect.replaceChildren();
        const empty = document.createElement("option");
        empty.value = "";
        empty.textContent = "—";
        fascicleSelect.appendChild(empty);
        const nodesPayload = await knowledgeRequest(
          "/api/projects/" + projectId + "/document-nodes",
          {},
          "Falha ao listar estrutura."
        );
        const nodeRows = Array.isArray(nodesPayload) ? nodesPayload : (nodesPayload.nodes || []);
        nodeRows.forEach(function (row) {
          if (row.node_type === "fascicle" && !row.parent_id) {
            const opt = document.createElement("option");
            opt.value = row.id;
            opt.textContent = (row.display_code ? row.display_code + " — " : "") + row.title;
            fascicleSelect.appendChild(opt);
          }
        });
        const imports = await knowledgeRequest(
          "/api/projects/" + projectId + "/imports",
          {},
          "Falha ao listar importações."
        );
        imports.forEach(function (row) {
          const p = document.createElement("p");
          p.textContent =
            row.id.slice(0, 8) + "… · " + row.status + " · quarentena " + row.quarantine_count;
          p.dataset.importId = row.id;
          list.appendChild(p);
        });
        document.getElementById("impProposals").replaceChildren();
        document.getElementById("impConsolidate").hidden = true;
        activeMergeSessionId = null;
      }

      function renderProposals(projectId, merge) {
        activeMergeSessionId = merge.id;
        const mergeRoot = lastUploadedImportIsPackage
          ? "/api/projects/" + projectId + "/packages/merge/"
          : "/api/projects/" + projectId + "/imports/merge/";
        const target = document.getElementById("impProposals");
        target.replaceChildren();
        if (!merge.proposals.length) {
          const p = document.createElement("p");
          p.textContent = "Sem propostas (ou omissões tratadas como no-op).";
          target.appendChild(p);
        }
        merge.proposals.forEach(function (prop) {
          const box = document.createElement("div");
          box.style.marginBottom = "1rem";
          const title = document.createElement("p");
          title.textContent =
            prop.proposal_kind + " · " + prop.title +
            (prop.conflict ? " · conflito" : "") +
            (prop.protected_touch ? " · protegido" : "");
          box.appendChild(title);
          const dec = document.createElement("select");
          dec.innerHTML = "<option value=''>—</option><option value='accepted'>aceitar</option><option value='rejected'>rejeitar</option>";
          if (prop.decision) dec.value = prop.decision;
          const dest = document.createElement("select");
          dest.innerHTML = "<option value='project'>project</option><option value='library'>library</option><option value='pending'>pending</option><option value='rejected'>rejected</option>";
          if (prop.destination) dest.value = prop.destination;
          const confirm = document.createElement("input");
          confirm.type = "checkbox";
          confirm.checked = !!prop.confirmed_protected;
          const save = document.createElement("button");
          save.type = "button";
          save.textContent = "Guardar decisão";
          save.className = "secondary";
          save.addEventListener("click", function () {
            if (!dec.value) {
              setImportStatus("Seleccione aceitar ou rejeitar.");
              return;
            }
            knowledgeRequest(
              mergeRoot + merge.id + "/proposals/" + prop.id,
              {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  decision: dec.value,
                  destination: dest.value,
                  confirmed_protected: confirm.checked,
                }),
              },
              "Falha ao guardar decisão."
            ).then(function () { setImportStatus("Decisão guardada."); })
              .catch(function (err) { setImportStatus(err.message); });
          });
          box.appendChild(dec);
          box.appendChild(dest);
          box.appendChild(confirm);
          box.appendChild(save);
          target.appendChild(box);
        });
        document.getElementById("impConsolidate").hidden = false;
      }

      function setExportStatus(message) {
        const el = document.getElementById("expStatus");
        if (!message) {
          el.hidden = true;
          el.textContent = "";
          return;
        }
        el.hidden = false;
        el.textContent = message;
      }

      async function loadExportSection(projectId) {
        const expBriefLabel = document.querySelector('label[data-help-key="export.get_package_brief"]');
        if (expBriefLabel) {
          expBriefLabel.querySelector(".field-help-btn")?.remove();
          delete expBriefLabel.dataset.helpWired;
        }
        applyPackageBriefTemplate("expPkgBriefNotes", "loadExportSection");
        const meta = document.getElementById("expBaselineMeta");
        const fascicleSelect = document.getElementById("expFascicle");
        const pkgFascicleSelect = document.getElementById("expFasciclePkg");
        const llmFascicleSelect = document.getElementById("expLlmFascicle");
        const list = document.getElementById("expList");
        list.replaceChildren();
        fascicleSelect.replaceChildren();
        const empty = document.createElement("option");
        empty.value = "";
        empty.textContent = "—";
        fascicleSelect.appendChild(empty);
        if (pkgFascicleSelect) {
          pkgFascicleSelect.replaceChildren();
          pkgFascicleSelect.appendChild(empty.cloneNode(true));
        }
        if (llmFascicleSelect) {
          const keep = llmFascicleSelect.querySelector('option[value=""]');
          llmFascicleSelect.replaceChildren();
          if (keep) {
            llmFascicleSelect.appendChild(keep);
          } else {
            const allOpt = document.createElement("option");
            allOpt.value = "";
            allOpt.textContent = "Projecto inteiro";
            llmFascicleSelect.appendChild(allOpt);
          }
        }

        const baseline = await knowledgeRequest(
          "/api/projects/" + projectId + "/baselines/latest",
          {},
          "Falha ao obter baseline."
        );
        if (!baseline) {
          meta.textContent = "Baseline: nenhuma — publique antes do mestre.";
        } else {
          meta.textContent = "Baseline " + baseline.code + " · rev. " + baseline.revision;
        }

        const nodesPayload = await knowledgeRequest(
          "/api/projects/" + projectId + "/document-nodes",
          {},
          "Falha ao listar estrutura documental."
        );
        const nodeRows = Array.isArray(nodesPayload) ? nodesPayload : (nodesPayload.nodes || []);
        nodeRows.forEach(function (row) {
          if (row.node_type === "fascicle" && !row.parent_id) {
            const label = (row.display_code ? row.display_code + " — " : "") + row.title;
            const opt = document.createElement("option");
            opt.value = row.id;
            opt.textContent = label;
            fascicleSelect.appendChild(opt);
            if (pkgFascicleSelect) {
              const optPkg = document.createElement("option");
              optPkg.value = row.id;
              optPkg.textContent = label;
              pkgFascicleSelect.appendChild(optPkg);
            }
            if (llmFascicleSelect) {
              const opt2 = document.createElement("option");
              opt2.value = row.id;
              opt2.textContent = label;
              llmFascicleSelect.appendChild(opt2);
            }
          }
        });

        const exports = await knowledgeRequest(
          "/api/projects/" + projectId + "/exports",
          {},
          "Falha ao listar exportações."
        );
        exports.forEach(function (row) {
          const p = document.createElement("p");
          p.textContent =
            row.export_id +
            " · " +
            row.package_type +
            " · " +
            row.profile +
            " · sha256 " +
            row.sha256.slice(0, 12) +
            "…";
          list.appendChild(p);
        });

        try {
          const llmCtx = await knowledgeRequest(
            "/api/projects/" + projectId + "/llm-context",
            {},
            "Falha ao carregar contexto LLM."
          );
          const ctx = llmCtx.context || {};
          const loc = ctx.location || {};
          const codeEl = document.getElementById("expLlmCode");
          const ownerEl = document.getElementById("expLlmOwner");
          const siteEl = document.getElementById("expLlmSite");
          const docEl = document.getElementById("expLlmDocType");
          if (codeEl) codeEl.value = ctx.code || "";
          if (ownerEl) ownerEl.value = ctx.owner || "";
          if (siteEl) siteEl.value = loc.site || "";
          if (docEl) docEl.value = ctx.document_type || "";
        } catch (_err) {
          /* opcional */
        }
      }

      function setKnowledgeError(message) {
        const el = document.getElementById("kError");
        if (!message) {
          el.hidden = true;
          el.textContent = "";
          return;
        }
        el.hidden = false;
        el.textContent = message;
      }

      function knowledgePayload() {
        return {
          title: document.getElementById("kTitle").value.trim(),
          content: document.getElementById("kContent").value.trim(),
          origin_context: document.getElementById("kContext").value.trim(),
        };
      }

      async function knowledgeRequest(url, options, fallback) {
        const opts = options || {};
        const res = await fetch(url, opts);
        if (!res.ok) {
          const payload = await res.json().catch(function () { return {}; });
          let msg = apiErrorMessage(payload, fallback);
          if (res.status === 404 && (url.indexOf("/document-nodes") !== -1 || url.indexOf("/references") !== -1 || url.indexOf("/terminology") !== -1 || url.indexOf("/baselines") !== -1 || url.indexOf("/exports") !== -1 || url.indexOf("/imports") !== -1)) {
            msg =
              "Servidor desatualizado (rotas E04–E07 em falta). Feche todas as janelas \"GET\" do uvicorn e execute de novo Arranque GET.bat.";
          }
          throw new Error(msg);
        }
        if (res.status === 204) return null;
        const text = await res.text();
        if (!text) return null;
        return JSON.parse(text);
      }

      function applyProfileToForm(prefix, item) {
        const meta = document.getElementById(prefix + "ProfileMeta");
        const typeEl = document.getElementById(prefix + "ProfileType");
        const dataEl = document.getElementById(prefix + "ProfileData");
        const warnEl = document.getElementById(prefix === "k" ? "kProfileWarn" : null);
        if (!item) {
          meta.textContent = "Seleccione uma unidade na lista.";
          dataEl.value = "";
          if (warnEl) { warnEl.hidden = true; warnEl.textContent = ""; }
          return;
        }
        meta.textContent = item.title + " (" + item.id + ")";
        const profile = item.technical_profile;
        if (profile) {
          typeEl.value = profile.profile_type;
          dataEl.value = JSON.stringify(profile.data, null, 2);
          if (warnEl && profile.validation_warnings && profile.validation_warnings.length) {
            warnEl.hidden = false;
            warnEl.textContent = profile.validation_warnings.join(" ");
          } else if (warnEl) {
            warnEl.hidden = true;
            warnEl.textContent = "";
          }
        } else {
          dataEl.value = "{}";
          if (warnEl) { warnEl.hidden = true; warnEl.textContent = ""; }
        }
      }

      function saveTechnicalProfile(itemId, prefix, onDone) {
        let data;
        try {
          data = JSON.parse(document.getElementById(prefix + "ProfileData").value || "{}");
        } catch (e) {
          setKnowledgeError("JSON da ficha inválido.");
          return;
        }
        knowledgeRequest("/api/knowledge/" + itemId + "/technical-profile", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            profile_type: document.getElementById(prefix + "ProfileType").value,
            data: data,
          }),
        }, "Falha ao guardar ficha.")
          .then(onDone)
          .catch(function (err) { setKnowledgeError(err.message); });
      }

      async function loadLibraryReferences() {
        const rows = await knowledgeRequest("/api/references?scope_type=library", {}, "Falha ao listar referências.");
        const list = document.getElementById("libRefList");
        list.replaceChildren();
        rows.forEach(function (row) {
          const p = document.createElement("div");
          p.className = "list-item-row";
          const text = document.createElement("span");
          text.textContent =
            row.title +
            (row.standard_profile && row.standard_profile.contractual_role
              ? " · " + row.standard_profile.contractual_role
              : "");
          p.appendChild(text);
          p.appendChild(
            actionDeleteButton("Apagar", function () {
              knowledgeRequest("/api/references/" + row.id, { method: "DELETE" }, "Falha ao apagar referência.")
                .then(loadLibraryReferences)
                .catch(function (err) {
                  setKnowledgeError(err.message);
                });
            })
          );
          list.appendChild(p);
        });
      }

      async function loadLibraryTerminology() {
        libraryTerms = await knowledgeRequest("/api/terminology?scope_type=library", {}, "Falha ao listar terminologia.");
        const list = document.getElementById("libTermList");
        list.replaceChildren();
        libraryTerms.forEach(function (row) {
          const p = document.createElement("div");
          p.className = "list-item-row";
          const text = document.createElement("span");
          text.textContent = row.preferred_term + " — " + row.definition.substring(0, 80);
          p.appendChild(text);
          p.appendChild(
            actionDeleteButton("Apagar", function () {
              knowledgeRequest("/api/terminology/" + row.id, { method: "DELETE" }, "Falha ao apagar termo.")
                .then(loadLibraryTerminology)
                .catch(function (err) {
                  setKnowledgeError(err.message);
                });
            })
          );
          list.appendChild(p);
        });
        const conceptSel = document.getElementById("termOverrideConcept");
        conceptSel.replaceChildren();
        const empty = document.createElement("option");
        empty.value = "";
        empty.textContent = "—";
        conceptSel.appendChild(empty);
        libraryTerms.forEach(function (row) {
          const opt = document.createElement("option");
          opt.value = row.id;
          opt.textContent = row.preferred_term;
          conceptSel.appendChild(opt);
        });
      }

      async function loadProjectReferences(projectId) {
        const rows = await knowledgeRequest(
          "/api/references?scope_type=project&scope_id=" + encodeURIComponent(projectId),
          {},
          "Falha ao listar referências do projecto."
        );
        const list = document.getElementById("projRefList");
        const sel = document.getElementById("projRefStandard");
        list.replaceChildren();
        sel.replaceChildren();
        const empty = document.createElement("option");
        empty.value = "";
        empty.textContent = "—";
        sel.appendChild(empty);
        rows.forEach(function (row) {
          const p = document.createElement("div");
          p.className = "list-item-row";
          const text = document.createElement("span");
          text.textContent = row.title + (row.standard_profile ? " · norma" : "");
          p.appendChild(text);
          p.appendChild(
            actionDeleteButton("Apagar", function () {
              knowledgeRequest("/api/references/" + row.id, { method: "DELETE" }, "Falha ao apagar referência.")
                .then(function () {
                  return loadProjectReferences(projectId);
                })
                .catch(function (err) {
                  setProjectError(err.message);
                });
            })
          );
          list.appendChild(p);
          const opt = document.createElement("option");
          opt.value = row.id;
          opt.textContent = row.title;
          sel.appendChild(opt);
        });
      }

      async function loadProjectTerminologyOverrides(projectId) {
        const rows = await knowledgeRequest(
          "/api/projects/" + projectId + "/terminology-overrides",
          {},
          "Falha ao listar overrides."
        );
        const list = document.getElementById("projTermOverrideList");
        list.replaceChildren();
        rows.forEach(function (row) {
          const p = document.createElement("div");
          p.className = "list-item-row";
          const text = document.createElement("span");
          text.textContent = row.preferred_term + " → legado: " + (row.legacy_term || "—");
          p.appendChild(text);
          p.appendChild(
            actionDeleteButton("Apagar", function () {
              knowledgeRequest(
                "/api/projects/" + projectId + "/terminology-overrides/" + row.id,
                { method: "DELETE" },
                "Falha ao apagar override."
              )
                .then(function () {
                  return loadProjectTerminologyOverrides(projectId);
                })
                .catch(function (err) {
                  setProjectError(err.message);
                });
            })
          );
          list.appendChild(p);
        });
      }

      function renderItems(target, items, showConclude) {
        if (showConclude === undefined) showConclude = target.id === "kList";
        const isLibrary = target.id === "kList";
        const isProject = target.id === "pkList";
        target.replaceChildren();
        if (!items.length) {
          const empty = document.createElement("p");
          empty.textContent = "Nenhuma unidade.";
          target.appendChild(empty);
          return;
        }
        items.forEach(function (item) {
          const block = document.createElement("div");
          block.className = "item";
          const title = document.createElement("strong");
          title.textContent = item.title;
          const meta = document.createElement("p");
          meta.textContent = item.status_label + " · " + item.scope_type + " · " + item.id;
          if (item.technical_profile) {
            meta.textContent += " · ficha:" + item.technical_profile.profile_type;
          }
          block.appendChild(title);
          block.appendChild(meta);
          const pick = document.createElement("button");
          pick.type = "button";
          pick.className = "secondary";
          pick.textContent = "Seleccionar para ficha";
          pick.addEventListener("click", function () {
            if (isLibrary) {
              selectedLibraryItemId = item.id;
              applyProfileToForm("k", item);
            }
            if (isProject) {
              selectedProjectItemId = item.id;
              applyProfileToForm("pk", item);
            }
          });
          block.appendChild(pick);
          if (showConclude) {
            const conclude = document.createElement("button");
            conclude.type = "button";
            conclude.textContent = "Concluir revisão";
            conclude.addEventListener("click", function () {
              knowledgeRequest("/api/knowledge/" + item.id + "/conclude", { method: "POST" }, "Falha ao concluir revisão.")
                .then(loadKnowledge)
                .catch(function (err) { setKnowledgeError(err.message); });
            });
            block.appendChild(conclude);
          }
          const remove = actionDeleteButton("Apagar", function () {
            knowledgeRequest("/api/knowledge/" + item.id, { method: "DELETE" }, "Falha ao apagar unidade.")
              .then(function (result) {
                if (isLibrary && selectedLibraryItemId === item.id) selectedLibraryItemId = null;
                if (isProject && selectedProjectItemId === item.id) selectedProjectItemId = null;
                const msg = result && result.detail ? result.detail : "";
                if (msg) setKnowledgeError(msg);
                if (isLibrary) return loadKnowledge();
                return loadProjectDetail(document.getElementById("pActive").value);
              })
              .catch(function (err) {
                if (isLibrary) setKnowledgeError(err.message);
                else setProjectError(err.message);
              });
          });
          block.appendChild(remove);
          target.appendChild(block);
        });
      }

      async function loadKnowledge() {
        setKnowledgeError("");
        const items = await knowledgeRequest("/api/knowledge?scope_type=library", {}, "Falha ao listar unidades.");
        renderItems(document.getElementById("kList"), items);
        if (selectedLibraryItemId) {
          const found = items.find(function (i) { return i.id === selectedLibraryItemId; });
          if (found) applyProfileToForm("k", found);
        }
        try {
          await loadLibraryReferences();
        } catch (err) {
          setKnowledgeError(err.message);
        }
        try {
          await loadLibraryTerminology();
        } catch (err) {
          setKnowledgeError(err.message);
        }
      }

      async function refresh() {
        loadingEl.hidden = false;
        emptyEl.hidden = true;
        stateEl.hidden = true;
        const res = await fetch("/api/workspace");
        if (!res.ok) throw new Error("Falha ao obter workspace.");
        const data = await res.json();
        showWorkspace(data);
      }

      async function postWorkspace(url, body, fallback) {
        setError("");
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) {
          const payload = await res.json().catch(function () { return {}; });
          throw new Error(apiErrorMessage(payload, fallback));
        }
        const opened = await res.json();
        statusEl.hidden = false;
        statusEl.textContent = "Workspace aberto: " + (opened.root_path || rootPath.value.trim());
        await refresh();
      }

      function syncButtons() {
        const disabled = !rootPath.value.trim();
        createBtn.disabled = disabled;
        openBtn.disabled = disabled;
      }

      rootPath.addEventListener("input", syncButtons);
      createBtn.addEventListener("click", function () {
        postWorkspace("/api/workspace/create", {
          root_path: rootPath.value.trim(),
          local_user_name: userName.value.trim() || "local_user",
        }, "Falha ao criar workspace.").catch(function (err) { setError(err.message); });
      });
      openBtn.addEventListener("click", function () {
        postWorkspace("/api/workspace/open", {
          root_path: rootPath.value.trim(),
        }, "Falha ao abrir workspace.").catch(function (err) { setError(err.message); });
      });

      document.getElementById("kCreate").addEventListener("click", function () {
        const body = knowledgePayload();
        if (!body.title || !body.content || !body.origin_context) {
          setKnowledgeError("Preencha título, conteúdo e contexto de origem.");
          return;
        }
        knowledgeRequest("/api/knowledge", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }, "Falha ao criar unidade.")
          .then(function () {
            document.getElementById("kTitle").value = "";
            document.getElementById("kContent").value = "";
            document.getElementById("kContext").value = "";
            return loadKnowledge();
          })
          .catch(function (err) { setKnowledgeError(err.message); });
      });
      document.getElementById("pCreate").addEventListener("click", function () {
        const body = {
          template_version_id: document.getElementById("pTemplateVersion").value,
          name: document.getElementById("pName").value.trim(),
          intervention_type: document.getElementById("pIntervention").value.trim() || "brownfield",
        };
        if (!body.template_version_id || !body.name) {
          setProjectError("Seleccione o modelo e indique o nome do projeto.");
          return;
        }
        knowledgeRequest("/api/projects", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }, "Falha ao criar projeto.")
          .then(function () {
            document.getElementById("pName").value = "";
            return loadProjects();
          })
          .catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("pActive").addEventListener("change", function () {
        lastUploadedImportId = null;
        lastUploadedImportIsPackage = false;
        loadProjectDetail(this.value).catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("iCreate").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const name = document.getElementById("iName").value.trim();
        if (!projectId || !name) {
          setProjectError("Seleccione um projeto e indique o nome da instância.");
          return;
        }
        const parent = document.getElementById("iParent").value;
        knowledgeRequest("/api/projects/" + projectId + "/instances", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            kind: document.getElementById("iKind").value,
            name: name,
            parent_id: parent || null,
          }),
        }, "Falha ao criar instância.")
          .then(function () {
            document.getElementById("iName").value = "";
            return loadProjectDetail(projectId);
          })
          .catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("docType").addEventListener("change", function () {
        if (this.value === "fascicle") {
          document.getElementById("docParent").value = "";
        }
      });
      document.getElementById("docCreate").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const title = document.getElementById("docTitle").value.trim();
        const nodeType = document.getElementById("docType").value;
        const parent = document.getElementById("docParent").value;
        if (!projectId || !title) {
          setDocError("Seleccione o projeto activo (em cima) e indique o título do nó.");
          return;
        }
        setDocStatus("A criar nó…");
        const parentId = nodeType === "fascicle" ? null : (parent || null);
        knowledgeRequest("/api/projects/" + projectId + "/document-nodes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            node_type: nodeType,
            title: title,
            parent_id: parentId,
          }),
        }, "Falha ao criar nó documental.")
          .then(function (body) {
            setDocStatus("");
            document.getElementById("docTitle").value = "";
            return loadDocumentTree(projectId);
          })
          .then(function () {
            setDocStatus("Nó criado.");
          })
          .catch(function (err) {
            setDocStatus("");
            setDocError(err.message);
          });
      });
      document.getElementById("docOpenBlockPrep")?.addEventListener("click", function () {
        if (!selectedDocumentBlockId || !onBlockSelect) return;
        onBlockSelect(selectedDocumentBlockId);
      });
      document.getElementById("docAssocCreate").addEventListener("click", function () {
        const nodeId = selectedDocumentNodeId;
        const itemId = document.getElementById("docAssocItem").value;
        if (!nodeId || !itemId) {
          setProjectError("Seleccione um nó e uma unidade de conhecimento.");
          return;
        }
        knowledgeRequest("/api/document-nodes/" + nodeId + "/associations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            knowledge_item_id: itemId,
            role: document.getElementById("docAssocRole").value,
            usage_instruction: document.getElementById("docAssocInstruction").value.trim() || null,
          }),
        }, "Falha ao criar associação.")
          .then(function () {
            document.getElementById("docAssocInstruction").value = "";
            return loadDocumentAssociations(nodeId);
          })
          .catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("pkCreate").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const body = {
          title: document.getElementById("pkTitle").value.trim(),
          content: document.getElementById("pkContent").value.trim(),
          origin_context: document.getElementById("pkContext").value.trim(),
          scope_type: "project",
          scope_id: projectId,
        };
        if (!projectId || !body.title || !body.content || !body.origin_context) {
          setProjectError("Preencha o projeto activo e os campos da unidade.");
          return;
        }
        knowledgeRequest("/api/knowledge", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }, "Falha ao criar unidade no projeto.")
          .then(function () {
            document.getElementById("pkTitle").value = "";
            document.getElementById("pkContent").value = "";
            document.getElementById("pkContext").value = "";
            return loadProjectDetail(projectId);
          })
          .catch(function (err) { setProjectError(err.message); });
      });

      document.getElementById("kProfileSave").addEventListener("click", function () {
        if (!selectedLibraryItemId) {
          setKnowledgeError("Seleccione uma unidade da biblioteca.");
          return;
        }
        saveTechnicalProfile(selectedLibraryItemId, "k", loadKnowledge);
      });
      document.getElementById("pkProfileSave").addEventListener("click", function () {
        if (!selectedProjectItemId) {
          setProjectError("Seleccione uma unidade do projecto.");
          return;
        }
        const projectId = document.getElementById("pActive").value;
        saveTechnicalProfile(selectedProjectItemId, "pk", function () {
          return loadProjectDetail(projectId);
        });
      });
      document.getElementById("libRefCreate").addEventListener("click", function () {
        const title = document.getElementById("libRefTitle").value.trim();
        if (!title) { setKnowledgeError("Indique o título da referência."); return; }
        knowledgeRequest("/api/references", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            scope_type: "library",
            title: title,
            citation: document.getElementById("libRefCitation").value.trim() || null,
          }),
        }, "Falha ao criar referência.")
          .then(function () {
            document.getElementById("libRefTitle").value = "";
            document.getElementById("libRefCitation").value = "";
            return loadLibraryReferences();
          })
          .catch(function (err) { setKnowledgeError(err.message); });
      });
      document.getElementById("libTermCreate").addEventListener("click", function () {
        const preferred = document.getElementById("libTermPreferred").value.trim();
        const definition = document.getElementById("libTermDefinition").value.trim();
        if (!preferred || !definition) {
          setKnowledgeError("Preencha termo e definição.");
          return;
        }
        const syns = document.getElementById("libTermSynonyms").value.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
        knowledgeRequest("/api/terminology", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            scope_type: "library",
            preferred_term: preferred,
            definition: definition,
            synonyms: syns,
          }),
        }, "Falha ao criar termo.")
          .then(function () {
            document.getElementById("libTermPreferred").value = "";
            document.getElementById("libTermDefinition").value = "";
            document.getElementById("libTermSynonyms").value = "";
            return loadLibraryTerminology();
          })
          .catch(function (err) { setKnowledgeError(err.message); });
      });
      document.getElementById("projRefCreate").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const title = document.getElementById("projRefTitle").value.trim();
        if (!projectId || !title) { setProjectError("Projecto e título obrigatórios."); return; }
        knowledgeRequest("/api/references", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scope_type: "project", scope_id: projectId, title: title }),
        }, "Falha ao criar referência.")
          .then(function () {
            document.getElementById("projRefTitle").value = "";
            return loadProjectReferences(projectId);
          })
          .catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("projRefStandardSave").addEventListener("click", function () {
        const refId = document.getElementById("projRefStandard").value;
        if (!refId) { setProjectError("Seleccione uma referência."); return; }
        knowledgeRequest("/api/references/" + refId + "/standard-profile", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ contractual_role: document.getElementById("projRefRole").value }),
        }, "Falha ao guardar ficha normativa.")
          .then(function () {
            const projectId = document.getElementById("pActive").value;
            return loadProjectReferences(projectId);
          })
          .catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("termOverrideCreate").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const conceptId = document.getElementById("termOverrideConcept").value;
        if (!projectId || !conceptId) { setProjectError("Seleccione projecto e conceito."); return; }
        knowledgeRequest("/api/projects/" + projectId + "/terminology-overrides", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            concept_id: conceptId,
            legacy_term: document.getElementById("termLegacy").value.trim() || null,
            usage_note: document.getElementById("termUsageNote").value.trim() || null,
          }),
        }, "Falha ao criar override.")
          .then(function () {
            document.getElementById("termLegacy").value = "";
            document.getElementById("termUsageNote").value = "";
            return loadProjectTerminologyOverrides(projectId);
          })
          .catch(function (err) { setProjectError(err.message); });
      });
      document.getElementById("expBaselinePublish").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        if (!projectId) {
          setProjectError("Seleccione um projecto.");
          return;
        }
        setExportStatus("");
        knowledgeRequest(
          "/api/projects/" + projectId + "/baselines/publish",
          { method: "POST" },
          "Falha ao publicar baseline."
        )
          .then(function () { return loadExportSection(projectId); })
          .catch(function (err) { setExportStatus(err.message); });
      });
      document.getElementById("expLlmContextSave")?.addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        if (!projectId) {
          setProjectError("Seleccione um projecto.");
          return;
        }
        const statusEl = document.getElementById("expLlmContextStatus");
        const payload = {
          context: {
            code: document.getElementById("expLlmCode")?.value?.trim() || null,
            owner: document.getElementById("expLlmOwner")?.value?.trim() || null,
            document_type: document.getElementById("expLlmDocType")?.value?.trim() || null,
            location: {
              site: document.getElementById("expLlmSite")?.value?.trim() || null,
            },
            fascicle_overrides: {},
          },
        };
        knowledgeRequest(
          "/api/projects/" + projectId + "/llm-context",
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          },
          "Falha ao guardar contexto LLM."
        )
          .then(function () {
            if (statusEl) {
              statusEl.hidden = false;
              statusEl.textContent = "Contexto LLM guardado.";
            }
          })
          .catch(function (err) {
            if (statusEl) {
              statusEl.hidden = false;
              statusEl.textContent = err.message;
            }
          });
      });
      document.getElementById("expMaster").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        if (!projectId) {
          setProjectError("Seleccione um projecto.");
          return;
        }
        setExportStatus("");
        knowledgeRequest(
          "/api/projects/" + projectId + "/exports/master",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              profile: document.getElementById("expProfile").value,
              write_zip: document.getElementById("expWriteZip").checked,
            }),
          },
          "Falha ao exportar mestre."
        )
          .then(function (row) {
            setExportStatus("Mestre gravado: " + row.file_path);
            return loadExportSection(projectId);
          })
          .catch(function (err) { setExportStatus(err.message); });
      });
      document.getElementById("impUpload").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const fileInput = document.getElementById("impFile");
        if (!projectId || !fileInput.files.length) {
          setImportStatus("Seleccione projecto e ficheiro JSON.");
          return;
        }
        const file = fileInput.files[0];
        const form = new FormData();
        form.append("file", file, file.name);
        setImportStatus("");
        fetch("/api/projects/" + projectId + "/imports", { method: "POST", body: form })
          .then(function (res) {
            return res.json().then(function (payload) {
              if (!res.ok) throw new Error(apiErrorMessage(payload, "Falha no upload."));
              return payload;
            });
          })
          .then(function (payload) {
            lastUploadedImportId = payload.id;
            lastUploadedImportIsPackage = false;
            return loadImportSection(projectId);
          })
          .then(function () { setImportStatus("Importação gravada."); })
          .catch(function (err) { setImportStatus(err.message); });
      });
      document.getElementById("impPkgUpload").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const fileInput = document.getElementById("impPkgFile");
        if (!projectId || !fileInput.files.length) {
          setImportStatus("Seleccione projecto e pacote JSON.");
          return;
        }
        const file = fileInput.files[0];
        const form = new FormData();
        form.append("file", file, file.name);
        setImportStatus("");
        fetch("/api/projects/" + projectId + "/packages/import", { method: "POST", body: form })
          .then(function (res) {
            return res.json().then(function (payload) {
              if (!res.ok) throw new Error(apiErrorMessage(payload, "Ficheiro incompatível."));
              return payload;
            });
          })
          .then(function (payload) {
            return loadImportSection(projectId).then(function () {
              lastUploadedImportId = payload.import_id;
              lastUploadedImportIsPackage = true;
            });
          })
          .then(function () { setImportStatus("Pacote aceite. Use Rever alterações."); })
          .catch(function (err) { setImportStatus(err.message); });
      });
      document.getElementById("impPkgMerge").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const importId = lastUploadedImportId;
        if (!projectId || !importId || !lastUploadedImportIsPackage) {
          setImportStatus("Importe um pacote GET-PACKAGE primeiro.");
          return;
        }
        setImportStatus("");
        knowledgeRequest(
          "/api/projects/" + projectId + "/packages/imports/" + importId + "/merge",
          { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" },
          "Falha ao analisar pacote."
        )
          .then(function (merge) {
            renderProposals(projectId, merge);
            setImportStatus("Alterações: " + merge.proposals.length + " proposta(s).");
          })
          .catch(function (err) { setImportStatus(err.message); });
      });
      document.getElementById("impMerge").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const fascicleId = document.getElementById("impFascicle").value;
        const list = document.getElementById("impList");
        const newest = list.querySelector("p");
        const importId =
          lastUploadedImportId ||
          (newest && newest.dataset.importId);
        if (!projectId || !fascicleId || !importId) {
          setImportStatus("Seleccione fascículo e carregue uma importação.");
          return;
        }
        setImportStatus("");
        knowledgeRequest(
          "/api/projects/" + projectId + "/imports/" + importId + "/merge",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ fascicle_node_id: fascicleId }),
          },
          "Falha no merge."
        )
          .then(function (merge) {
            renderProposals(projectId, merge);
            setImportStatus("Merge concluído: " + merge.proposals.length + " proposta(s).");
          })
          .catch(function (err) { setImportStatus(err.message); });
      });
      document.getElementById("impConsolidate").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        if (!projectId || !activeMergeSessionId) {
          setImportStatus("Execute merge antes de consolidar.");
          return;
        }
        const consolidateUrl = lastUploadedImportIsPackage
          ? "/api/projects/" + projectId + "/packages/merge/" + activeMergeSessionId + "/consolidate"
          : "/api/projects/" + projectId + "/imports/merge/" + activeMergeSessionId + "/consolidate";
        knowledgeRequest(consolidateUrl, { method: "POST" }, "Falha ao consolidar.")
          .then(function (row) {
            setImportStatus("Consolidado. Backup: " + row.backup_id);
            return loadImportSection(projectId);
          })
          .catch(function (err) { setImportStatus(err.message); });
      });
      document.addEventListener("get:package-imported", function (ev) {
        const detail = ev.detail || {};
        const importId = detail.import_id;
        if (!importId) return;
        lastUploadedImportId = importId;
        lastUploadedImportIsPackage = true;
        const projectId = detail.project_id || document.getElementById("pActive").value;
        if (!projectId) return;
        loadImportSection(projectId)
          .then(function () {
            if (appRouter) appRouter.navigate("import");
            setImportStatus("Pacote importado.");
            if (detail.auto_review) {
              setImportStatus("A analisar alterações do pacote…");
              const mergeBtn = document.getElementById("impPkgMerge");
              if (mergeBtn) mergeBtn.click();
            } else {
              setImportStatus("Pacote importado. Prima «Rever alterações».");
            }
          })
          .catch(function (err) {
            setImportStatus(err.message);
          });
      });

      function runFasciclePackageExport() {
        const projectId = document.getElementById("pActive").value;
        const pkgSel = document.getElementById("expFasciclePkg");
        const fascicleId = (pkgSel && pkgSel.value) || document.getElementById("expFascicle").value;
        if (!projectId || !fascicleId) {
          return Promise.reject(new Error("Seleccione projecto e fascículo."));
        }
        const notesEl = document.getElementById("expPkgBriefNotes");
        const rawNotes = notesEl && notesEl.value ? notesEl.value.trim() : "";
        return knowledgeRequest(
          "/api/projects/" + projectId + "/packages/export",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              scope_kind: "fascicle",
              node_id: fascicleId,
              profile: document.getElementById("expProfile").value,
              llm_notes: rawNotes || null,
            }),
          },
          "Falha ao exportar pacote."
        ).then(function (row) {
          lastFasciclePackageExport = {
            brief: row.brief || "",
            body: row.body,
            export_id: row.export_id,
          };
          const copyBtn = document.getElementById("expPkgCopyBrief");
          if (copyBtn) copyBtn.disabled = !lastFasciclePackageExport.brief;
          downloadTextFile(row.filename || "GET-pacote.json", row.body || "");
          setExportStatus("Pacote gravado: " + row.file_path);
          return loadExportSection(projectId).then(function () {
            return lastFasciclePackageExport;
          });
        });
      }

      document.getElementById("expPackageBtn").addEventListener("click", function () {
        setExportStatus("");
        runFasciclePackageExport().catch(function (err) {
          setExportStatus(err.message);
        });
      });

      document.getElementById("expPkgCopyBrief").addEventListener("click", function () {
        if (lastFasciclePackageExport && lastFasciclePackageExport.brief) {
          copyPackageBrief(lastFasciclePackageExport.brief).catch(function (err) {
            setExportStatus(err.message);
          });
          return;
        }
        runFasciclePackageExport()
          .then(function (exp) {
            return copyPackageBrief(exp.brief);
          })
          .catch(function (err) {
            setExportStatus(err.message);
          });
      });
      document.getElementById("expFascicleBtn").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        const fascicleId = document.getElementById("expFascicle").value;
        if (!projectId || !fascicleId) {
          setExportStatus("Seleccione projecto e fascículo raiz.");
          return;
        }
        setExportStatus("");
        knowledgeRequest(
          "/api/projects/" + projectId + "/exports/fascicle/" + fascicleId,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              profile: document.getElementById("expProfile").value,
              write_zip: document.getElementById("expWriteZip").checked,
            }),
          },
          "Falha ao exportar fascículo."
        )
          .then(function (row) {
            setExportStatus("Fascículo gravado: " + row.file_path);
            return loadExportSection(projectId);
          })
          .catch(function (err) { setExportStatus(err.message); });
      });
      document.getElementById("expLlmGeneration").addEventListener("click", function () {
        const projectId = document.getElementById("pActive").value;
        if (!projectId) {
          setProjectError("Seleccione um projecto.");
          return;
        }
        const fascicleEl = document.getElementById("expLlmFascicle");
        const fascicleId = fascicleEl && fascicleEl.value ? fascicleEl.value : null;
        setExportStatus("");
        knowledgeRequest(
          "/api/projects/" + projectId + "/exports/llm-generation",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              profile: document.getElementById("expProfile").value,
              include_draft: document.getElementById("expLlmIncludeDraft").checked,
              fascicle_node_id: fascicleId,
            }),
          },
          "Falha ao exportar pacote GET-LLM."
        )
          .then(function (row) {
            const blocks = (row.manifest && row.manifest.files)
              ? row.manifest.files.filter(function (f) { return f.kind === "block"; }).length
              : "?";
            setExportStatus(
              "Pacote GET-LLM: " + row.zip_path + " · mestre " + row.file_path + " · " + blocks + " bloco(s)."
            );
            return loadExportSection(projectId);
          })
          .catch(function (err) { setExportStatus(err.message); });
      });
      document.getElementById("kSearch").addEventListener("click", function () {
        const q = document.getElementById("kQuery").value.trim();
        knowledgeRequest("/api/knowledge/search?q=" + encodeURIComponent(q) + "&scope_type=library", {}, "Falha na pesquisa.")
          .then(function (items) { renderItems(document.getElementById("kResults"), items); })
          .catch(function (err) { setKnowledgeError(err.message); });
      });

      refresh().catch(function (err) {
        loadingEl.hidden = true;
        setError(err.message);
      });
}
