
# utils/data_processor.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions.

    Returns: float (total revenue)
    Expected Output: sum of (Quantity * UnitPrice), e.g. 1545000.50
    """
    total_revenue = 0.0
    for txn in transactions:
        try:
            qty = int(txn.get("Quantity", 0))
            price = float(txn.get("UnitPrice", 0.0))
            total_revenue += qty * price
        except (ValueError, TypeError, AttributeError):
            continue
    return round(total_revenue, 2)


def region_wise_sales(transactions):
    """
    Analyzes sales by region.

    Returns: dict
      {
        'North': {'total_sales': 450000.0, 'transaction_count': 15, 'percentage': 29.13},
        'South': {...},
        ...
      }
    Sorted by total_sales desc.
    """
    region_stats = {}
    grand_total = 0.0

    # Aggregate sales and counts
    for txn in transactions:
        try:
            region = str(txn.get("Region", "")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not region:
            continue

        grand_total += amount
        if region not in region_stats:
            region_stats[region] = {"total_sales": 0.0, "transaction_count": 0}
        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # Percentage & rounding
    for region in region_stats:
        pct = (region_stats[region]["total_sales"] / grand_total) * 100 if grand_total > 0 else 0.0
        region_stats[region]["percentage"] = round(pct, 2)
        region_stats[region]["total_sales"] = round(region_stats[region]["total_sales"], 2)

    # Sort by total_sales desc
    sorted_region_stats = dict(
        sorted(region_stats.items(), key=lambda x: x[1]["total_sales"], reverse=True)
    )
    return sorted_region_stats


def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold.

    Returns: list of tuples
      [
        ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ('Mouse', 38, 19000.0),
        ...
      ]
    """
    product_stats = {}

    for txn in transactions:
        try:
            product = str(txn.get("ProductName", "")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            revenue = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not product:
            continue

        if product not in product_stats:
            product_stats[product] = {"total_qty": 0, "total_revenue": 0.0}
        product_stats[product]["total_qty"] += qty
        product_stats[product]["total_revenue"] += revenue

    sorted_products = sorted(
        product_stats.items(), key=lambda x: x[1]["total_qty"], reverse=True
    )

    top_n = [
        (product, stats["total_qty"], round(stats["total_revenue"], 2))
        for product, stats in sorted_products[:n]
    ]
    return top_n


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns.

    Returns: dict
      {
        'C001': {
          'total_spent': 95000.0,
          'purchase_count': 3,
          'avg_order_value': 31666.67,
          'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        ...
      }
    Sorted by total_spent desc.
    """
    customer_stats = {}

    for txn in transactions:
        try:
            customer = str(txn.get("CustomerID", "")).strip()
            product = str(txn.get("ProductName", "")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not customer:
            continue

        if customer not in customer_stats:
            customer_stats[customer] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set(),
            }

        customer_stats[customer]["total_spent"] += amount
        customer_stats[customer]["purchase_count"] += 1
        if product:
            customer_stats[customer]["products_bought"].add(product)

    # finalize
    for cust in customer_stats:
        purchases = customer_stats[cust]["purchase_count"]
        total = customer_stats[cust]["total_spent"]
        avg = total / purchases if purchases > 0 else 0.0
        customer_stats[cust]["avg_order_value"] = round(avg, 2)
        customer_stats[cust]["total_spent"] = round(total, 2)
        customer_stats[cust]["products_bought"] = sorted(
            list(customer_stats[cust]["products_bought"])
        )

    sorted_customers = dict(
        sorted(customer_stats.items(), key=lambda x: x[1]["total_spent"], reverse=True)
    )
    return sorted_customers


def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date.

    Returns: dict sorted by date
      {
        '2024-12-01': {'revenue': 125000.0, 'transaction_count': 8, 'unique_customers': 6},
        ...
      }
    """
    daily = {}

    for txn in transactions:
        try:
            dt = str(txn.get("Date", "")).strip()
            cust = str(txn.get("CustomerID", "")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not dt:
            continue

        if dt not in daily:
            daily[dt] = {"revenue": 0.0, "transaction_count": 0, "unique_customers": set()}

        daily[dt]["revenue"] += amount
        daily[dt]["transaction_count"] += 1
        if cust:
            daily[dt]["unique_customers"].add(cust)

    for dt in daily:
        daily[dt]["revenue"] = round(daily[dt]["revenue"], 2)
        daily[dt]["unique_customers"] = len(daily[dt]["unique_customers"])

    sorted_daily = dict(sorted(daily.items(), key=lambda x: x[0]))  # YYYY-MM-DD sorts lexicographically
    return sorted_daily


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue.

    Returns: tuple (date, revenue, transaction_count)
      e.g. ('2024-12-15', 185000.0, 12)
    """
    daily = {}

    for txn in transactions:
        try:
            dt = str(txn.get("Date", "")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not dt:
            continue

        if dt not in daily:
            daily[dt] = {"revenue": 0.0, "transaction_count": 0}

        daily[dt]["revenue"] += amount
        daily[dt]["transaction_count"] += 1

    if not daily:
        return None, 0.0, 0

    peak_date, peak_stats = max(daily.items(), key=lambda x: x[1]["revenue"])
    return (peak_date, round(peak_stats["revenue"], 2), peak_stats["transaction_count"])


def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales.

    Returns: list of tuples sorted asc by quantity
      [
        ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
        ...
      ]
    """
    product_stats = {}

    for txn in transactions:
        try:
            product = str(txn.get("ProductName", "")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            revenue = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not product:
            continue

        if product not in product_stats:
            product_stats[product] = {"total_qty": 0, "total_revenue": 0.0}

        product_stats[product]["total_qty"] += qty
        product_stats[product]["total_revenue"] += revenue

    low_products = [
        (product, stats["total_qty"], round(stats["total_revenue"], 2))
        for product, stats in product_stats.items()
        if stats["total_qty"] < threshold
    ]

    low_products_sorted = sorted(low_products, key=lambda x: x[1])
    return low_products_sorted
