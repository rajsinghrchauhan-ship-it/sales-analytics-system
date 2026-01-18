# sales-analytics-system

**Student Name:** [RAJ SINGH CHAUHAN]
**Student ID:** [bitsom_ba_25071378]
**Email:** [raj.singh@msn.com]
**Date:** [18-Jan-2025]

## Project Overview
This project is a Python-based sales analytics pipeline that:
    Reads raw sales data from a pipe-delimited text file
    Cleans, validates, and filters transactions
    Performs analytical computations (revenue, regions, customers, trends)
    Fetches product metadata from an external API
    Enriches sales transactions with API product data
    Generates enriched data and a summary report
    The project is designed to work both as:
    A script-based pipeline (main.py)
    Modular, reusable components (utils/) - file_handler.py, data_processor.py, api_handler.py

## Repository structure

    sales-analytics-system/
│
├── main.py                     # Entry point (run this)
├── requirements.txt
├── README.md
│
├── data/
│   ├── sales_data.txt           # Input sales file
│   └── enriched_sales_data.txt  # Generated output
│
├── output/
│   └── sales_report.txt         # Final report
│
└── utils/
    ├── file_handler.py          # Read, parse, validate sales data
    ├── data_processor.py        # Analytics & aggregations
    ├── api_handler.py           # API fetch + enrichment logic
    └── generate_sales_report.py # Report generation

# Run the main file
    main.py

# The pipeline executes the following steps:

1. Reads sales data from data/sales_data.txt
2. Parses and cleans raw records
3. Validates transactions and removes invalid entries
4. (Optional) Applies region and amount filters via user input
5. Performs analytics:
    Total revenue
    Region-wise performance
    Top & low-performing products
    Customer insights
    Daily trends
6. Fetches product data from DummyJSON API
7. Enriches sales transactions with:
    Category
    Brand
    Rating
    API match flag
8. Saves enriched data to:
    data/enriched_sales_data.txt
9. Generates a summary report:
    output/sales_report.txt

# Output files

Enriched Sales Data -
    includes additional fields:
        API_Category
        API_Brand
        API_Rating
        API_Match

Sales Report -
    contains:
        Revenue summary
        Region-wise breakdown
        Customer insights
        Top and low-performing products

#   Design Highlights
    Modular architecture
    Clean separation of concerns
    Graceful error handling
    Cross-platform file handling
    Notebook logic successfully converted into a script-based pipeline
