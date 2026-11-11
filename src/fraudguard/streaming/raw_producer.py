"""Publish raw TabFormer transactions to Kafka."""

import argparse
import csv
import json
from collections.abc import Iterator
from pathlib import Path

from confluent_kafka import Producer
from jsonschema import Draft202012Validator

from fraudguard.core.config import get_settings

ROOT = Path(__file__).resolve().parents[3]

DEFAULT_SOURCE = ROOT / "data/raw/tabformer/card_transaction.v1.csv"
CONTRACT = ROOT / "contracts/tabformer_raw.v1.schema.json"

TOPIC = "transactions.raw"


def load_validator() -> Draft202012Validator:
    schema = json.loads(CONTRACT.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def iter_transactions(
    source: Path,
    years: set[int],
    limit: int | None = None,
) -> Iterator[tuple[str, dict]]:
    """Read selected transactions without loading the full CSV."""

    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")

    emitted = 0

    with source.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV header is missing")

        if "Is Fraud?" not in reader.fieldnames:
            raise ValueError("Fraud label column is missing")

        for row_number, row in enumerate(reader, start=1):
            if int(row["Year"]) not in years:
                continue

            user_id = row["User"]
            key = f"cust_{user_id}"

            # Preserve original source values.
            raw = {name: value for name, value in row.items() if name != "Is Fraud?"}

            event = {
                "schema_version": "1.0",
                "source_row_id": f"tx_{row_number:010d}",
                "raw": raw,
            }

            yield key, event

            emitted += 1
            if limit is not None and emitted >= limit:
                break


def publish_transactions(
    source: Path,
    years: set[int],
    limit: int | None,
) -> int:
    """Validate and publish raw transactions to Kafka."""

    settings = get_settings()
    validator = load_validator()

    producer = Producer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "enable.idempotence": True,
            "acks": "all",
            "message.timeout.ms": 30000,
        }
    )

    delivered = 0
    errors = []

    def delivery_callback(error, message):
        nonlocal delivered

        if error is not None:
            errors.append(str(error))
        else:
            delivered += 1

    try:
        for key, event in iter_transactions(source, years, limit):
            validator.validate(event)

            payload = json.dumps(event).encode("utf-8")

            # Kafka producer is asynchronous.
            while True:
                try:
                    producer.produce(
                        topic=TOPIC,
                        key=key.encode("utf-8"),
                        value=payload,
                        callback=delivery_callback,
                    )
                    break
                except BufferError:
                    producer.poll(1)

            producer.poll(0)

            if errors:
                raise RuntimeError(f"Kafka delivery failed: {errors[0]}")

    finally:
        remaining = producer.flush(35)

    if remaining:
        raise RuntimeError(f"{remaining} Kafka messages not delivered")

    if errors:
        raise RuntimeError(f"Kafka delivery failed: {errors[0]}")

    return delivered


def main():
    parser = argparse.ArgumentParser(description="Publish raw TabFormer events.")

    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
    )
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        default=[2019, 2020],
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    count = publish_transactions(
        source=args.source,
        years=set(args.years),
        limit=args.limit,
    )

    print(f"Successfully delivered {count} Kafka messages")


if __name__ == "__main__":
    main()
