"""
Calculates total revenue from all transactions

Returns: float (total revenue)

Expected Output: Single number representing sum of (Quantity * UnitPrice)
Example: 1545000.50
"""
def calculate_total_revenue(transactions):
    
    total_revenue = 0.0

    for txn in transactions:
        try:
            qty = int(txn.get("Quantity", 0))
            price = float(txn.get("UnitPrice", 0.0))
            total_revenue += qty * price
        except (ValueError, TypeError, AttributeError):
            continue

    return round(total_revenue, 2)



"""
Analyzes sales by region

Returns: dictionary with region statistics

Expected Output Format:
{
    'North': {
        'total_sales': 450000.0,
        'transaction_count': 15,
        'percentage': 29.13
    },
    'South': {...},
    ...
}

Requirements:
- Calculate total sales per region
- Count transactions per region
- Calculate percentage of total sales
- Sort by total_sales in descending order
"""

def region_wise_sales(transactions):

    region_stats = {}
    grand_total = 0.0

    # --- Aggregate sales and counts ---
    for txn in transactions:
        try:
            region = str(txn.get("Region")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not region:
            continue

        grand_total += amount

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0
            }

        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # --- Calculate percentage contribution ---
    for region in region_stats:
        if grand_total > 0:
            pct = (region_stats[region]["total_sales"] / grand_total) * 100
        else:
            pct = 0.0
        region_stats[region]["percentage"] = round(pct, 2)
        region_stats[region]["total_sales"] = round(region_stats[region]["total_sales"], 2)

    # --- Sort by total_sales (descending) ---
    sorted_region_stats = dict(
        sorted(
            region_stats.items(),
            key=lambda x: x[1]["total_sales"],
            reverse=True
        )
    )

    return sorted_region_stats


"""
Finds top n products by total quantity sold

Returns: list of tuples

Expected Output Format:
[
    ('Laptop', 45, 2250000.0),  # (ProductName, TotalQuantity, TotalRevenue)
    ('Mouse', 38, 19000.0),
    ...
]

Requirements:
- Aggregate by ProductName
- Calculate total quantity sold
- Calculate total revenue for each product
- Sort by TotalQuantity descending
- Return top n products
"""
def top_selling_products(transactions, n=5):

    product_stats = {}

    # --- Aggregate quantity and revenue per product ---
    for txn in transactions:
        try:
            product = str(txn.get("ProductName")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            revenue = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not product:
            continue

        if product not in product_stats:
            product_stats[product] = {
                "total_qty": 0,
                "total_revenue": 0.0
            }

        product_stats[product]["total_qty"] += qty
        product_stats[product]["total_revenue"] += revenue

    # --- Sort by total quantity (descending) ---
    sorted_products = sorted(
        product_stats.items(),
        key=lambda x: x[1]["total_qty"],
        reverse=True
    )

    # --- Return top n in required tuple format ---
    top_n = [
        (
            product,
            stats["total_qty"],
            round(stats["total_revenue"], 2)
        )
        for product, stats in sorted_products[:n]
    ]

    return top_n


"""
Analyzes customer purchase patterns

Returns: dictionary of customer statistics

Expected Output Format:
{
    'C001': {
        'total_spent': 95000.0,
        'purchase_count': 3,
        'avg_order_value': 31666.67,
        'products_bought': ['Laptop', 'Mouse', 'Keyboard']
    },
    'C002': {...},
    ...
}

Requirements:
- Calculate total amount spent per customer
- Count number of purchases
- Calculate average order value
- List unique products bought
- Sort by total_spent descending
"""

def customer_analysis(transactions):
    customer_stats = {}

    # --- Aggregate per customer ---
    for txn in transactions:
        try:
            customer = str(txn.get("CustomerID")).strip()
            product = str(txn.get("ProductName")).strip()
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
                "products_bought": set()
            }

        customer_stats[customer]["total_spent"] += amount
        customer_stats[customer]["purchase_count"] += 1

        if product:
            customer_stats[customer]["products_bought"].add(product)

    # --- Final calculations (avg order value, formatting) ---
    for cust in customer_stats:
        purchases = customer_stats[cust]["purchase_count"]
        total = customer_stats[cust]["total_spent"]

        avg = total / purchases if purchases > 0 else 0.0

        customer_stats[cust]["avg_order_value"] = round(avg, 2)
        customer_stats[cust]["total_spent"] = round(total, 2)
        customer_stats[cust]["products_bought"] = sorted(
            list(customer_stats[cust]["products_bought"])
        )

    # --- Sort by total_spent (descending) ---
    sorted_customers = dict(
        sorted(
            customer_stats.items(),
            key=lambda x: x[1]["total_spent"],
            reverse=True
        )
    )

    return sorted_customers



