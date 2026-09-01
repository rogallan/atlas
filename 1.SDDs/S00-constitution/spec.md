# S00 — Constitution + arquitetura

Trimestre: T1 · Categoria: Base do projeto
Entregável: `constitution.md` + `architecture.md`

## 1. Objetivo

Estabelecer, antes de qualquer linha de código de produto, os princípios inegociáveis
e as fronteiras arquiteturais que vão governar todas as decisões técnicas do ATLAS
ao longo dos quatro trimestres. Este item é a fundação de todo o padrão SDD: nenhum
outro item do catálogo (S01 → S22) deve entrar em conflito com o que for definido aqui.

## 2. Contexto

O ATLAS é um copiloto conversacional para gerente bancário que:
- consulta conhecimento público do Banco Central via RAG;
- consulta uma base fictícia de clientes/histórico financeiro via MCP;
- executa operações simples **simuladas** (nunca reais) por ferramentas controladas.

Por lidar com um domínio sensível (bancário) mesmo que com dados sintéticos, e por
usar LLMs com tool calling, o projeto precisa de princípios explícitos de segurança,
verificação e qualidade desde o primeiro commit.

## 3. Escopo

Este item cobre exclusivamente a criação de dois documentos fundacionais:

1. **`constitution.md`** — princípios do projeto, não-negociáveis, que qualquer
   spec/plan/tasks futuro deve respeitar.
2. **`architecture.md`** — mapa das fronteiras entre os módulos do sistema
   (Front / API / Agent / MCP / RAG / Infra), com as responsabilidades e os
   contratos de comunicação entre eles.

## 4. Fora de escopo

- Implementação de qualquer código de produto (isso começa em S01+).
- Decisões de baixo nível de bibliotecas/frameworks específicos (ficam nos ADRs
  de cada item, ex: S06 decide Vector DB, S04 decide integração Ollama).
- Definição de operações de negócio detalhadas (fica em S02 e na seção "Mapa de
  Operações" do PDI).

## 5. Princípios candidatos (a redigir em constitution.md)

- **Local-first**: o desenvolvimento roda inteiramente local (Ollama, containers,
  Vector DB/Store, MCP); cloud é caminho alternativo, não dependência de dia a dia.
- **Segurança por padrão**: nenhuma ação sensível é executada sem validação e,
  quando aplicável, confirmação humana (human-in-the-loop).
- **Ferramentas explícitas**: o agente nunca improvisa uma capacidade; toda ação
  passa por uma tool/MCP tipada e auditável.
- **Evidência antes de afirmação**: respostas baseadas em conhecimento (RAG) só
  são dadas com citação rastreável; na ausência de evidência, o agente admite
  não saber em vez de inventar.
- **Testes antes de release**: nenhuma feature é considerada "pronta" (Definition
  of Done) sem testes automatizados e, quando aplicável, evals passando.
- **Dados fictícios, sempre**: nenhum dado real de cliente é usado em nenhuma
  camada do projeto, inclusive em documentação e vídeos publicados.

## 6. Critérios de aceite

- [ ] `constitution.md` versionado na raiz do repositório, com princípios acima
      redigidos e validados.
- [ ] `architecture.md` documentando as fronteiras Front/API/Agent/MCP/RAG/Infra,
      incluindo diagrama textual e contrato de responsabilidade de cada módulo.
- [ ] Ambos os documentos revisados com o(a) mentor(a) do PDI.
- [ ] Nenhuma decisão de S01+ pode contradizer o que está definido aqui sem
      abrir um ADR explicando a exceção.
