# Sincronizar o GET com GitHub (`mastercorisco/GET`)

O código canónico do agente está no **Origin**; o repositório GitHub foi criado vazio. O push automático para `github.com` na VM do agente **não** usa o mesmo token que o Origin.

## Opção A — Push manual no Windows (recomendado, uma vez)

1. Instale o código sem Origin (`releases/GET-src.zip` ou agente Cursor). Ver `WINDOWS_SETUP.md`.
2. No PowerShell, na pasta do projeto:

```powershell
gh auth login
git init
git branch -M main
git add -A
git commit -m "sync: código GET desde agente Cursor"
git remote add origin https://github.com/mastercorisco/GET.git
git push -u origin main
```

3. A partir da­: `git pull` / `git push` normal no GitHub.

## Opção B — PAT (sem `gh`)

1. GitHub → **Settings** → **Developer settings** → **Fine-grained personal access tokens**.
2. Repositório: **mastercorisco/GET**.
3. Permissões: **Contents** (read and write), **Metadata** (read).
4. **Não envie o token no chat.** Use-o só no Git Credential Manager quando o `git push` pedir password (o utilizador é o seu login GitHub; a password é o token).

```powershell
git push -u origin main
```

## Opção C — Integração Cursor + agente (para pushes futuros)

1. [cursor.com/dashboard](https://cursor.com/dashboard) → **Integrations** → **GitHub** → confirmar accesso à conta **mastercorisco** e ao repo **GET** (write).
2. Volte a este agente e epea: *“faz push para o GitHub”*.

Se ainda falhar na VM, use a Opção A uma vez; depois o GitHub passa a ser a cópia de trabalho.

## Opção D — Espelho Origin → GitHub (avancado)

Repositório do agente: `jo-o-pedro-cabral/tmp-d400637815729183` (status `no-mirror` no Origin). Ligar espelho **outbound** para GitHub é feito na UI Origin / documentação Cursor, não por `git clone` do Origin no CMD.

## O que evitar

- `git clone https://origin.cursor.com/...` fora do Cursor (pede token Origin).
- Colar tokens no chat do agente.