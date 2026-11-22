# get-research — exemplos

## Gatilho a partir do grill

```text
Modo get-research. Lacuna do grill (ponto X): «potência UPS mínima» — datasheet em corpus/vendor/ups-xx.pdf.
Propor Reference + internal_location; opcional fact que cite a ref. Não marcar verificado.
```

## Saída (trecho)

```json
{
  "proposed_reference": {
    "citation": "Fabricante X — UPS série Y, datasheet rev. 2024",
    "internal_location": "corpus/vendor/ups-xx.pdf",
    "notes": "Pág. 12 — potência nominal kVA"
  },
  "for_grill": "Fechar open_question «potência UPS» com must_include objecto tipado após validação humana."
}
```