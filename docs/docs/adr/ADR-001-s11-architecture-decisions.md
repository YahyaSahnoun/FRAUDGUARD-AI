# ADR-001 — S11 architecture decisions (proposed for owner approval)

Date: 2026-11-07  
Status: **Proposed — requires owner approval**  
Scope: Sprint 1, Story S11. No runtime components are claimed as implemented.

## D1 — Kafka partitioning

Use `customer_id` as the record key for `transactions.raw` and `transactions.validated`, and `alert_id` for `fraud.alerts`. For the DLQ, retain the original Kafka key when valid and non-sensitive; otherwise use a deterministic source-position key (topic/partition/offset). Keep `transaction_id` in every valid transaction payload as the business deduplication key. Fix partition counts during MVP (do not change without an explicit re-partitioning/migration plan).

**Rationale:** colocates each customer's events within one topic partition for partition-local arrival ordering. Kafka partition ordering does **not** ensure event-time ordering; Spark still needs event-time handling and may shuffle by `customer_id`. Potential hot customers and partition scaling require monitoring.

**Acceptance:** two events with same customer key use same partition under fixed configuration; repeated `transaction_id` can be detected even when source is replayed; out-of-order event_time is handled explicitly.

## D2 — Online/offline feature consistency

Stage A: train and serve an event-only baseline using exactly the same versioned feature specification (never include `is_fraud`). Stage B: design a PostgreSQL online snapshot table of customer aggregates, maintained via the streaming path, with `customer_id`, `as_of_event_time`, `computed_at`, `feature_version`, and feature values. Offline training computes equivalent event-time aggregates via Spark and point-in-time joins.

**Rationale:** MinIO Gold historical Parquet is not an online feature store. A latest snapshot is not automatically valid for an event-time prediction. For late events, either perform as-of lookup against retained historical feature state or use the event-only fallback model; never use a snapshot containing future information. Align null-handling, categorical encoding, units, time windows, and versioning; verify parity on fixtures. Keep the model and feature_version linked.

**Acceptance:** automated fixture-driven parity checks; no future-data leakage; specified behavior on missing/stale snapshots; measure actual latency/freshness before setting SLOs. Stage B schema/mutation logic belongs in S20/S27.

## D3 — Processing and delivery guarantees

Target **at-least-once delivery with effectively-once persisted business effects**, not unconditional end-to-end exactly-once. Producers use Kafka idempotence and acknowledgements. Consumers commit offsets only after durable downstream handling; replay may still occur if a crash happens after output and before commit. Validation consumer publishes validated/DLQ before committing source offset (Kafka transactions optional). Spark uses checkpointing and sink-specific deduplication; `foreachBatch` external writes require replay safety. DB alert persister enforces `(transaction_id, model_version)` uniqueness and deterministic `alert_id`; auditing decisions is transactional with review-state changes. Do not overwrite a reviewed alert on replay. For outbound notifications driven by DB commits, use an outbox in a later story.

**Acceptance:** crash/retry test at each handoff; replay emits no duplicate persisted alerts or human reviews; source events are never silently discarded. NOTE: uniqueness is per transaction + model version, unlike the initial README's single transaction UNIQUE example.

## D4 — JSON Schema evolution and validation

Use JSON Schema Draft 2020-12 and maintain explicit versioned files; do not add Schema Registry in MVP. The current v1 event schemas use `schema_version: const "1.0"` and allow unspecified properties. Therefore a payload labeled "1.1" is **rejected by a 1.0 consumer**, even when the only payload change is an optional field. Adopt an explicit dual-read rollout for additive version 1.1 (1.0 + 1.1 supported by new consumers) before producers send 1.1. Breaking type, meaning, required field, unit, or key semantics require v2 and migration. Test both old/new payloads against deployed validators, not only structural compatibility. Enforce timezone-aware ISO-8601 UTC and format checks explicitly in code (Python jsonschema requires a FormatChecker); require input-size limit before JSON parsing. Unknown properties are accepted but ignored, never used in scoring until a new feature contract is promoted. Keep `is_fraud` prohibited in inference even if extra fields are accepted.

**Acceptance:** schema tests for invalid types, missing fields, unknown fields, version mismatch, dates and forbidden label; CI matrix for supported versions.

## D5 — Dead Letter Queue and retries

`transactions.dlq` receives persistent contract failures: invalid JSON, missing fields, unsupported schema versions, bad data formats, and poison records after bounded retries. Envelope includes source topic/partition/offset, safe record key, error_code, redacted error_detail and rejection timestamp; **no full payload by default**. Add `retry_count` and payload-reference contract only when a safe storage/replay design exists. Transient Kafka/DB/network outages are not immediately DLQ'ed: retry with exponential backoff, bounded attempts, then stop/pause/alert to avoid silently dropping valid events. DLQ publish must be durable before committing the offending source offset. Replay is operator-triggered after remediation, idempotent, and auditable; do not automatically republish indefinitely.

**Acceptance:** malformed JSON/unknown version goes to DLQ once as a logical record despite possible Kafka replays (using source position dedup key); transient failure does not yield unbounded loops; manual replay test; original data preserved only in permitted raw event retention or separately protected safe quarantine.

## S11 review checklist

- [x] Five decisions documented and rationale given
- [x] Existing schemas inspected for compatibility and identity inconsistencies
- [ ] Owner approves design choices
- [ ] Jira issue updated by authorized actor

## Implementation ownership

S12: repo structure / validation tooling. S14/S17: Kafka configuration, keys and validation-DLQ paths. S18-S20: Spark event-time, snapshot/features, replay. S27/S33: scoring/alert uniqueness, persistence transactions. S39: failure-injection E2E tests.

## References

- Apache Kafka design and delivery semantics: https://kafka.apache.org/40/design/design/
- Apache Kafka partition ordering: https://github.com/apache/kafka/blob/trunk/docs/getting-started/introduction.md
- Spark Structured Streaming 3.5 guide: https://spark.apache.org/docs/3.5.6/structured-streaming-programming-guide.html
- Confluent Schema Evolution (caveat: exact compatibility depends on JSON Schema policy): https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
