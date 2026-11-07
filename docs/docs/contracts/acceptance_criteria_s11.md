# S11 — Acceptance criteria / review checklist

**Jira import ID:** 11. **Status:** ready for technical review (not yet approved / not Done).

- [x] Proposed architecture, roles, data/control flow, and operational boundaries documented.
- [x] Four Kafka topics, keys, value schemas and producer/consumer boundaries specified.
- [x] Versioned JSON Schemas for transaction, alert, DLQ and offline label produced.
- [x] Conventions for names, timestamps, versions and score field defined.
- [x] Risk of label leakage and online/offline feature parity explicitly identified.
- [x] Local JSON Schema checks run and recorded in test evidence below.
- [ ] Owner approves five proposed decisions recorded in `docs/adr/ADR-001-s11-architecture-decisions.md`.
- [ ] Actual Jira status synchronized by authorized user/tool.

## Evidence

- `docs/architecture/detailed_architecture.md`
- `docs/contracts/data_contracts.md`
- `docs/contracts/naming_conventions.md`
- `contracts/*.schema.json`
- `tests/contracts/test_json_contracts.py`

## Test scope

Static JSON Schema validation only. No Kafka, Spark, PostgreSQL, model or API calls performed. S11 closes upon review of design; integration tests belong to implementation Stories.

## Contrôle exécuté — 2026-11-07

Commande : `python -m pytest -q tests/contracts`
Résultat observé : **10 passed in 0.86s**.
Contrôle limité aux schémas JSON sur l'environnement de préparation ; aucune validation de producteur Kafka ni de workflow distribué.
