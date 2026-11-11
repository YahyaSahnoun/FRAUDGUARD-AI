"""Tests for the raw Kafka producer input."""

import csv
from pathlib import Path

import pytest

from fraudguard.streaming.raw_producer import (
    iter_transactions,
    load_validator,
)

FIELDS = [
    "User",
    "Card",
    "Year",
    "Month",
    "Day",
    "Time",
    "Amount",
    "Use Chip",
    "Merchant Name",
    "Merchant City",
    "Merchant State",
    "Zip",
    "MCC",
    "Errors?",
    "Is Fraud?",
]


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "sample.csv"

    rows = [
        {
            "User": "0",
            "Card": "0",
            "Year": "2018",
            "Month": "12",
            "Day": "31",
            "Time": "10:00",
            "Amount": "$10.00",
            "Use Chip": "Chip Transaction",
            "Merchant Name": "123",
            "Merchant City": "Boston",
            "Merchant State": "MA",
            "Zip": "02101",
            "MCC": "5411",
            "Errors?": "",
            "Is Fraud?": "No",
        },
        {
            "User": "1",
            "Card": "0",
            "Year": "2019",
            "Month": "1",
            "Day": "1",
            "Time": "12:30",
            "Amount": "-$25.50",
            "Use Chip": "Online Transaction",
            "Merchant Name": "456",
            "Merchant City": "New York",
            "Merchant State": "NY",
            "Zip": "",
            "MCC": "5300",
            "Errors?": "",
            "Is Fraud?": "Yes",
        },
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return path


def test_filter_by_year(sample_csv):
    events = list(iter_transactions(sample_csv, {2019}))

    assert len(events) == 1
    assert events[0][0] == "cust_1"


def test_raw_values_and_label_isolation(sample_csv):
    _, event = next(iter_transactions(sample_csv, {2019}))

    assert event["source_row_id"] == "tx_0000000002"
    assert event["raw"]["Amount"] == "-$25.50"
    assert "Is Fraud?" not in event["raw"]

    load_validator().validate(event)


def test_reproducibility(sample_csv):
    first = list(iter_transactions(sample_csv, {2018, 2019}))
    second = list(iter_transactions(sample_csv, {2018, 2019}))

    assert first == second


def test_invalid_limit(sample_csv):
    with pytest.raises(ValueError):
        list(iter_transactions(sample_csv, {2019}, limit=0))