"""
Analyzes sales trends by date

Returns: dictionary sorted by date

Expected Output Format:
{
    '2024-12-01': {
        'revenue': 125000.0,
        'transaction_count': 8,
        'unique_customers': 6
    },
    '2024-12-02': {...},
    ...
}

Requirements:
- Group by date
- Calculate daily revenue
- Count daily transactions
- Count unique customers per day
- Sort chronologically
"""

def daily_sales_trend(transactions):

    daily = {}

    # --- Aggregate by date ---
    for txn in transactions:
        try:
            dt = str(txn.get("Date")).strip()
            cust = str(txn.get("CustomerID")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not dt:
            continue

        if dt not in daily:
            daily[dt] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily[dt]["revenue"] += amount
        daily[dt]["transaction_count"] += 1
        if cust:
            daily[dt]["unique_customers"].add(cust)

    # --- Finalize: convert set to count + rounding ---
    for dt in daily:
        daily[dt]["revenue"] = round(daily[dt]["revenue"], 2)
        daily[dt]["unique_customers"] = len(daily[dt]["unique_customers"])

    # --- Sort chronologically by date string (YYYY-MM-DD sorts correctly) ---
    sorted_daily = dict(sorted(daily.items(), key=lambda x: x[0]))

    return sorted_daily


"""
Identifies the date with highest revenue

Returns: tuple (date, revenue, transaction_count)

Expected Output Format:
('2024-12-15', 185000.0, 12)
"""

def find_peak_sales_day(transactions):

    daily = {}

    # --- Aggregate revenue and count by date ---
    for txn in transactions:
        try:
            dt = str(txn.get("Date")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            amount = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not dt:
            continue

        if dt not in daily:
            daily[dt] = {
                "revenue": 0.0,
                "transaction_count": 0
            }

        daily[dt]["revenue"] += amount
        daily[dt]["transaction_count"] += 1

    if not daily:
        return None, 0.0, 0

    # --- Find peak revenue day ---
    peak_date, peak_stats = max(
        daily.items(),
        key=lambda x: x[1]["revenue"]
    )

    return (
        peak_date,
        round(peak_stats["revenue"], 2),
        peak_stats["transaction_count"]
    )



"""
Identifies products with low sales

Returns: list of tuples

Expected Output Format:
[
    ('Webcam', 4, 12000.0),  # (ProductName, TotalQuantity, TotalRevenue)
    ('Headphones', 7, 10500.0),
    ...
]

Requirements:
- Find products with total quantity < threshold
- Include total quantity and revenue
- Sort by TotalQuantity ascending
"""

def low_performing_products(transactions, threshold=10):

    product_stats = {}

    # --- Aggregate quantity and revenue per product ---
    for txn in transactions:
        try:
            product = str(txn.get("ProductName")).strip()
            qty = int(txn.get("Quantity"))
            price = float(txn.get("UnitPrice"))
            revenue = qty * price
        except (ValueError, TypeError, AttributeError):
            continue

        if not product:
            continue

        if product not in product_stats:
            product_stats[product] = {
                "total_qty": 0,
                "total_revenue": 0.0
            }

        product_stats[product]["total_qty"] += qty
        product_stats[product]["total_revenue"] += revenue

    # --- Filter products with quantity below threshold ---
    low_products = [
        (
            product,
            stats["total_qty"],
            round(stats["total_revenue"], 2)
        )
        for product, stats in product_stats.items()
        if stats["total_qty"] < threshold
    ]

    # --- Sort by total quantity (ascending) ---
    low_products_sorted = sorted(
        low_products,
        key=lambda x: x[1]
    )

    return low_products_sorted




