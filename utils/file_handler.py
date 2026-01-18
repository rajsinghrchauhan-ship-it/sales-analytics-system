## **File Format:**
    # - Pipe-delimited (`|`) format
    # - Non-UTF-8 encoding (handle encoding issues)
    # - Data quality issues (commas in fields, missing/extra fields, numeric commas, invalid data)


##Read Sales Data with Encoding Handling

import csv
from pathlib import Path

# Current file location
CURRENT_DIR = Path(__file__).resolve().parent

# Project root directory
PROJECT_ROOT = CURRENT_DIR.parent
file_path = PROJECT_ROOT / "data" / "sales_data.txt"

# read data with encoding handling
def read_sales_data(filename):
    """
    Reads sales data handling encoding issues and skipping header/empty lines.
    Tries multiple encodings: 'utf-8', 'latin-1', 'cp1252'.
    Returns: list[str] of raw lines with '|' still joining fields.
    """
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
    last_error = None

    for enc in encodings_to_try:
        try:
            data = []
            # IMPORTANT: keep newline='' for csv module
            with open(filename, mode='r', encoding=enc, newline='') as file:
                reader = csv.reader(file, delimiter='|')
                _ = next(reader, None)  # skip header if present
                for row in reader:
                    if row and any((field or "").strip() for field in row):
                        data.append('|'.join(row))

            if data:
                print(f"Read {len(data)} data lines using encoding: {enc}")
            else:
                print(f"No data lines found using encoding: {enc}")
            return data

        except UnicodeDecodeError as e:
            last_error = e
            # try the next encoding
            continue
        except FileNotFoundError:
            print(f'{filename} file does not exist.')
            return []

    # If all encodings failed due to decode issues
    print(f"Failed to decode {filename} with tried encodings {encodings_to_try}. Last error: {last_error}")
    return []

# %%
a = read_sales_data(file_path)

# %%
first_row = a[0].split('|') if a else []
print(first_row)

# Parse and clean data

def parse_transactions(raw_lines):
    data = []
    for line in raw_lines:
        parts = [f.strip() for f in line.split('|')]
        if len(parts) < 8:
            continue  # Skip lines that don't have exactly 8 fields
        t_id, dt, p_id, p_name, qty_raw, price_raw, c_id, region = parts[:8]

        # Handle commas within ProductName (replace commas with space)
        p_name_clean = (p_name or "").replace(",", " ").strip()

        # Remove commas from numeric fields (e.g., "45,000")
        qty_clean = (qty_raw or "").replace(",", "").strip()
        price_clean = (price_raw or "").replace(",", "").strip()

        try:
            qty = int(qty_clean)
            unit_price = float(price_clean)
        except ValueError:
            continue

        data.append(
            {
                "TransactionID": t_id,
                "Date": dt,
                "ProductID": p_id,
                "ProductName": p_name_clean,
                "Quantity": qty,
                "UnitPrice": unit_price,
                "CustomerID": c_id,
                "Region": region,
            }
        )
    return data

## Data validation and filtering

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters.
    Returns: (valid_filtered, invalid_count, filter_summary)
    """
    required_fields = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]

    total_input = len(transactions)
    invalid_count = 0
    valid_transactions = []

    # --- Print available regions (from all input, if present) ---
    regions = sorted({
        t.get("Region", "").strip()
        for t in transactions
        if isinstance(t, dict) and t.get("Region")
    })
    print("Available regions:", regions if regions else "None found")

    # --- Validate transactions ---
    for txn in transactions:
        # Must be a dict
        if not isinstance(txn, dict):
            invalid_count += 1
            continue

        # All required fields must exist and be non-empty (basic check)
        missing = [k for k in required_fields if k not in txn or txn[k] in (None, "")]
        if missing:
            invalid_count += 1
            continue

        # ID prefix rules
        if not str(txn["TransactionID"]).startswith("T"):
            invalid_count += 1
            continue
        if not str(txn["ProductID"]).startswith("P"):
            invalid_count += 1
            continue
        if not str(txn["CustomerID"]).startswith("C"):
            invalid_count += 1
            continue

        # Quantity and UnitPrice positive + type-safe
        try:
            qty = int(txn["Quantity"])
            price = float(txn["UnitPrice"])
        except (ValueError, TypeError):
            invalid_count += 1
            continue

        if qty <= 0 or price <= 0:
            invalid_count += 1
            continue

        # Normalize numeric values
        txn["Quantity"] = qty
        txn["UnitPrice"] = price
        valid_transactions.append(txn)

    # --- Amount range print (computed from valid transactions) ---
    if valid_transactions:
        amounts = [t["Quantity"] * t["UnitPrice"] for t in valid_transactions]
        print(f"Transaction amount range (valid only): min={min(amounts):.2f}, max={max(amounts):.2f}")
    else:
        print("Transaction amount range: no valid transactions to compute range.")

    # Summary counters
    filtered_by_region = 0
    filtered_by_amount = 0

    current = valid_transactions
    print(f"After validation: {len(current)} records (invalid: {invalid_count})")

    # --- Region filter ---
    if region is not None:
        before = len(current)
        current = [t for t in current if str(t.get("Region", "")).strip().lower() == str(region).strip().lower()]
        filtered_by_region = before - len(current)
        print(f"After region filter ({region}): {len(current)} records")

    # --- Amount filters ---
    def amount(t):
        return t["Quantity"] * t["UnitPrice"]

    if min_amount is not None:
        before = len(current)
        current = [t for t in current if amount(t) >= float(min_amount)]
        filtered_by_amount += before - len(current)
        print(f"After min_amount filter ({min_amount}): {len(current)} records")

    if max_amount is not None:
        before = len(current)
        current = [t for t in current if amount(t) <= float(max_amount)]
        filtered_by_amount += before - len(current)
        print(f"After max_amount filter ({max_amount}): {len(current)} records")

    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "valid_records": len(valid_transactions),
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(current)
    }
    return current, invalid_count, filter_summary

# %%
# Parse all transactions and validate/filter
clean_data = parse_transactions(a)

print("\nSample parsed transactions (Expected Output Format):")
for txn in clean_data[:1]:  # show first 3 only
    print(txn)

clean_data, invalid_count, filter_summary = validate_and_filter(clean_data, 'North', 300, 5000)

# %%
print("\nsummary_data")
print(filter_summary)
print("\ninvalid_count (as per spec):", invalid_count)
