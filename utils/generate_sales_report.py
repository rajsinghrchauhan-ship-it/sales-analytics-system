import os
from datetime import datetime

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report
    """

    # ---------------- helpers ----------------
    def money(x):
        try:
            return f"₹{float(x):,.2f}"
        except Exception:
            return "₹0.00"

    def fmt_int(x):
        try:
            return f"{int(x):,}"
        except Exception:
            return "0"

    def fmt_pct(x):
        try:
            return f"{float(x):.2f}%"
        except Exception:
            return "0.00%"

    def safe_amount(txn):
        return int(txn.get("Quantity")) * float(txn.get("UnitPrice"))

    def safe_date_range(txns):
        dates = []
        for t in txns:
            d = t.get("Date")
            if isinstance(d, str) and d.strip():
                dates.append(d.strip())
        return (min(dates), max(dates)) if dates else (None, None)

    def avg_txn_value_per_region(txns):
        agg = {}
        for t in txns:
            try:
                r = str(t.get("Region", "")).strip()
                amt = safe_amount(t)
            except Exception:
                continue
            if not r:
                continue
            agg.setdefault(r, {"sum": 0.0, "count": 0})
            agg[r]["sum"] += amt
            agg[r]["count"] += 1

        out = {}
        for r, v in agg.items():
            out[r] = (v["sum"] / v["count"]) if v["count"] else 0.0

        return dict(sorted(out.items(), key=lambda x: x[1], reverse=True))

    def unenriched_products(enriched_txns):
        missing = set()
        for t in enriched_txns:
            try:
                if not bool(t.get("API_Match", False)):
                    pn = str(t.get("ProductName", "")).strip()
                    if pn:
                        missing.add(pn)
            except Exception:
                continue
        return sorted(missing)

    # ---------------- 1) HEADER ----------------
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records_processed = len(transactions)

    # ---------------- 2) OVERALL SUMMARY ----------------
    total_revenue = 0.0
    total_transactions = 0
    for t in transactions:
        try:
            total_revenue += safe_amount(t)
            total_transactions += 1
        except Exception:
            continue

    avg_order_value = (total_revenue / total_transactions) if total_transactions else 0.0
    min_date, max_date = safe_date_range(transactions)

    # ---------------- 3) REGION-WISE PERFORMANCE ----------------
    region_stats = {}
    grand_total = 0.0
    for t in transactions:
        try:
            r = str(t.get("Region", "")).strip()
            amt = safe_amount(t)
        except Exception:
            continue
        if not r:
            continue
        grand_total += amt
        region_stats.setdefault(r, {"total_sales": 0.0, "transaction_count": 0})
        region_stats[r]["total_sales"] += amt
        region_stats[r]["transaction_count"] += 1

    region_rows = []
    for r, v in region_stats.items():
        pct = (v["total_sales"] / grand_total * 100) if grand_total else 0.0
        region_rows.append((r, v["total_sales"], pct, v["transaction_count"]))
    region_rows.sort(key=lambda x: x[1], reverse=True)

    # ---------------- 4) TOP 5 PRODUCTS ----------------
    product_stats = {}
    for t in transactions:
        try:
            pn = str(t.get("ProductName", "")).strip()
            qty = int(t.get("Quantity"))
            price = float(t.get("UnitPrice"))
        except Exception:
            continue
        if not pn:
            continue
        product_stats.setdefault(pn, {"qty": 0, "rev": 0.0})
        product_stats[pn]["qty"] += qty
        product_stats[pn]["rev"] += qty * price

    top_products = sorted(product_stats.items(), key=lambda x: x[1]["qty"], reverse=True)[:5]

    # ---------------- 5) TOP 5 CUSTOMERS ----------------
    customer_stats = {}
    for t in transactions:
        try:
            cid = str(t.get("CustomerID", "")).strip()
            amt = safe_amount(t)
        except Exception:
            continue
        if not cid:
            continue
        customer_stats.setdefault(cid, {"spent": 0.0, "count": 0})
        customer_stats[cid]["spent"] += amt
        customer_stats[cid]["count"] += 1

    top_customers = sorted(customer_stats.items(), key=lambda x: x[1]["spent"], reverse=True)[:5]

    # ---------------- 6) DAILY SALES TREND ----------------
    daily = {}
    for t in transactions:
        try:
            d = str(t.get("Date", "")).strip()
            cid = str(t.get("CustomerID", "")).strip()
            amt = safe_amount(t)
        except Exception:
            continue
        if not d:
            continue
        daily.setdefault(d, {"revenue": 0.0, "transaction_count": 0, "customers": set()})
        daily[d]["revenue"] += amt
        daily[d]["transaction_count"] += 1
        if cid:
            daily[d]["customers"].add(cid)

    daily_rows = []
    for d, v in daily.items():
        daily_rows.append((d, v["revenue"], v["transaction_count"], len(v["customers"])))
    daily_rows.sort(key=lambda x: x[0])  # YYYY-MM-DD => chronological

    # ---------------- 7) PRODUCT PERFORMANCE ANALYSIS ----------------
    # Best selling day
    if daily_rows:
        best_day = max(daily_rows, key=lambda x: x[1])  # (date, revenue, txn_count, uniq_customers)
        best_selling = (best_day[0], best_day[1], best_day[2])
    else:
        best_selling = (None, 0.0, 0)

    # Low performing products (qty < 10)
    low_products = [(pn, v["qty"], v["rev"]) for pn, v in product_stats.items() if v["qty"] < 10]
    low_products.sort(key=lambda x: x[1])  # ascending qty

    # Average transaction value per region
    avg_region = avg_txn_value_per_region(transactions)

    # ---------------- 8) API ENRICHMENT SUMMARY ----------------
    total_enriched_attempt = len(enriched_transactions)
    success_enriched = 0
    for t in enriched_transactions:
        try:
            if bool(t.get("API_Match", False)):
                success_enriched += 1
        except Exception:
            continue
    success_rate = (success_enriched / total_enriched_attempt * 100) if total_enriched_attempt else 0.0
    missing_products = unenriched_products(enriched_transactions)

    # ---------------- build report ----------------
    lines = []
    lines.append("=" * 44)
    lines.append("       SALES ANALYTICS REPORT")
    lines.append(f"     Generated: {now}")
    lines.append(f"     Records Processed: {fmt_int(records_processed)}")
    lines.append("=" * 44)
    lines.append("")

    lines.append("OVERALL SUMMARY")
    lines.append("-" * 44)
    lines.append(f"Total Revenue:        {money(total_revenue)}")
    lines.append(f"Total Transactions:   {fmt_int(total_transactions)}")
    lines.append(f"Average Order Value:  {money(avg_order_value)}")
    lines.append(f"Date Range:           {(min_date + ' to ' + max_date) if (min_date and max_date) else 'N/A'}")
    lines.append("")

    lines.append("REGION-WISE PERFORMANCE")
    lines.append("-" * 44)
    lines.append(f"{'Region':<10}{'Sales':>15}  {'% of Total':>10}  {'Transactions':>12}")
    if region_rows:
        for r, sales, p, cnt in region_rows:
            lines.append(f"{r:<10}{money(sales):>15}  {fmt_pct(p):>10}  {fmt_int(cnt):>12}")
    else:
        lines.append("No region data available.")
    lines.append("")

    lines.append("TOP 5 PRODUCTS")
    lines.append("-" * 44)
    lines.append(f"{'Rank':<6}{'Product Name':<22}{'Quantity Sold':>14}{'Revenue':>14}")
    if top_products:
        for i, (pn, v) in enumerate(top_products, start=1):
            lines.append(f"{i:<6}{pn[:22]:<22}{fmt_int(v['qty']):>14}{money(v['rev']):>14}")
    else:
        lines.append("No product data available.")
    lines.append("")

    lines.append("TOP 5 CUSTOMERS")
    lines.append("-" * 44)
    lines.append(f"{'Rank':<6}{'Customer ID':<14}{'Total Spent':>14}{'Order Count':>12}")
    if top_customers:
        for i, (cid, v) in enumerate(top_customers, start=1):
            lines.append(f"{i:<6}{cid:<14}{money(v['spent']):>14}{fmt_int(v['count']):>12}")
    else:
        lines.append("No customer data available.")
    lines.append("")

    lines.append("DAILY SALES TREND")
    lines.append("-" * 44)
    lines.append(f"{'Date':<12}{'Revenue':>14}{'Transactions':>14}{'Unique Customers':>18}")
    if daily_rows:
        for d, rev, cnt, uniq in daily_rows:
            lines.append(f"{d:<12}{money(rev):>14}{fmt_int(cnt):>14}{fmt_int(uniq):>18}")
    else:
        lines.append("No daily trend data available.")
    lines.append("")

    lines.append("PRODUCT PERFORMANCE ANALYSIS")
    lines.append("-" * 44)
    if best_selling[0]:
        lines.append(f"Best Selling Day: {best_selling[0]} | Revenue: {money(best_selling[1])} | Transactions: {fmt_int(best_selling[2])}")
    else:
        lines.append("Best Selling Day: N/A")

    if low_products:
        lines.append("")
        lines.append("Low Performing Products (Total Qty < 10)")
        lines.append(f"{'Product Name':<22}{'Qty':>8}{'Revenue':>14}")
        for pn, q, rev in low_products:
            lines.append(f"{pn[:22]:<22}{fmt_int(q):>8}{money(rev):>14}")
    else:
        lines.append("Low Performing Products: None")

    lines.append("")
    lines.append("Average Transaction Value per Region")
    if avg_region:
        for r, av in avg_region.items():
            lines.append(f"- {r}: {money(av)}")
    else:
        lines.append("No region averages available.")
    lines.append("")

    lines.append("API ENRICHMENT SUMMARY")
    lines.append("-" * 44)
    lines.append(f"Total records checked for enrichment: {fmt_int(total_enriched_attempt)}")
    lines.append(f"Successful enrichments:              {fmt_int(success_enriched)}")
    lines.append(f"Success rate:                       {fmt_pct(success_rate)}")
    lines.append("")
    lines.append("Products that couldn't be enriched:")
    if missing_products:
        for p in missing_products:
            lines.append(f"- {p}")
    else:
        lines.append("- None")
    lines.append("")

    report_text = "\n".join(lines)

    # ---------------- write output (valid open() usage) ----------------
    try:
        out_dir = os.path.dirname(output_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # NOTE: open() does NOT accept file= keyword. Use positional filename.
        with open(output_file, "w", encoding="utf-8", errors="replace", newline="\n") as f:
            f.write(report_text)

        print(f"Sales report generated successfully: {output_file}")
    except Exception as e:
        print(f"Failed to write report to '{output_file}': {e}")

    return report_text
