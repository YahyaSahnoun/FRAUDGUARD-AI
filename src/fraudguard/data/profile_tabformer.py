"""Profile IBM TabFormer transactions without loading all rows into RAM."""

from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/raw/tabformer/card_transaction.v1.csv")


def main():
    total = 0
    fraud_counts = {}
    users = set()

    for chunk in pd.read_csv(DATA_PATH, chunksize=100_000):
        total += len(chunk)

        for label, count in chunk["Is Fraud?"].value_counts().items():
            fraud_counts[label] = fraud_counts.get(label, 0) + int(count)

        users.update(chunk["User"].dropna().unique().tolist())

    print(f"Transactions: {total:,}")
    print(f"Unique users: {len(users):,}")
    print(f"Fraud counts: {fraud_counts}")

    fraud_total = fraud_counts.get("Yes", 0)
    print(f"Fraud rate: {fraud_total / total:.4%}")


def profile_by_year():
    yearly = {}

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=["Year", "Is Fraud?"],
        chunksize=100_000,
    ):
        grouped = chunk.groupby("Year")["Is Fraud?"].agg(
            total="count",
            fraud=lambda values: (values == "Yes").sum(),
        )

        for year, row in grouped.iterrows():
            if year not in yearly:
                yearly[year] = {"total": 0, "fraud": 0}

            yearly[year]["total"] += int(row["total"])
            yearly[year]["fraud"] += int(row["fraud"])

    for year in sorted(yearly):
        total = yearly[year]["total"]
        fraud = yearly[year]["fraud"]
        print(f"{year}: {total:,} transactions | {fraud:,} frauds | {fraud / total:.3%}")


def profile_quality():
    """Inspect data quality using memory-efficient chunks."""

    total = 0
    missing = {}
    invalid_amounts = 0
    negative_amounts = 0
    zero_amounts = 0
    invalid_dates = 0
    channels = {}

    for chunk in pd.read_csv(
        DATA_PATH,
        chunksize=100_000,
        dtype={"Merchant Name": "string", "Zip": "string"},
    ):
        total += len(chunk)

        # Missing values
        for col, count in chunk.isna().sum().items():
            missing[col] = missing.get(col, 0) + int(count)

        # Transaction amounts
        amounts = pd.to_numeric(
            chunk["Amount"]
            .astype("string")
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False),
            errors="coerce",
        )

        invalid_amounts += int(amounts.isna().sum())
        negative_amounts += int((amounts < 0).sum())
        zero_amounts += int((amounts == 0).sum())

        # Validate calendar dates and transaction times
        dates = pd.to_datetime(
            chunk[["Year", "Month", "Day"]].rename(
                columns={"Year": "year", "Month": "month", "Day": "day"}
            ),
            errors="coerce",
        )

        times_valid = chunk["Time"].astype("string").str.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d")

        invalid_dates += int((dates.isna() | ~times_valid.fillna(False)).sum())

        # Payment channels
        for channel, count in chunk["Use Chip"].value_counts().items():
            channels[channel] = channels.get(channel, 0) + int(count)

    print(f"\nTotal transactions: {total:,}")
    print(f"Invalid amounts: {invalid_amounts:,}")
    print(f"Negative amounts: {negative_amounts:,}")
    print(f"Zero amounts: {zero_amounts:,}")
    print(f"Invalid timestamps: {invalid_dates:,}")

    print("\nMissing values:")
    for col, count in missing.items():
        if count:
            print(f"{col}: {count:,} ({count / total:.2%})")

    print("\nPayment channels:")
    for channel, count in channels.items():
        print(f"{channel}: {count:,}")


def profile_amounts():
    counts = {
        "negative": {"total": 0, "fraud": 0},
        "zero": {"total": 0, "fraud": 0},
        "positive": {"total": 0, "fraud": 0},
    }

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=["Amount", "Is Fraud?", "Use Chip"],
        chunksize=100_000,
    ):
        amounts = pd.to_numeric(
            chunk["Amount"].str.replace("$", "", regex=False).str.replace(",", "", regex=False)
        )

        for name, mask in {
            "negative": amounts < 0,
            "zero": amounts == 0,
            "positive": amounts > 0,
        }.items():
            counts[name]["total"] += int(mask.sum())
            counts[name]["fraud"] += int(((chunk["Is Fraud?"] == "Yes") & mask).sum())

    print("\nAmount distribution:")
    for name, values in counts.items():
        rate = values["fraud"] / values["total"] if values["total"] else 0
        print(
            f"{name}: {values['total']:,} transactions, "
            f"{values['fraud']:,} frauds, fraud rate={rate:.4%}"
        )


if __name__ == "__main__":
    main()
    profile_by_year()
    profile_quality()
    profile_amounts()
