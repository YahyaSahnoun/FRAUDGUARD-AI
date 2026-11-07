# FraudGuard AI

**Status:** specification only — implementation not started. Sprint 1 Story S10 approved by project owner (2026-11-07); Story S11 design ready for review, not marked Done. Jira is not automatically synchronized.

FraudGuard AI is a learning-oriented fraud risk scoring and human-led investigation platform using synthetic data. The target system is documented in `FraudGuard_AI_Cahier_des_Charges.pdf` and `FraudGuard_AI_README.md` (supplied separately).

## Project plan and documents

- [Local story status](docs/project_plan.md)
- [S10 MVP scope](docs/product/mvp_scope.md)
- [S10 user journeys](docs/product/user_journeys.md)
- [S10 approval](docs/product/acceptance_criteria_s10.md)
- [Non-functional requirements](docs/product/non_functional_requirements.md)
- [S10 initial architecture](docs/architecture/overview.md)
- [S11 detailed architecture](docs/architecture/detailed_architecture.md)
- [S11 data contracts](docs/contracts/data_contracts.md)
- [S11 naming conventions](docs/contracts/naming_conventions.md)
- [S11 acceptance criteria](docs/contracts/acceptance_criteria_s11.md)
- [JSON Schemas](contracts/)

## Test the S11 contracts (requires pytest and jsonschema)

```bash
python -m pytest -q tests/contracts
```

No Kafka, Spark, FastAPI, or model integration exists yet. Future runtime story S12 initializes the repo's application packaging.

## Conventions

Documentation: French. Code, identifiers, API and commit messages: English. Only synthetic or duly authorized public data. Never autonomous account blocking or fraud adjudication.
