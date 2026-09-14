# BMAD Methodology & Governance Rules

## 1. Visão Geral
Esta regra aplica os princípios do **BMAD (Breakthrough Method for Agile AI-Driven Development)** ao ciclo de desenvolvimento do ATLAS no Google Antigravity.

O objetivo é transformar o desenvolvimento assistido por IA em um processo rigoroso de engenharia de software com:
- **Papéis Especializados:** Divisão clara de responsabilidades (Product Manager, Architect, Developer, QA).
- **Contexto Durável:** Decisões documentadas em artefatos versionados (`1.SDDs/`, `docs/adr/`, `evals/`), nunca apenas no histórico volátil de chat.
- **Review Gates & Qualidade:** Nenhuma funcionalidade avança sem planos aprovados, testes e aderência à Definition of Done.
- **Human-in-the-Loop:** Decisões de alto impacto e ações com efeitos colaterais sempre exigem aprovação explícita.

## 2. Princípios de Execução BMAD
1. **Spec First (SDD):** Antes de codificar, valide os requisitos na pasta `1.SDDs/` (`spec.md` -> `plan.md` -> `tasks.md`).
2. **Separação de Preocupações:** 
   - *PM/Analyst:* Define o "quê", o valor de negócio e critérios de aceitação.
   - *Architect:* Define o "como", contratos de dados (Pydantic/OpenAPI) e trade-offs técnicos (ADRs).
   - *Developer:* Implementa código limpo, tipado e com testes unitários.
   - *QA/Evaluator:* Mede regressões, avalia scorecards e valida conformidade.
3. **Evidência Antes de Conclusão:** Uma tarefa só é dada como finalizada quando comprovada com saída de testes, validação de schema ou verificação prática.
4. **Idioma dos Artefatos Técnicos (Inglês Mandatório):** Independentemente da língua utilizada no chat ou na descrição das skills, todos os artefatos técnicos formais do repositório (`1.SDDs/` com `spec.md`, `plan.md`, `tasks.md`, `verify.md`, bem como código-fonte em `2.src/`, testes e documentação técnica) **devem ser gerados e mantidos estritamente em inglês**, preservando a convenção global e o padrão dos SDDs já existentes.

