# ATLAS Banking GenAI Copilot — Technical Portfolio Showcase

Welcome to the technical portfolio showcase for **ATLAS (Agentic Tiered Lightweight Advisory System)**, an enterprise-grade banking conversational copilot designed for relationship managers in the Brazilian financial sector.

Developed across a comprehensive 4-quarter Individual Development Plan (PDI) for Senior GenAI Software Engineering, ATLAS demonstrates end-to-end mastery across distributed system design, local-first LLM orchestration, regulatory RAG retrieval, security guardrails, observability, and cloud infrastructure as code.

---

## 🌟 Key Technical Highlights

1. **Local-First & Zero-Cloud LLM Cost:**
   - Runs open-weights foundation models (`Qwen 2.5 7B Instruct` + `nomic-embed-text`) locally via **Ollama**.
   - Vector database persistence powered by embedded **ChromaDB**.
   - Zero private banking data sent to commercial third-party LLM providers.
2. **Deterministic Tool Integration via Model Context Protocol (MCP):**
   - 6 specialized micro-servers: Customer Profile/Transactions, Loan Amortization (Price & SAC), Insurance, Consortia, Tariff Catalog (BACEN Res. 3.919), and Support Tickets.
3. **Multi-Agent State Orchestration:**
   - Cyclical graph coordination implemented via **LangGraph (`StateGraph`)**.
   - Mandatory **Human-in-the-Loop (HITL)** governance with cryptographically signed tokens for sensitive operations (ticket creation, limit changes).
4. **Dual-Layer Defensive Security Guardrails:**
   - Input guardrails blocking prompt injection, system prompt extraction, and jailbreaks.
   - Output guardrails performing real-time masking of Brazilian Personally Identifiable Information (PII) including CPFs and bank accounts.
5. **Full Observability & Cost Transparency:**
   - Prometheus metrics exporter (`/metrics`), structured JSON logging (`structlog`), and real-time session token accounting with USD cost estimation.
6. **Dual Deployment Topology:**
   - **Local Hybrid:** Local Uvicorn backend connected to a Vercel-hosted Next.js frontend via an Ngrok static domain tunnel.
   - **Production AWS IaC:** Modular Terraform configuration deploying the stack to **AWS ECS Fargate**, ALB, and **OpenSearch Serverless**.

---

## 📁 Portfolio Assets Directory

* [Interactive Demo Script](file:///c:/Users/rogall/source/repos/atlas/8.docs/portfolio/demo_script.md) — Step-by-step 10-minute live demonstration script covering all 5 canonical use cases.
* [Video Series Curriculum](file:///c:/Users/rogall/source/repos/atlas/8.docs/portfolio/video_curriculum.md) — Detailed syllabus mapping the 20 technical episodes across YouTube and LinkedIn.
* [Architecture Decision Records (ADRs)](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/README.md) — Master index of all 12 architectural decisions (ADR-0001 through ADR-0012).
* [Final Benchmark Scorecard v1.0.0](file:///c:/Users/rogall/source/repos/atlas/7.evals/reports/final_scorecard_v1.0.0.md) — Regulatory evaluation harness report proving 96% intent accuracy and 100% safety compliance.
* [AWS Cost Estimate Model](file:///c:/Users/rogall/source/repos/atlas/docs/architecture/aws_cost_estimate.md) — Engineering cost breakdown comparing Dev ($222/mo) vs. Prod ($444/mo).
