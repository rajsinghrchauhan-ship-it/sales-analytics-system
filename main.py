import os
import requests
from utils import file_handler, data_processor, api_handler,generate_sales_report

def main():
    """
    Main execution function
    """
    try:
        print("=" * 40)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 40)
        print()

        # ---------------- [1/10] Read sales data ----------------
        print("[1/10] Reading sales data...")
        sales_file = "data/sales_data.txt"  # change if your file name differs
        raw_lines = file_handler.read_sales_data(sales_file)
        print(f"✓ Successfully read {len(raw_lines)} transactions")
        print()

        # ---------------- [2/10] Parse and clean ----------------
        print("[2/10] Parsing and cleaning data...")
        parsed_transactions = file_handler.parse_transactions(raw_lines)
        print(f"✓ Parsed {len(parsed_transactions)} records")
        print()

        # ---------------- [3/10] Filter options ----------------
        print("[3/10] Filter Options Available:")

        # Available regions + amount range (from parsed data)
        regions = sorted({t.get("Region") for t in parsed_transactions if t.get("Region")})
        amounts = []
        for t in parsed_transactions:
            try:
                amounts.append(int(t["Quantity"]) * float(t["UnitPrice"]))
            except Exception:
                pass

        print("Regions:", ", ".join(regions) if regions else "N/A")
        if amounts:
            print(f"Amount Range: {money(min(amounts))} - {money(max(amounts))}")
        else:
            print("Amount Range: N/A")

        choice = input("\nDo you want to filter data? (y/n): ").strip().lower()

        region = None
        min_amount = None
        max_amount = None

        if choice == "y":
            region_in = input("Enter region (or press Enter to skip): ").strip()
            if region_in:
                region = region_in

            min_in = input("Enter min amount (or press Enter to skip): ").strip()
            if min_in:
                try:
                    min_amount = float(min_in.replace(",", ""))
                except ValueError:
                    print("⚠ Invalid min amount. Skipping min_amount filter.")

            max_in = input("Enter max amount (or press Enter to skip): ").strip()
            if max_in:
                try:
                    max_amount = float(max_in.replace(",", ""))
                except ValueError:
                    print("⚠ Invalid max amount. Skipping max_amount filter.")

        print()

        # ---------------- [4/10] Validate & filter ----------------
        print("[4/10] Validating transactions...")
        valid_transactions, invalid_count, summary = file_handler.validate_and_filter(
            parsed_transactions, region=region, min_amount=min_amount, max_amount=max_amount
        )
        print(f"✓ Valid: {len(valid_transactions)} | Invalid: {invalid_count}")
        print()

        # ---------------- [5/10] Analysis (Part 2) ----------------
        print("[5/10] Analyzing sales data...")

        total_rev = data_processor.calculate_total_revenue(valid_transactions)
        region_perf = data_processor.region_wise_sales(valid_transactions)
        top_products = data_processor.top_selling_products(valid_transactions, n=5)
        cust_stats = data_processor.customer_analysis(valid_transactions)
        daily_trend = data_processor.daily_sales_trend(valid_transactions)
        peak_day = data_processor.find_peak_sales_day(valid_transactions)
        low_products = data_processor.low_performing_products(valid_transactions, threshold=10)

        print("✓ Analysis complete")
        print()

        # ---------------- [6/10] Fetch API products ----------------
        print("[6/10] Fetching product data from API...")
        api_products = api_handler.fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products")
        print()

        # ---------------- [7/10] Enrich sales data ----------------
        print("[7/10] Enriching sales data...")
        product_map = api_handler.create_product_mapping(api_products)
        enriched_transactions = api_handler.enrich_sales_data(valid_transactions, product_map)

        enriched_success = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
        total_to_enrich = len(enriched_transactions)
        rate = (enriched_success / total_to_enrich * 100) if total_to_enrich else 0.0
        print(f"✓ Enriched {enriched_success}/{total_to_enrich} transactions ({rate:.1f}%)")
        print()

        # ---------------- [8/10] Save enriched data ----------------
        print("[8/10] Saving enriched data...")
        enriched_file = "data/enriched_sales_data.txt"
        if os.path.exists(enriched_file):
            print(f"✓ Saved to: {enriched_file}")
        else:
            # enrich_sales_data already tries to save; this is just a fallback status
            print("✓ Save attempted (check data/enriched_sales_data.txt)")
        print()

        # ---------------- [9/10] Generate report ----------------
        print("[9/10] Generating report...")
        report_file = "output/sales_report.txt"
        generate_sales_report.generate_sales_report(valid_transactions, enriched_transactions, output_file=report_file)
        print(f"✓ Report saved to: {report_file}")
        print()

        # ---------------- [10/10] Done ----------------
        print("[10/10] Process Complete!")
        print("=" * 40)
        print(f"Enriched data: {enriched_file}")
        print(f"Report:        {report_file}")
        print("=" * 40)

    except Exception as e:
        print("\n❌ Something went wrong, but the program did not crash.")
        print("Error:", e)


# Helper used in main for amount range formatting
def money(x):
    try:
        return f"₹{float(x):,.2f}"
    except Exception:
        return "₹0.00"


if __name__ == "__main__":
    main()
