import csv
from pathlib import Path
import os

# Current file location
CURRENT_DIR = Path(__file__).resolve().parent

# Project root directory
PROJECT_ROOT = CURRENT_DIR.parent

# Standard project folders
DATA_DIR = PROJECT_ROOT / "data"
ETL_DIR = PROJECT_ROOT / "utils"

"""
Reads sales data from file handling encoding issues

Returns: list of raw lines (strings)

Expected Output Format:
['T001|2024-12-01|P101|Laptop|2|45000|C001|North', ...]

Requirements:
- Use 'with' statement
- Handle different encodings (try 'utf-8', 'latin-1', 'cp1252')
- Handle FileNotFoundError with appropriate error message
- Skip the header row
- Remove empty lines
"""


def read_sales_data(filename, file_encoder):
    try:
        data = []
        with open(file= filename, mode='r', encoding=file_encoder, newline='\n',) as file:
            file_content = csv.reader(file, delimiter='|')

            header = next(file_content, None)  # skip header

            for row in file_content:
                if row and any(field.strip() for field in row):
                    data.append('|'.join(row))
        
        return data
    except UnicodeEncodeError:
        print(f'{filename} file is not in UTF-8 encoding')
        return data
    except FileNotFoundError:
        print(f'{filename} file does not exist.')
        return data
    


"""
Parses raw lines into clean list of dictionaries

Returns: list of dictionaries with keys:
['TransactionID', 'Date', 'ProductID', 'ProductName',
    'Quantity', 'UnitPrice', 'CustomerID', 'Region']

Expected Output Format:
[
    {
        'TransactionID': 'T001',
        'Date': '2024-12-01',
        'ProductID': 'P101',
        'ProductName': 'Laptop',
        'Quantity': 2,           # int type
        'UnitPrice': 45000.0,    # float type
        'CustomerID': 'C001',
        'Region': 'North'
    },
    ...
]

Requirements:
- Split by pipe delimiter '|'
- Handle commas within ProductName (remove or replace)
- Remove commas from numeric fields and convert to proper types
- Convert Quantity to int
- Convert UnitPrice to float
- Skip rows with incorrect number of fields
"""


def parse_transactions(raw_line):

    data = []
    for line in raw_line:
        t_id, dt, p_id, p_name, qty_raw, price_raw, c_id, region = [f.strip() for f in line.split('|')]
        
        # Handle commas within ProductName (replace commas with space)
        p_name_clean = p_name.replace(",", " ").strip()

        # Remove commas from numeric fields (e.g., "45,000")
        qty_clean = qty_raw.replace(",", "").strip()
        price_clean = price_raw.replace(",", "").strip()

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


"""
Validates transactions and applies optional filters

Parameters:
- transactions: list of transaction dictionaries
- region: filter by specific region (optional)
- min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
- max_amount: maximum transaction amount (optional)

Returns: tuple (valid_transactions, invalid_count, filter_summary)

Expected Output Format:
(
    [list of valid filtered transactions],
    5,  # count of invalid transactions
    {
        'total_input': 100,
        'invalid': 5,
        'filtered_by_region': 20,
        'filtered_by_amount': 10,
        'final_count': 65
    }
)

Validation Rules:
- Quantity must be > 0
- UnitPrice must be > 0
- All required fields must be present
- TransactionID must start with 'T'
- ProductID must start with 'P'
- CustomerID must start with 'C'

Filter Display:
- Print available regions to user before filtering
- Print transaction amount range (min/max) to user
- Show count of records after each filter applied
"""


def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
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

        # Store normalized numeric values back (optional but helpful)
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
    # Compute amounts once for filtering
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
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(current)
    }

    return current, filter_summary
