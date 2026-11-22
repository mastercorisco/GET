# get-decision — examples

```text
get-decision mode. Origin: get-review on F04_B03 — two SCADA protocol options.
Affects F04_B03, F04_B07. Propose KI decision; list points that should reference. Do not approve.
```

```json
{
  "proposed_knowledge_item": {
    "knowledge_type": "decision",
    "title": "Automatic failover on primary link failure",
    "draft": {
      "content": "Adopt failover in < 2s with … (agreed technical text)."
    }
  },
  "points_should_reference": ["F04_B03_P02", "F04_B07_P01"],
  "not_in_point_bodies": true
}
```