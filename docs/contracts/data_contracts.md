# S11 — Data contracts v1

**Status:** proposed for approval. Normative machine-readable schemas in `contracts/`. UTF-8 JSON, UTC ISO-8601 timestamps; all required fields enforced; additional fields accepted for forward compatibility (consumers ignore unknown fields). Changing types or semantics is breaking; publish v2 rather than silently altering v1.

## Topics

| Topic | Kafka key | Value schema | Producer -> consumer | Retention |
|---|---|---|---|---|
| `transactions.raw` | `transaction_id` when available | `transaction.v1.schema.json` for valid events; malformed examples may arrive for DLQ testing | Simulator -> validator | To be configured S14/S17 |
| `transactions.validated` | `transaction_id` | `transaction.v1.schema.json` | validator -> Spark / scoring worker | To be configured S14/S17 |
| `transactions.dlq` | original `transaction_id` when known, otherwise generated envelope key | `dlq.v1.schema.json` | validator -> operator / replay | To be configured S14/S17 |
| `fraud.alerts` | `alert_id` | `fraud_alert.v1.schema.json` | scoring worker -> DB persister | To be configured S14/S27 |

Topic names come from the reference README. A scoring worker invoked once per event is proposed; exact topology remains open for later stories.

## Transaction contract

`schema_version=1.0`, `transaction_id`, pseudonymized `customer_id`, `event_time`, strictly positive `amount`, `currency` (3-letter code), `merchant_category`, `channel`, `country` (2-letter code). `is_fraud` must **not** appear in transaction inference JSON; put it in the offline label record. This deliberately tightens the illustrative source README, which shows `is_fraud` only for synthetic training records.

JSON numbers may exhibit floating-point rounding; this is an MVP scoring representation and not an accounting ledger. Future versions may adopt integer minor units or decimal strings.

## Fraud alert contract

`risk_score` in [0,1], threshold in [0,1], `model_version`, `reason_codes`, `status=new`, unique deterministic `alert_id` derived by unambiguous encoding of transaction ID + model version (canonical implementation and safe escaping required S27). A risk score **does not imply calibrated probability**. `risk_level` is optional display metadata, with thresholds separately documented later.

## DLQ contract

A structured envelope identifies the source record and error category. It excludes original payload by default; a small safe redacted excerpt can be added in a future version under explicit policy. Offsets and partitions are diagnostic, not business IDs.

## Offline training label contract

Labels are stored outside inference topics in a labeled historical dataset, keyed by transaction ID with `is_fraud` 0 or 1; train / validation / test splits strictly temporal. Synthetic ground truth may be emitted by the generator to a separate local artifact, not as model features.

## Consumer compatibility

- v1 consumer accepts additional JSON properties but must not rely on their presence.
- Missing required properties, wrong type, unsupported `schema_version` -> DLQ with reason.
- Producer must not redefine field meaning in a minor release; breaking changes get a new major schema and migration strategy.
- Timestamp comparison is performed using parsed timezone-aware datetimes; zero offset `Z` is preferred.
- Kafka ordering only holds within a partition; event-time logic deals with lateness.

## Open decisions

Partition counts, retention, event size limit, topic security, validated-event provenance, late-arrival threshold, model threshold, serving feature freshness, and alert publisher consistency are deferred to S14/S17/S20/S27, then baselined with measurements.
