"""Adapt IBM TabFormer records to FraudGuard transaction contracts."""

import argparse
import csv
import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = ROOT / "data/raw/tabformer/card_transaction.v1.csv"

CHANNELS = {
    "Swipe Transaction": "pos",
    "Chip Transaction": "pos",
    "Online Transaction": "online",
}


def convert_row(row: dict, row_number: int) -> tuple[dict, dict]:
    """Convert one source row into a transaction and separate label."""
    timestamp = datetime.strptime(
        f"{row['Year']}-{row['Month']}-{row['Day']} {row['Time']}",
        "%Y-%m-%d %H:%M",
    ).replace(tzinfo=UTC)

    amount = float(Decimal(row["Amount"].replace("$", "").replace(",", "")))
    transaction_id = f"tx_{row_number:010d}"

    transaction = {
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "customer_id": f"cust_{row['User']}",
        "event_time": timestamp.isoformat().replace("+00:00", "Z"),
        "amount": amount,
        "currency": "USD",
        "merchant_category": str(row["MCC"]),
        "channel": CHANNELS[row["Use Chip"]],
        "country": "US",
        "card_id": f"card_{row['User']}_{row['Card']}",
        "merchant_id": str(row["Merchant Name"]),
        "merchant_city": row["Merchant City"] or None,
        "merchant_state": row["Merchant State"] or None,
        "merchant_zip": row["Zip"] or None,
    }

    label = {
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "is_fraud": {"Yes": 1, "No": 0}[row["Is Fraud?"]],
    }

    return transaction, label


def load_validator() -> Draft202012Validator:
    path = ROOT / "contracts/transaction.v1.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def export_sample(
    source: Path,
    output_dir: Path,
    years: set[int],
    limit: int,
) -> int:
    """Export a bounded set of validated events and labels."""
    if limit < 1:
        raise ValueError("limit must be positive")

    validator = load_validator()
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    with (
        source.open(newline="", encoding="utf-8") as infile,
        (output_dir / "transactions.jsonl").open("w", encoding="utf-8") as txfile,
        (output_dir / "labels.jsonl").open("w", encoding="utf-8") as labelfile,
    ):
        reader = csv.DictReader(infile)

        for row_number, row in enumerate(reader, start=1):
            if int(row["Year"]) not in years:
                continue

            transaction, label = convert_row(row, row_number)
            validator.validate(transaction)

            txfile.write(json.dumps(transaction) + "\n")
            labelfile.write(json.dumps(label) + "\n")

            count += 1
            if count >= limit:
                break

    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=Path("data/processed/tabformer"))
    parser.add_argument("--years", type=int, nargs="+", default=[2019, 2020])
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()

    count = export_sample(
        args.source,
        args.output,
        set(args.years),
        args.limit,
    )
    print(f"Exported {count} validated transactions and labels")


if __name__ == "__main__":
    main()
