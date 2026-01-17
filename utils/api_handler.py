
"""
Fetches all products from DummyJSON API

Returns: list of product dictionaries

Expected Output Format:
[
    {
        'id': 1,
        'title': 'iPhone 9',
        'category': 'smartphones',
        'brand': 'Apple',
        'price': 549,
        'rating': 4.69
    },
    ...
]

Requirements:
- Fetch all available products (use limit=100)
- Handle connection errors with try-except
- Return empty list if API fails
- Print status message (success/failure)
"""

import requests

def fetch_all_products():
    url = "https://dummyjson.com/products"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx

        data = response.json()
        products = data.get("products", [])

        print(f"Successfully fetched {len(products)} products.")
        return products

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch products: {e}")
        return []
    


"""
Creates a mapping of product IDs to product info

Parameters: api_products from fetch_all_products()

Returns: dictionary mapping product IDs to info

Expected Output Format:
{
    1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
    2: {'title': 'iPhone X', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.44},
    ...
}
"""
def create_product_mapping(api_products):

    product_map = {}

    for product in api_products:
        try:
            product_id = product.get("id")
            title = product.get("title")
            category = product.get("category")
            brand = product.get("brand")
            rating = product.get("rating")
        except AttributeError:
            continue

        # Validate required fields
        if product_id is None or title is None:
            continue

        product_map[product_id] = {
            "title": title,
            "category": category,
            "brand": brand,
            "rating": rating
        }

    return product_map



"""
Enriches transaction data with API product information

Parameters:
- transactions: list of transaction dictionaries
- product_mapping: dictionary from create_product_mapping()

Returns: list of enriched transaction dictionaries

Expected Output Format (each transaction):
{
    'TransactionID': 'T001',
    'Date': '2024-12-01',
    'ProductID': 'P101',
    'ProductName': 'Laptop',
    'Quantity': 2,
    'UnitPrice': 45000.0,
    'CustomerID': 'C001',
    'Region': 'North',
    # NEW FIELDS ADDED FROM API:
    'API_Category': 'laptops',
    'API_Brand': 'Apple',
    'API_Rating': 4.7,
    'API_Match': True  # True if enrichment successful, False otherwise
}

Enrichment Logic:
- Extract numeric ID from ProductID (P101 → 101, P5 → 5)
- If ID exists in product_mapping, add API fields
- If ID doesn't exist, set API_Match to False and other fields to None
- Handle all errors gracefully

File Output:
- Save enriched data to 'data/enriched_sales_data.txt'
- Use same pipe-delimited format
- Include new columns in header
"""

import os
import re

def enrich_sales_data(transactions, product_mapping):

    enriched = []

    # Output file path
    output_dir = "data"
    output_file = os.path.join(output_dir, "enriched_sales_data.txt")
    os.makedirs(output_dir, exist_ok=True)

    # Columns for file output (pipe-delimited)
    base_cols = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region"
    ]
    new_cols = ["API_Category", "API_Brand", "API_Rating", "API_Match"]
    header_cols = base_cols + new_cols

    def extract_numeric_id(product_id):
        # P101 -> 101, P5 -> 5, also handles "P-101" or "P101A" by extracting digits
        if product_id is None:
            return None
        m = re.search(r"(\d+)", str(product_id))
        return int(m.group(1)) if m else None

    for txn in transactions:
        # Default enriched fields
        api_category = None
        api_brand = None
        api_rating = None
        api_match = False

        try:
            pid_num = extract_numeric_id(txn.get("ProductID"))
            if pid_num is not None and pid_num in product_mapping:
                info = product_mapping[pid_num]
                api_category = info.get("category")
                api_brand = info.get("brand")
                api_rating = info.get("rating")
                api_match = True
        except Exception:
            # Graceful handling: keep defaults (no match)
            pass

        # Build enriched transaction (do not mutate original)
        enriched_txn = dict(txn)
        enriched_txn["API_Category"] = api_category
        enriched_txn["API_Brand"] = api_brand
        enriched_txn["API_Rating"] = api_rating
        enriched_txn["API_Match"] = api_match

    def to_str(val):
        if val is None:
            return ""
        if isinstance(val, bool):
            return "True" if val else "False"
        return str(val)

    try:
        with open(output_file, "w", encoding="utf-8", newline="\n") as f:
            # Header
            f.write("|".join(header_cols) + "\n")

            # Rows
            for row in enriched:
                line = "|".join(to_str(row.get(col)) for col in header_cols)
                f.write(line + "\n")

        print(f"Enriched data saved successfully to: {output_file}")
    except Exception as e:
        print(f"Failed to write enriched file: {e}")

    return enriched
