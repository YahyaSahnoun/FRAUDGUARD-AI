# S11 — Naming conventions

| Item | Convention | Example |
|---|---|---|
| Kafka topics | lower dot-separated | `transactions.raw`, `fraud.alerts` |
| Python packages | snake_case | `alert_worker` |
| Files / JSON fields | snake_case | `transaction_id`, `risk_score` |
| HTTP paths | `/v1/` + plural lowercase | `/v1/alerts` |
| Environment variables | UPPER_SNAKE_CASE | `KAFKA_BOOTSTRAP_SERVERS` |
| SQL tables / columns | snake_case plural table | `audit_events`, `model_version` |
| Object storage | lowercase buckets; path stage partition | `s3a://fraudguard/bronze/transactions/` (candidate; configure in S18) |
| Date/time | RFC 3339 UTC preferably `Z` | `2026-11-07T10:15:00Z` |
| Story tags | `sprint-01` to `sprint-08` | `sprint-01` |
| Event contract version | `schema_version: "1.0"` | `1.0` |
| Code / commit | English imperative | `docs: define data contracts` |

Naming of object-store buckets and checkpoint paths is a **proposal**, not existing infrastructure. Use the scoring name `risk_score` unless verified calibration justifies probability semantics; avoid `fraud_score` ambiguity. Do not use `fraude_suspecte` as a topic when actual target is `fraud.alerts`.
