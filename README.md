# Retail Sales Pipeline

## Project Overview

This project is about building a retail sales data pipeline using Python, Pandas, MySQL, SQLAlchemy and FastAPI.

The main goal was to clean the retail sales data, handle missing and incorrect values, convert GBP revenue into USD, and store the processed data in a MySQL database.

I also created APIs using FastAPI to get customer details, product sales and monthly business reports.

## Technologies Used

- Python
- Pandas
- MySQL
- SQLAlchemy
- FastAPI
- Uvicorn
- Pytest
- SQL

## Project Structure

```text
Retail_Sales_Pipeline/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── reference/
│
├── etl/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── database/
│   ├── connection.py
│   └── models.py
│
├── api/
│   └── main.py
│
├── tests/
│   └── test_pipeline.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── ASSUMPTIONS.md
└── RESULTS.md
```

## ETL Process

I divided the ETL process into three main parts.

### 1. Extract

- Read the original retail sales CSV file.
- Loaded the dataset using Pandas.
- Checked the total rows, columns and missing values.

### 2. Transform

I applied the following cleaning rules:

- Removed exact duplicate records.
- Identified cancellation invoices.
- Identified stock write-offs.
- Handled missing Customer IDs.
- Identified non-product items.
- Checked zero and negative prices.
- Calculated GBP revenue.
- Converted GBP revenue into USD.
- Mapped countries to their regions.

### 3. Load

- Created a MySQL database.
- Created customer, product, country and date dimension tables.
- Created a fact sales table.
- Loaded the processed records into MySQL.
- Stored invalid price records in the data quality issue table.

## Database Design

I used a star schema with the following tables:

| Table | Purpose |
|---|---|
| dim_customer | Stores customer information |
| dim_product | Stores product information |
| dim_country | Stores country and region information |
| dim_date | Stores date-related information |
| fact_sales | Stores sales transactions |
| data_quality_issue | Stores invalid data records |

## FastAPI Endpoints

I created the following five GET APIs:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Checks API and database connection |
| GET | `/customers/{customer_id}/summary` | Gets customer sales summary |
| GET | `/products/top` | Gets top-selling products for a month |
| GET | `/kpis/monthly` | Gets monthly sales KPIs |
| GET | `/data-quality/summary` | Gets data quality issue counts |

## How to Run the Project

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd Retail_Sales_Pipeline
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install required libraries

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Create a MySQL database named:

```sql
CREATE DATABASE retail_sales_db;
```

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=retail_sales_db
```

Update the password according to your MySQL setup.

Create the required database tables using the SQL table definitions provided with the project.

### 5. Run the ETL process

Make sure the raw dataset and reference CSV files are present in their respective folders.

Run the extraction and transformation steps according to the project scripts, save the processed CSV files, and then run:

```bash
python -m etl.load
```

### 6. Start FastAPI

```bash
uvicorn api.main:app --reload
```

### 7. Open API documentation

Open the following URL in your browser:

http://127.0.0.1:8000/docs

You can test all five API endpoints using Swagger UI.

## Run Tests

To run the project tests:

```bash
pytest -v
```

## Project Results

- Original records read: 1,067,371
- Duplicate records removed: 34,335
- Final records loaded into fact_sales: 1,033,031
- Unique products: 5,131
- Countries: 42
- Distinct invoices: 53,623
- Negative-price records saved as data quality issues: 5

For detailed revenue, top products and data quality results, see [RESULTS.md](RESULTS.md).

## Learning Outcomes

While building this project, I learned how to:

- Work with a large CSV dataset using Pandas.
- Apply data cleaning and validation rules.
- Convert currency using historical exchange rates.
- Design a star schema in MySQL.
- Connect Python with MySQL using SQLAlchemy.
- Create REST APIs using FastAPI.
- Write SQL queries for business reports.
- Test Python functions using Pytest.