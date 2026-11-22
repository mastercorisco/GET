# get-research — examples

## Trigger from grill

```text
get-research mode. Grill gap (point X): «minimum UPS power» — datasheet at corpus/vendor/ups-xx.pdf.
Propose Reference + internal_location; optional fact citing the ref. Do not mark verified.
```

## Output (excerpt)

```json
{
  "proposed_reference": {
    "citation": "Vendor X — UPS series Y, datasheet rev. 2024",
    "internal_location": "corpus/vendor/ups-xx.pdf",
    "notes": "Page 12 — nominal kVA"
  },
  "for_grill": "Close open_question «UPS power» with typed must_include after human validation."
}
```