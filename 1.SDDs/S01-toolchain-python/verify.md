# S01 — Projeto e toolchain Python · Verificação

## Critérios de aceite (Definition of Done deste item)

- [ ] Estrutura `src/{api,agent,rag,mcp,providers,data}` existe e está
      alinhada ao `architecture.md` de S00.
- [ ] `pyproject.toml` (ou equivalente) versionado, com lockfile de
      dependências commitado.
- [ ] Rodar o lint localmente (`ruff check .`) retorna sem erros no esqueleto
      inicial do projeto.
- [ ] Rodar o type check localmente (`mypy src/`) retorna sem erros no
      esqueleto inicial.
- [ ] `pre-commit run --all-files` passa sem falhas.
- [ ] `pytest --cov` executa com sucesso, com pelo menos 1 teste passando e um
      relatório de cobertura sendo gerado.
- [ ] `docker build .` completa com sucesso a partir do `Dockerfile` base.
- [ ] O workflow de CI roda automaticamente em um push/PR de teste e todos os
      steps (lint, type check, testes) terminam em verde.
- [ ] `README.md` documenta o passo a passo de setup local e uma pessoa nova
      no projeto consegue reproduzir o ambiente só seguindo essas instruções.

## Como verificar

1. Clonar o repositório em uma pasta limpa e seguir apenas o `README.md` para
   montar o ambiente — sem conhecimento prévio do projeto.
2. Rodar, nesta ordem: `ruff check .`, `mypy src/`, `pytest --cov`,
   `docker build .`.
3. Abrir um PR de teste (ex.: alterar um comentário) e confirmar que o CI
   dispara e conclui com sucesso.
4. Marcar este item como concluído no checklist do PDI (seção 14) somente após
   os 3 passos acima serem confirmados.
