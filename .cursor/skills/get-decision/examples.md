# get-decision — exemplos

```text
Modo get-decision. Origem: get-review no F04_B03 — duas opções de protocolo SCADA.
Afecta F04_B03, F04_B07. Propor KI decision; listar pontos que devem referenciar. Não aprovar.
```

```json
{
  "proposed_knowledge_item": {
    "knowledge_type": "decision",
    "title": "Protocolo de troca automática perante falha do link principal",
    "draft": {
      "content": "Adopta-se failover em < 2s com … (texto técnico acordado)."
    }
  },
  "points_should_reference": ["F04_B03_P02", "F04_B07_P01"],
  "not_in_point_bodies": true
}
```