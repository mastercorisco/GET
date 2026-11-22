# M3 — prompt sessão get-research / grill (referências partilhadas)

**Projecto:** CTBJ testes (`976e3991-e64e-4306-99fe-4ac1e2230b52`).

## Contexto

Skill **get-research** + **get-grill**. Ler `checklist-m3-references.md`.

Estado prévio (API ou CLI):

```powershell
# API (servidor activo)
curl -s http://127.0.0.1:8000/api/projects/976e3991-e64e-4306-99fe-4ac1e2230b52/reuse-report

# Offline
python backend/scripts/f3_reference_citation_report.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --json
```

## Pedido ao agente

1. Identificar norma ou documento citado em vários pontos do fascículo piloto sem `Reference` única na app.
2. PROPOSE uma `Reference` com `internal_location` sugerido + lista de pontos que devem partilhar o mesmo `reference_id`.
3. Não POST na API; engenheiro regista e actualiza pontos na UI ou GET-PACKAGE.

## Critério de sucesso

Relatório com `m3_reuse_ready: true` (≥2 pontos com o mesmo `reference_id`).