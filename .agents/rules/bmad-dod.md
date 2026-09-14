# BMAD Definition of Done (DoD) & Quality Gates

## 1. Quality Gates Obrigatórios
Nenhum item do catálogo ou incremento de código deve ser considerado concluído sem atender a todos os critérios abaixo:

1. **Gate 1: Alinhamento de Especificação (PM/Spec)**
   - O item possui `spec.md` claro com escopo, não-escopo, requisitos numerados e critérios de aceite.
   - Respeita os princípios de segurança, dados 100% sintéticos e evidências documentais.

2. **Gate 2: Revisão de Arquitetura & Contratos (Architect/Plan)**
   - O `plan.md` define a estrutura modular, interfaces, contratos de dados tipados (Pydantic/TypeScript) e tratamento de erros/resiliência.
   - Mudanças estruturais ou de stack possuem seu correspondente ADR registrado em `docs/adr/`.

3. **Gate 3: Implementação & Testes (Developer/Code)**
   - Código Python estritamente tipado (Type Annotations completas) e aderente aos linters/formatadores (`ruff`, `mypy`).
   - Testes unitários cobrindo o caminho feliz, limites de parâmetros e erros esperados.
   - Nenhuma credencial ou dado confidencial exposto no código ou logs.

4. **Gate 4: Verificação & Evidências (QA/Verify)**
   - O arquivo `verify.md` contém evidências reais de execução (logs de teste, saída de schemas, relatórios de eval).
   - Nenhuma caixa em `tasks.md` é marcada como concluída sem a respectiva evidência documentada em `verify.md`.
