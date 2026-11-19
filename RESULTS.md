# Project Results

## 1. Dataset Summary

I started with 1,067,371 records from the original retail dataset.

After removing duplicate records and invalid prices, 1,033,031 records were loaded into the MySQL fact table.

| Description | Count |
|---|---:|
| Original records | 1,067,371 |
| Duplicate records removed | 34,335 |
| Records after duplicate removal | 1,033,036 |
| Invalid negative-price records | 5 |
| Final fact records | 1,033,031 |
| Distinct invoices | 53,623 |
| Customer records including CASH_SALES | 5,943 |
| Unique products | 5,131 |
| Countries | 42 |
| Unique transaction dates | 604 |

## 2. Data Cleaning Results

| Rule | Description | Count |
|---|---|---:|
| R1 | Duplicate records removed | 34,335 |
| R2 | Cancellation invoices | 19,104 |
| R2 | Stock write-offs | 3,393 |
| R3 | Missing Customer IDs handled | 235,151 |
| R4 | Non-product records identified | 5,674 |
| R5 | Free samples | 6,014 |
| R5 | Negative-price records rejected | 5 |
| R7 | Missing FX rates | 0 |
| R7 | Missing FX dates | 0 |
| R8 | Records mapped to Unknown region | 813 |

## 3. Total Revenue

Non-product items were excluded from these revenue calculations. Cancellation and stock write-off transactions were included as negative adjustments.

| Currency | Total Revenue |
|---|---:|
| GBP | £18,932,945.3570 |
| USD | $29,888,764.9728 |

## 4. December 2010 Revenue

| Currency | Revenue |
|---|---:|
| GBP | £758,167.0900 |
| USD | $1,188,446.6295 |

## 5. Top 5 Products in March 2011

Products were ranked according to USD revenue.

| Stock Code | Product | USD Revenue |
|---|---|---:|
| 22423 | REGENCY CAKESTAND 3 TIER | 27,178.9612 |
| 85099B | JUMBO BAG RED WHITE SPOTTY | 16,316.7336 |
| 47566 | PARTY BUNTING | 14,675.3496 |
| 85099F | JUMBO BAG STRAWBERRY | 9,431.8859 |
| 85123A | WHITE HANGING HEART T-LIGHT HOLDER | 8,958.8371 |

## 6. Data Quality Issues

The invalid negative-price records were saved in the `data_quality_issue` table.

| Rule Code | Issue | Count |
|---|---|---:|
| R5 | Negative Price | 5 |
| Total | | 5 |

## 7. Testing Results

I ran the tests using Pytest.

| Test | Result |
|---|---|
| Database connection | PASSED |
| Cancellation and stock write-off identification | PASSED |
| GBP to USD conversion | PASSED |

Total tests passed: 3.

## 8. Final Summary

The ETL pipeline successfully processed 1,067,371 original records and loaded 1,033,031 valid records into MySQL.

I created five FastAPI endpoints to access customer summaries, top products, monthly KPIs, API health and data quality information.

The project helped me understand how to clean a large dataset, work with a relational database, design a star schema and build APIs for business reporting.