# FraudGuard AI — Security Threat Model

## Scope
Local educational MVP using synthetic financial transactions.

## Assets to protect
- API keys and database credentials
- Transaction integrity
- Model artifacts and versions
- Alert investigation reports
- Human review and audit records

## Main threats and mitigations

| Threat | Mitigation |
|---|---|
| Secrets committed to Git | .gitignore, secret scanning |
| Unauthorized database modification | Read-only agent DB role |
| Malformed Kafka messages | JSON Schema validation and DLQ |
| Duplicate alerts | Deterministic IDs and unique constraints |
| LLM prompt injection | Restricted tools, cited evidence, human approval |
| Sensitive information in logs | Structured logs without credentials or raw PII |
| Unauthorized analyst decisions | Authentication and audit trail |

## Data handling
Only synthetic or explicitly authorized public data is permitted.
No real card numbers, client identifiers, passwords, or banking records.

## Trust boundaries
1. Transaction producer to Kafka
2. Kafka to Spark and storage
3. Scoring API to alert persistence
4. LangGraph tools to PostgreSQL and RAG sources
5. Analyst interface to decision API

## Limitations
Local development configuration is not production-grade security.
Authentication, network isolation, access control, and secret management
must be strengthened before any non-local deployment.