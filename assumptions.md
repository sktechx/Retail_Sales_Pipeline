# Assumptions

While working on this project, I followed these assumptions:

### 1. Duplicate Records
- Exact duplicate rows were removed from the dataset.
- Only one copy of each duplicate record was kept.

### 2. Invoice and Quantity
- Invoices starting with `C` were treated as cancelled invoices.
- Negative quantities on normal invoices were treated as stock write-offs.
- Both types of records were kept in the database with separate flags.

### 3. Customer Information
- Rows with missing Customer IDs were treated as cash sales.
- I used `CASH_SALES` as a common customer ID for these records.
- Cash sales were not included in individual customer reports.

### 4. Product Information
- I used the provided non-product codes file to identify non-product items.
- These records were kept in the database but excluded from product revenue calculations.

### 5. Price Validation
- Zero-price records were treated as free samples.
- Negative-price records were treated as invalid.
- Invalid records were not loaded into the sales fact table. They were saved in the data quality table for reference.

### 6. Currency Conversion
- GBP was used as the base currency.
- Revenue was calculated using Quantity × Price.
- I used the provided exchange rate file to convert GBP into USD.
- If an exchange rate was not available for a transaction date, I used the most recent previous available rate.

### 7. Country and Region
- I used the provided country mapping file.
- Countries without a matching region were assigned to `Unknown`.
- These records were not removed.

### 8. Revenue Calculation
- Non-product items were excluded from revenue reports.
- Cancellation and stock write-off records were retained as negative revenue adjustments.
- Free samples contributed zero revenue because their price was zero.

### 9. Database and API
- MySQL was used to store the processed data.
- SQLAlchemy was used for database connectivity.
- FastAPI was used to create APIs.
- SQL queries were used for calculations and reports instead of loading all records into Python.