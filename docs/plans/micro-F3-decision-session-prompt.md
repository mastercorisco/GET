# F3 — prompt sessão get-decision (piloto)

**Projecto:** CTBJ testes (`976e3991-e64e-4306-99fe-4ac1e2230b52`).

## Contexto

Activar skill **get-decision**. Ler `checklist-f3.md`.

Relatório prévio:

```powershell
python backend/scripts/f3_decision_citation_report.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --json
```

## Pedido ao agente

1. Propor **uma** decisão de engenharia que hoje está repetida ou implícita em vários pontos do bloco piloto (ex. F04_B07 ou fascículo F04).
2. Entregar candidato KI `decision` (JSON) + lista de `point_id` / códigos que devem passar a `knowledge_item_ids`.
3. Não executar POST na API; preparar GET-PACKAGE ou instruções para a UI.

## Critério de sucesso

Após o engenheiro aplicar: relatório F3 com `f3_pilot_ready: true`.