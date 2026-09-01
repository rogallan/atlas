# S00 — Constitution + arquitetura · Verificação

## Critérios de aceite (Definition of Done deste item)

- [ ] `constitution.md` existe na raiz do repositório e contém, no mínimo, os
      6 princípios definidos no spec.md (local-first, segurança por padrão,
      ferramentas explícitas, evidência antes de afirmação, testes antes de
      release, dados fictícios sempre).
- [ ] Cada princípio em `constitution.md` tem pelo menos um exemplo concreto de
      aplicação no contexto do ATLAS (não é só um enunciado abstrato).
- [ ] `architecture.md` existe na raiz do repositório e documenta as 6 fronteiras
      (Front, API, Agent, MCP, Knowledge/RAG, Infra) com responsabilidade e
      contrato de cada uma.
- [ ] `architecture.md` contém o diagrama textual do fluxo principal
      (Usuário → Front → API → Agent Router → RAG/MCP → Validation → Resposta).
- [ ] Ambos os documentos foram revisados com o(a) mentor(a) do PDI (registrar
      data/observações no próprio commit ou em `docs/adr/`).
- [ ] `README.md` do repositório referencia (linka) `constitution.md` e
      `architecture.md`.
- [ ] Nenhuma pendência de S01 foi iniciada antes deste item estar concluído
      (S00 é bloqueante para o restante do catálogo, conforme a ordem T1 do PDI).

## Como verificar

1. Abrir `constitution.md` e `architecture.md` na raiz do repositório e conferir
   que ambos existem e não estão vazios/placeholder.
2. Conferir que os 6 princípios estão presentes e cada um tem exemplo aplicado.
3. Conferir que o diagrama de fluxo em `architecture.md` cobre todas as 6
   fronteiras citadas no PDI.
4. Confirmar com o(a) mentor(a) que a revisão foi feita.
5. Marcar este item como concluído no checklist do PDI (seção 14) somente após
   os 4 passos acima.
