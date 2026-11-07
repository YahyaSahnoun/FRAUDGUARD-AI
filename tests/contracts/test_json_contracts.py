"""S11 JSON Schema contract tests."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[2]


def validator(name: str) -> Draft202012Validator:
    schema_path = ROOT / "contracts" / f"{name}.v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    Draft202012Validator.check_schema(schema)

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def transaction() -> dict:
    return {
        "schema_version": "1.0",
        "transaction_id": "tx_000001",
        "customer_id": "cust_042",
        "event_time": "2026-11-07T10:15:00Z",
        "amount": 187.5,
        "currency": "MAD",
        "merchant_category": "retail",
        "channel": "online",
        "country": "MA",
    }


def test_valid_transaction():
    validator("transaction").validate(transaction())


def test_transaction_accepts_nonbreaking_extra_field():
    data = {**transaction(), "new_optional_field": "ok"}
    validator("transaction").validate(data)


@pytest.mark.parametrize(
    "change",
    [
        {"amount": -1},
        {"schema_version": "2.0"},
        {"event_time": "not-a-date"},
        {"is_fraud": 1},
    ],
)
def test_reject_invalid_transaction(change):
    data = {**transaction(), **change}

    with pytest.raises(ValidationError):
        validator("transaction").validate(data)


def test_valid_alert():
    alert = {
        "schema_version": "1.0",
        "alert_id": "alert_tx_000001_fraud-xgb-v1",
        "transaction_id": "tx_000001",
        "event_time": "2026-11-07T10:15:00Z",
        "scored_at": "2026-11-07T10:15:02Z",
        "risk_score": 0.91,
        "threshold": 0.8,
        "model_version": "fraud-xgb-v1",
        "reason_codes": ["high_amount"],
        "status": "new",
    }

    validator("fraud_alert").validate(alert)


def test_reject_uncalibrated_score_outside_range():
    alert = {
        "schema_version": "1.0",
        "alert_id": "alert_1",
        "transaction_id": "tx_1",
        "event_time": "2026-11-07T10:15:00Z",
        "scored_at": "2026-11-07T10:15:02Z",
        "risk_score": 1.2,
        "threshold": 0.8,
        "model_version": "v1",
        "reason_codes": [],
        "status": "new",
    }

    with pytest.raises(ValidationError):
        validator("fraud_alert").validate(alert)


def test_valid_dlq():
    dlq_event = {
        "schema_version": "1.0",
        "error_code": "invalid_json",
        "rejected_at": "2026-11-07T10:15:03Z",
        "source_topic": "transactions.raw",
        "source_partition": 0,
        "source_offset": 1,
        "record_key": None,
    }

    validator("dlq").validate(dlq_event)


def test_valid_label():
    label = {
        "schema_version": "1.0",
        "transaction_id": "tx_000001",
        "is_fraud": 1,
    }

    validator("training_label").validate(label)
