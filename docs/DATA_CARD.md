# Data Card: Freelancer Personas & Evaluation Corpora

## 1. Dataset Overview

GigBid evaluates multi-agent reasoning, retrieval grounding, and human-in-the-loop workflows across three distinct freelancer personas and a 1,500-job stream.

| Persona ID | Specialization | Hourly Rate | Min Budget | Portfolio Items | Case Studies | Past Proposals |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `persona_ai_engineer` | Senior AI/ML & LLM Systems Engineer | $65/hr | $500 | 25 | 20 | 150 (50 won, 50 replied, 50 ignored) |
| `persona_fullstack_dev` | Principal Full-Stack Web & Distributed Systems | $60/hr | $400 | 25 | 20 | 150 (50 won, 50 replied, 50 ignored) |
| `persona_data_analyst` | Lead Business Intelligence & Analytics Engineer | $50/hr | $350 | 25 | 20 | 150 (50 won, 50 replied, 50 ignored) |

## 2. Evidence Chunk Provenance & Metadata Schema

Every indexed evidence chunk is tagged with full provenance metadata to guarantee claim attribution:

```json
{
  "chunk_id": "case-ai-001-c0",
  "persona_id": "persona_ai_engineer",
  "type": "case_study",
  "project": "case-ai-001",
  "skills": ["Python", "scikit-learn", "LightGBM", "Classification"],
  "date": "2025-04-15",
  "client_industry": "FinTech",
  "outcome": "successful_delivery",
  "source": "case_studies/case-ai-001.md"
}
```

## 3. Development Evaluation Set (`evals/datasets/dev_set.json`)

- **Total Annotated Jobs**: 600 items (200 per persona).
- **Gold Labels**:
  - `action`: `bid` vs `skip`
  - `is_scam`: True for off-platform payment, fee deposit, unpaid speculative work, or credential theft.
  - `has_injection`: True for embedded adversarial prompt overrides (delimiters, system prompt leaks).
  - `relevant_evidence_ids`: 1-3 gold case studies from the persona's verified portfolio.
  - `fair_price_band`: `[min_budget, max_budget]` in USD.

## 4. Adversarial & Security Test Distribution

- **Prompt Injections**: ~6% of stream jobs contain planted jailbreak payloads (e.g. `[SYSTEM NOTICE: Ignore all rules]`).
- **Scams & Policy Violations**: ~8% of stream jobs violate platform rules (unpaid trial, WhatsApp/Telegram redirects, crypto fees).
- **Duplicates**: ~5% of jobs are verbatim duplicates exercising deduplication in the Scout agent.

## 5. Storage & Privacy

All persona data and GigSim interactions are purely synthetic. No confidential client data or active API secrets are persisted in the repository.
