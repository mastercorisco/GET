# F0-structure — prompt de sessão LLM (F01)

Usar com `exports/PKG-FASC-F01/F01_package.json` após re-export. Alternativa **sem LLM** (dry-run): [micro-F0-structure-dryrun.md](micro-F0-structure-dryrun.md).

## Anexar ao chat

1. Ficheiro completo `F01_package.json` (GET-PACKAGE).
2. Texto abaixo (cabeçalho + modo).

## Prompt (copiar)

```text
Trabalhas sobre um GET-PACKAGE 1.0.0 já exportado.
- Devolves APENAS o JSON completo do envelope (sem prose).
- rules, rules_hash, schema, schema_version, scope, export_id: byte-a-byte iguais ao ficheiro recebido.
- Não omitas entidades existentes (omissão NÃO é eliminação).
- Novos IDs só new_001, new_002, …
- Listas de pontos: sempre objectos tipados, nunca strings soltas.

MODO: F0-structure
Só podes alterar estrutura documental do fascículo exportado (títulos/ordem de blocos em payload.fascicle.structure).
NÃO alteres development_points, premises, editable_knowledge, protected_context, payload fora de fascicle.structure.

Tarefa piloto: alterar o title de exactamente UM bloco (ex. F01_B01) com correção ortográfica mínima ou sufixo « (piloto F0)»; manter node_id, display_code e position iguais nos restantes nós.
```

## Após devolução

```powershell
cd C:\PROGRAMACAO\GET\backend
python scripts/validate_get_package_file.py "<json devolvido>" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
```

Import na app → grupo **Estrutura** → consolidate → re-export F01 → retro [micro-F0-retro-F01.md](micro-F0-retro-F01.md).