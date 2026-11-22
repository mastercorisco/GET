# get-lexicon — examples

## Search before propose

```text
get-lexicon. project_id=<uuid>.
Read terminology_discussion_llm.json in ZIP EXP-LLM-….
GET /api/terminology/search?q=adjudicatário&project_id=<uuid> → 1 hit.
RCD norm uses «contratante de obras» — propose alignment?
```

## Candidate output (excerpt)

```json
{
  "skill": "get-lexicon",
  "project_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "candidates": [
    {
      "action": "create",
      "scope_type": "library",
      "preferred_term": "Entidade adjudicante",
      "definition": "Pessoa colectiva pública ou privada que celebra o contrato de empreitada.",
      "synonyms": ["adjudicante"],
      "avoid_terms": ["contratante de obras"],
      "notes": "Corpus: RCD clause 2 — validate with engineer"
    }
  ],
  "conflicts": []
}
```

The engineer registers in the UI or requests explicit API calls in another session.