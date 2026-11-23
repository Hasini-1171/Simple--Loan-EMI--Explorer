
import csv
import json
from dataclasses import asdict
from pathlib import Path

from loan_service import create_loan


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

JSON_FILE = DATA_DIR / "loan_records.json"
CSV_FILE = DATA_DIR / "loan_records.csv"

FIELDS = [
    "loan_id",
    "customer_name",
    "category",
    "principal",
    "annual_rate",
    "tenure_months",
    "monthly_emi",
    "total_payment",
    "total_interest"
]


def save_loans(loans):
    """Save records to JSON and CSV."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    records = [asdict(loan) for loan in loans]

    json_temp = JSON_FILE.with_suffix(".tmp")
    csv_temp = CSV_FILE.with_suffix(".tmp")

    try:
        with json_temp.open("w", encoding="utf-8") as file:
            json.dump(records, file, indent=4)

        with csv_temp.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)

        json_temp.replace(JSON_FILE)
        csv_temp.replace(CSV_FILE)

    except (OSError, ValueError, TypeError):
        json_temp.unlink(missing_ok=True)
        csv_temp.unlink(missing_ok=True)
        raise


def load_loans():
    """Load records from JSON, recovering from CSV if needed."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if JSON_FILE.exists():
        try:
            with JSON_FILE.open(encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list):
                raise ValueError("Invalid JSON structure.")

            return [record_from_dict(item) for item in records]

        except (OSError, ValueError, TypeError, KeyError):
            print("JSON unavailable. Trying CSV backup.")

    if CSV_FILE.exists():
        try:
            with CSV_FILE.open(
                newline="", encoding="utf-8-sig"
            ) as file:
                records = list(csv.DictReader(file))

            loans = [record_from_dict(item) for item in records]

            print("Records recovered from CSV.")
            return loans

        except (OSError, ValueError, TypeError, KeyError):
            print("CSV recovery unsuccessful.")

    return []


def record_from_dict(record):
    """Recalculate financial values instead of trusting stored totals."""

    return create_loan(
        loan_id=record["loan_id"],
        customer_name=record["customer_name"],
        category=record["category"],
        principal=float(record["principal"]),
        annual_rate=float(record["annual_rate"]),
        tenure_months=int(record["tenure_months"])
    )


def import_csv(file_path, existing_loans=None):
    """Import valid rows and report rejected rows."""

    existing_loans = existing_loans or []

    existing_ids = {loan.loan_id for loan in existing_loans}

    accepted = []
    errors = []

    with Path(file_path).open(
        newline="", encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        required = {
            "customer_name",
            "category",
            "principal",
            "annual_rate",
            "tenure_months"
        }

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV file has missing required columns.")

        for row_number, row in enumerate(reader, start=2):
            try:
                loan_id = str(row.get("loan_id") or "").strip()

                if not loan_id or loan_id in existing_ids:
                    import uuid
                    loan_id = "LN-" + uuid.uuid4().hex[:10].upper()

                loan = create_loan(
                    loan_id,
                    row["customer_name"],
                    row["category"].title(),
                    float(row["principal"]),
                    float(row["annual_rate"]),
                    int(row["tenure_months"])
                )

                existing_ids.add(loan.loan_id)
                accepted.append(loan)

            except (ValueError, TypeError, KeyError) as error:
                errors.append(f"Row {row_number}: {error}")

    return accepted, errors
