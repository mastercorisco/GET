# F0 — Inventário F01_B07 (workspace externo)

O incidente F01_B07 ocorreu **noutro workspace** que o `GET_aux/testes`. Use este checklist ao repetir o diagnóstico.

## 1. Localizar artefactos

| Item | Onde procurar |
|------|----------------|
| JSON devolvido pela LLM | pasta do utilizador + `imports/<uuid>/` |
| `merge_base.json` | mesma pasta do import |
| Export canónico | `exports/PKG-BLK-F01_B07/` ou export novo na UI |
| Registo | tabela `import_record` / UI Reimportar |

## 2. Validar offline

```powershell
cd C:\PROGRAMACAO\GET\backend
python scripts/validate_get_package_file.py "<caminho.json>" --project-id <uuid-projecto>
```

Interpretar:

- **ERRO** `bloco não existe` / `display_code` → export **obsoleto** após reestruturação; re-export na app.
- **AVISO** modo misto / `editable_knowledge` em pacote bloco → violação ritual F0.

## 3. Comparar árvore

- `display_code` no JSON vs árvore UI (F01_Bxx).
- `structure_anchor` (pacotes 1.0.1+): fascículo e posição.
- Não usar `PKG-FASC-F01` em disco sem confirmar `export_record` / hash actual.

## 4. Recuperação F01_B07 (Matriz / bloco deslocado)

| Sintoma | Acção |
|---------|--------|
| JSON com `display_code` `F01_B07` mas árvore só até `F01_B06` | Tratar pacote como **export obsoleto**; não forçar merge. |
| Conteúdo útil na discussão LLM | Copiar texto para notas; **criar** o bloco na app (título «Matriz…» ou equivalente) **ou** atribuir a um `F01_Bxx` existente com acordo humano. |
| `block_id` desconhecido | Nunca reutilizar UUID de ficheiro antigo; após criar/alinhar bloco, **novo** export `PKG-BLK-<display_code>`. |
| Fascículo desactualizado | Não usar `PKG-FASC-F01` em disco como verdade; re-export fascículo e confiar em `structure_anchor` (schema 1.0.1+). |

Fluxo recomendado:

1. Backup crítico na app.
2. Decidir destino do conteúdo (novo bloco vs bloco existente).
3. Re-export bloco (e fascículo se piloto estrutura).
4. Sessão LLM só sobre o pacote fresco; validar offline com `validate_get_package_file.py`.
5. Import; rever `conceptual_warnings` na resposta da API.
6. Consolidar; re-export.

## 5. Decisão de conteúdo (resumo)

Se «Matriz de fornecimentos…» não tiver bloco na árvore:

1. Criar bloco na app **ou** mapear para `F01_Bxx` existente.
2. Export bloco → LLM → import (nunca UUID antigo de migração CTBJ v3).

## 6. Registo

Preencher secções relevantes em [`micro-F0-retro-TEMPLATE.md`](micro-F0-retro-TEMPLATE.md).