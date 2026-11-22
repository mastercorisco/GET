# Checklist F0 — pré-import (get-orient / sessão estrutural)

Usar **antes** de `POST .../packages/import`. Complemento: [docs/plans/micro-F0-import-ritual.md](../../docs/plans/micro-F0-import-ritual.md).

## Modo declarado

- [ ] **F0-structure** | **F0-content-block** | **F0-knowledge** — um só por ficheiro
- [ ] Prompt LLM inclui cabeçalho e modo do ritual
- [ ] Diff esperado alinhado ao modo (não pedir “reorganização total”)

## Integridade do pacote

- [ ] `rules_hash` inalterado face ao export original
- [ ] `scope.project_id` correcto; `fascicle_id` ou `block_id` corresponde ao export
- [ ] `export_id` no JSON = export usado na sessão (re-export se dúvida)
- [ ] Novos IDs só `new_001`, `new_002`, …

## Conteúdo conceptual

- [ ] Sem decisões / lacunas globais em `core_idea` de pontos (modo structure/knowledge)
- [ ] Listas de pontos: objectos tipados, sem strings nuas
- [ ] Sem mistura: estrutura no fascículo **ou** pontos no bloco **ou** KI no fascículo

## Segurança operacional

- [ ] Backup crítico após último consolidate bom
- [ ] `backend/scripts/f0_pilot_preflight.py --fascicle F01 --export` (se export antigo ou em dúvida)
- [ ] `validate_get_package_file.py` sem erro estrito
- [ ] Avisos heurísticos do script lidos
- [ ] Número de alterações plausível para “humo” (alerta se >30 propostas estruturais de teste)

## Depois do upload (app)

- [ ] Ler `conceptual_warnings` na UI ou resposta API
- [ ] Revisar propostas por **grupo** (estrutura → pontos → premissas → knowledge)
- [ ] Não “aceitar tudo” se houver conflitos ou `protected_touch`