# AWS Cloud Infrastructure Cost Model & Budget Estimate (S21)

> **Domain:** Cloud FinOps & Infrastructure Architecture · **Region:** `us-east-1` · **Workload:** Regional / Medium Bank Copilot

---

## 1. Executive Summary & Sizing Assumptions

This cost model projects the monthly operational expenditure (OpEx) for running the **ATLAS Banking Copilot** on Amazon Web Services (AWS) using the modular Terraform infrastructure provisioned in **S21**.

### Reference Workload Profile:
- **Active User Base:** 50–100 bank relationship managers (gerentes de relacionamento).
- **Daily Query Volume:** ~2,500 conversational turns/day (~75,000 requests/month).
- **RAG Regulatory Corpus:** 200+ Central Bank (BACEN/CMN) regulatory circulars (~50 MB text, ~50,000 vector embeddings).
- **Traffic Patterns:** Concentrated during banking business hours (08:00–19:00 BRT).

---

## 2. Monthly Cost Breakdown (Development vs. Production)

All pricing is calculated based on AWS public rates in `us-east-1` (US East, N. Virginia) as of 2026.

| Component / Service | Resource Specification | Dev / Staging Cost | Production (Multi-AZ) | Notes |
| :--- | :--- | :---: | :---: | :--- |
| **Compute: ECS Fargate** | 2 tasks × 1 vCPU, 2 GB RAM (24/7) | $72.50 | $145.00 | 4 tasks in production with auto-scaling |
| **Load Balancing: ALB** | 1 Application Load Balancer + 1 LCU | $22.50 | $35.00 | Handles HTTPS & health probes |
| **Network: NAT Gateway** | 1 NAT Gateway (dev) / 2 NAT (prod) | $32.40 | $64.80 | Plus $0.045/GB data processed |
| **Data: Vector Index** | Amazon OpenSearch Serverless (0.5 OCU) | $87.60 | $175.20 | Alternative: Qdrant on t4g.medium ($24/mo) |
| **Storage: Amazon S3** | Standard storage + API requests | $1.20 | $3.50 | Knowledge corpus & document versioning |
| **Secrets Manager** | 1 Secret + 10,000 API calls | $0.45 | $0.90 | Runtime token and DB credential retrieval |
| **CloudWatch Logs** | 10 GB ingestion + 30-day retention | $5.30 | $18.50 | Application stdout & audit compliance logs |
| **AWS X-Ray** | 50,000 traces recorded/month | $0.25 | $1.00 | End-to-end latency waterfall tracing |
| **Total Estimated Monthly Cost** | | **~$222.20 / mo** | **~$443.90 / mo** | |

---

## 3. Cost Comparison: Local Stack vs. AWS Cloud

```
Local Docker Stack (S20):  $0.00 / month (Local-first, running on developer workstation / on-premise)
AWS Dev Environment (S21): ~$222.20 / month (Single NAT, 2 Fargate replicas, OpenSearch Serverless)
AWS Prod Cluster (S21):    ~$443.90 / month (Multi-AZ NAT, 4 Fargate replicas, High-availability vector)
```

---

## 4. Key Cost Optimization Levers

1. **Fargate Compute Savings Plans:**
   Committing to a 1-year or 3-year Compute Savings Plan reduces ECS Fargate hourly costs by **up to 45%** ($72.50 $\rightarrow$ ~$40.00/month).
2. **Fargate Spot for Non-Production Workloads:**
   Utilizing `FARGATE_SPOT` capacity providers for development and automated testing yields a **70% discount** on compute pricing.
3. **Alternative Vector DB Topology for Dev/Test:**
   For development environments where OpenSearch Serverless fixed OCU pricing is cost-prohibitive, running containerized Qdrant or Chroma on an Amazon EC2 `t4g.small` (ARM Graviton) reduces monthly vector storage costs from $87.60 to **~$12.50/month**.
4. **S3 Intelligent-Tiering:**
   Regulatory documents rarely accessed after indexing are automatically transitioned to infrequent access tiers, optimizing long-term storage costs.
5. **Single NAT Gateway in Development:**
   Configured in `environments/dev.tfvars` via `single_nat_gateway = true`, avoiding the redundant $32.40/month cost of a secondary NAT Gateway in non-production.
