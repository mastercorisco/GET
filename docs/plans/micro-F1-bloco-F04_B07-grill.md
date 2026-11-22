# F1 — Bloco F04_B07 (get-grill) — piloto activo

**Pré-requisito:** F0 fechado — [micro-F0-retro-F01.md](micro-F0-retro-F01.md).

## Porquê este bloco

F01_B01 já tem **4/4** pontos `ready` (M1 nominal no bloco piloto estrutural). **F04_B07** mistura `draft`, `ready`, `incomplete` e `approved` — melhor para exercitar **get-grill** e import `F0-content-block` sem repetir só estrutura.

| Campo | Valor |
|--------|--------|
| Projecto | `976e3991-e64e-4306-99fe-4ac1e2230b52` |
| Bloco | **F04_B07** — `node_id` `e80549f8-c24b-4ece-a156-1bb6452c3850` |
| Export | `PKG-BLK-F04_B07` → re-export com `--export` antes da sessão |
| Incidente Phase A | Canal histórico — usar ritual **um bloco / um ciclo** |

## Passos

1. **get-orient** (READ): [micro-F0-orient-snapshot-CTBJ.md](micro-F0-orient-snapshot-CTBJ.md) + summary API.
2. Pré-voo:
   ```powershell
   python backend/scripts/f1_block_preflight.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --block F04_B07 --export
   ```
3. Sessão **get-grill** sobre `F04_B07_package.json` (modo F0-content-block no ritual).
4. `validate_get_package_file.py` → import → aceitar **pontos/premissas** (não estrutura fascículo).
5. Consolidate → marcar **`ready`** na UI onde a validação passar (humano).

## Entrega M1

Harness credível no bloco escolhido: pontos alvo em `ready` sem alertas bloqueantes; pelo menos um ciclo grill+import documentado.

Skill: `agent-skills/get-grill/` — [micro-get-grill-skill.md](micro-get-grill-skill.md).

## F01_B01

Bloco estável pós-F0; export em `PKG-BLK-F01_B01`. Grill opcional (refino de conteúdo) — ver [micro-F1-bloco-F01_B01-grill.md](micro-F1-bloco-F01_B01-grill.md).