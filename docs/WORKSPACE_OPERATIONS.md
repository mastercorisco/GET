# Operação do workspace (robustez SQLite)

Guia curto para **uma instância** do GET por ficheiro `get.db`. Sem multiutilizador nem contentor no MVP.

## Variáveis

| Variável | Uso |
|----------|-----|
| `GET_WORKSPACE_ROOT` | Raiz de dados; sobrepõe `workspace_root` em `~/.get/app-config.json`. Útil para scripts e automação. |
| `GET_HOST` / `GET_PORT` | Arranque uvicorn (default `127.0.0.1:4810`). |

## Diagnóstico

- `GET /api/health` — versão e capacidades (sem abrir workspace).
- `GET /api/health/workspace` — requer workspace aberto; devolve `integrity` (`PRAGMA integrity_check`), `journal_mode` (esperado `wal`) e caminhos.

## SQLite

- Modo **WAL** e `busy_timeout` configurados na ligação SQLAlchemy.
- Escritas críticas usam **`BEGIN IMMEDIATE`** via `workspace_session(..., begin_immediate=True)`.
- **Uma instância uvicorn** (ou um script) por workspace; não partilhar `get.db` com outro processo (ex.: DB Browser em escrita).

## Operações exclusivas (HTTP 409 se outra estiver activa)

No **mesmo processo**, apenas uma destas operações de cada vez:

- Restauro de backup
- Publicar baseline
- Importar pacote (GET-PACKAGE ou fascículo) / correr merge
- Consolidar importação ou pacote
- Aplicar workbook
- Sync CTBJ (`--apply`)
- Purge de estrutura documental / apagar projecto

Mensagem típica: *Operação de workspace em curso (…). Aguarde e tente de novo.*

## Restauro de backup

1. Pré-visualização: `GET /api/backups/{id}/preview`.
2. Restauro: `POST /api/backups/{id}/restore?confirm=true`.
3. Antes de substituir `get.db`, é criado backup crítico `pre_restore_guard_*`.
4. Após restauro, o servidor **invalida cache** de motor SQLAlchemy e migração em memória; o próximo pedido reabre ligações ao ficheiro restaurado.

## Boas práticas

- Fazer backup **critical** antes de merge/consolidar (a aplicação já o faz em vários fluxos).
- Se aparecer *database is locked*, fechar outras ferramentas no mesmo `get.db` e reiniciar uvicorn.
- Para migrações de estrutura CTBJ ou purge, não correr scripts em paralelo com a UI.

## Roadmap

Embalagem em contentor (Docker) fica **fora do MVP** — ver épico `E09` em `BACKLOG.json`.