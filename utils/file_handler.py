import os

DATA_PATH = r"D:\sales-analytics-system\data\sales_data.txt"

EXPECTED_COLUMNS = [
    "TransactionID",
    "Date",
    "ProductID",
    "ProductName",
    "Quantity",
    "UnitPrice",
    "CustomerID",
    "Region"
]


def clean_numeric(value):
    """
    Remove commas and convert to float
    """
    try:
        return float(value.replace(",", "").strip())
    except Exception:
        return None


def read_and_clean_sales_data(file_path):
    total_records = 0
    valid_records = []
    invalid_records = 0

    # Handle non-UTF-8 safely
    with open(file_path, "r", encoding="latin-1") as file:
        header = file.readline().strip().split("|")

        for line in file:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            total_records += 1

            parts = line.split("|")

            # Skip rows with missing or extra fields
            if len(parts) != len(EXPECTED_COLUMNS):
                invalid_records += 1
                continue

            record = dict(zip(EXPECTED_COLUMNS, parts))

            # ---------------- VALIDATION RULES ----------------

            # TransactionID must start with 'T'
            if not record["TransactionID"].startswith("T"):
                invalid_records += 1
                continue

            # CustomerID and Region must not be missing
            if not record["CustomerID"].strip() or not record["Region"].strip():
                invalid_records += 1
                continue

            # Clean numeric fields
            quantity = clean_numeric(record["Quantity"])
            unit_price = clean_numeric(record["UnitPrice"])

            # Quantity and UnitPrice must be > 0
            if quantity is None or quantity <= 0:
                invalid_records += 1
                continue

            if unit_price is None or unit_price <= 0:
                invalid_records += 1
                continue

            # Clean ProductName (remove commas but keep value)
            record["ProductName"] = record["ProductName"].replace(",", "").strip()

            record["Quantity"] = int(quantity)
            record["UnitPrice"] = unit_price

            valid_records.append(record)

    # ---------------- REQUIRED OUTPUT ----------------
    print(f"Total records parsed: {total_records}")
    print(f"Invalid records removed: {invalid_records}")
    print(f"Valid records after cleaning: {len(valid_records)}")

    return valid_records


if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File not found: {DATA_PATH}")

    clean_data = read_and_clean_sales_data(DATA_PATH)
