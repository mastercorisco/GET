# Checklist de revisão do plano — GET (v2)

Utilizar antes de iniciar implementação de código. Marcar quando validado.

## Pacote e fontes

- [x] MANIFEST completo no repositório (`DATA_MODEL`, schemas, examples, ADRs, backlog, regras)
- [x] Ordem de precedência documentada no `PLAN.md`
- [x] Pacote sincronizado a partir do upload canónico (Nov 2026)

## Conflitos C-01 a C-06

- [x] **C-01** — `technical_instances.instance_id`: UUID na BD, código no export (tratamento aceite no plano)
- [x] **C-02** — Terminologia: UUID interno + código exportado
- [x] **C-03** — `origin_context` na BD; mapeamento export sem alterar schema v1.0.0
- [x] **C-04** — Reimport não aplica `approval`/`lifecycle` do JSON devolvido
- [x] **C-05** — Validação builder + golden files para `master` permissivo
- [x] **C-06** — `revision` e `id` protegidos no merge

## Arquitetura e ADRs

- [x] ADR-001: apenas `127.0.0.1`
- [x] ADR-018: FastAPI + SQLite + React
- [x] ADR-019: workspace separado, backups críticos/diários/semanais
- [x] Sem LLM, Docker, cloud, auth, multiutilizador no MVP

## Modelo de dados

- [x] Invariantes `DATA_MODEL.md` reflectidas no desenho físico do `PLAN.md`
- [x] Rascunho vs revisão append-only vs baseline imutável
- [x] JSON só em payloads de fichas, manifests e staging

## Intercâmbio

- [x] Omissão no JSON importado ≠ eliminação (`treat_omissions_as_deletions: false`)
- [x] Remoções via `proposed_removals` / `change_summary`
- [x] `protected_fields` alinhados ao exemplo `fascicle-roundtrip.example.json`
- [x] Apenas JSON reimportável; Markdown leitura

## Fases e testes

- [x] Fases E01–E08 coerentes com `BACKLOG.json`
- [x] Testes de contrato com exemplos listados (Fase 6)
- [x] Testes de falha E07 listados no plano

## Âmbito

- [x] Fora do MVP inalterado (spec §26)
- [x] Parâmetros técnicos texto livre (ADR-030)

## DoD

- [x] Definition of Done por épico mapeada às stories do backlog

## Aprovação

- [x] Plano v2 revisto e aceite para **Fase 1 (E01)** mediante implementação autorizada pelo utilizador
- [ ] Caminho do workbook GET (apenas E08 — não bloqueia E01)

**Data da revisão:** 2026-11-14