# get-lexicon — exemplos

## Pesquisa antes de propor

```text
get-lexicon. project_id=<uuid>.
Li terminology_discussion_llm.json no ZIP EXP-LLM-….
GET /api/terminology/search?q=adjudicatário&project_id=<uuid> → 1 hit.
Norma RCD usa «contratante de obras» — propor alinhamento?
```

## Saída candidatos (trecho)

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
      "notes": "Corpus: RCD cláusula 2 — validar com engenheiro"
    }
  ],
  "conflicts": []
}
```

O utilizador regista na UI ou pede noutra sessão chamadas API explícitas.