import json
import pandas as pd
from decimal import Decimal
from pathlib import Path

from database.connection import engine

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_PATH = (
    BASE_DIR / "data" / "processed" / "cleaned_retail_data.csv"
)


def load_processed_data():

    print("Reading cleaned retail dataset...")

    df = pd.read_csv(PROCESSED_DATA_PATH)

    print("Cleaned dataset loaded successfully!")
    print("Total rows:", len(df))
    print("Total columns:", len(df.columns))

    return df


def check_database_connection():

    try:
        with engine.connect() as connection:
            result = connection.exec_driver_sql(
                "SELECT DATABASE()"
            )

            print("Database connected successfully!")
            print("Database:", result.scalar())

    except Exception as e:
        print("Database connection failed!")
        print("Error:", e)


# if __name__ == "__main__":

#     df = load_processed_data()

#     check_database_connection()
#     load_customers(df)


from sqlalchemy import text


def load_customers(df):

    print("\nLoading customers...")

    customers = (
        df[["Customer ID"]]
        .drop_duplicates()
        .rename(columns={"Customer ID": "customer_id"})
    )

    # customers["customer_id"] = (
    #     customers["customer_id"].astype(str)
    # )
    customers["customer_id"] = customers["customer_id"].apply(
    lambda x: "CASH_SALES" if x == "CASH_SALES"
    else str(int(float(x)))
    )

    records = customers.to_dict(orient="records")

    insert_query = text("""
        INSERT INTO dim_customer (customer_id)
        VALUES (:customer_id)
        ON DUPLICATE KEY UPDATE
        customer_id = VALUES(customer_id)
    """)

    try:
        with engine.begin() as connection:

        # Clear previously inserted incorrect IDs
            connection.execute(
            text("DELETE FROM dim_customer")
        )

        # Insert corrected customer IDs
            connection.execute(insert_query, records)

        print("Customers loaded successfully!")
        print("Unique customer records:", len(records))

    except Exception as e:
        print("Customer loading failed!")
        print("Error:", e)


def load_products(df):

    print("\nLoading products...")

    products = df[["StockCode", "Description"]].copy()

    # Normalize StockCodes
    products["StockCode"] = (
        products["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Keep one record per normalized StockCode
    products = (
        products
        .drop_duplicates(subset=["StockCode"])
        .rename(columns={
            "StockCode": "stock_code",
            "Description": "description"
        })
    )

    # Handle missing descriptions
    products["description"] = (
        products["description"].fillna("Unknown")
    )

    records = products.to_dict(orient="records")

    insert_query = text("""
        INSERT INTO dim_product (stock_code, description)
        VALUES (:stock_code, :description)
        ON DUPLICATE KEY UPDATE
        description = VALUES(description)
    """)

    try:
        with engine.begin() as connection:

            # Safe because fact_sales has not been loaded yet
            connection.execute(
                text("DELETE FROM dim_product")
            )

            connection.execute(insert_query, records)

        print("Products loaded successfully!")
        print("Unique normalized products:", len(records))

    except Exception as e:
        print("Product loading failed!")
        print("Error:", e)


def load_countries(df):

    print("\nLoading countries...")

    countries = (
        df[["country_name", "region"]]
        .drop_duplicates(subset=["country_name"])
    )

    countries["country_name"] = (
        countries["country_name"].fillna("Unknown")
    )

    countries["region"] = (
        countries["region"].fillna("Unknown")
    )

    records = countries.to_dict(orient="records")

    insert_query = text("""
        INSERT INTO dim_country (country_name, region)
        VALUES (:country_name, :region)
        ON DUPLICATE KEY UPDATE
        region = VALUES(region)
    """)

    try:
        with engine.begin() as connection:

            connection.execute(
                text("DELETE FROM dim_country")
            )

            connection.execute(insert_query, records)

        print("Countries loaded successfully!")
        print("Unique countries:", len(records))

    except Exception as e:
        print("Country loading failed!")
        print("Error:", e)


def load_dates(df):

    print("\nLoading date dimension...")

    dates = pd.DataFrame()

    dates["full_date"] = (
        pd.to_datetime(df["InvoiceDate"])
        .dt.normalize()
        .drop_duplicates()
    )

    dates = dates.drop_duplicates().sort_values("full_date")

    dates["date_key"] = (
        dates["full_date"].dt.strftime("%Y%m%d").astype(int)
    )

    dates["day"] = dates["full_date"].dt.day
    dates["month"] = dates["full_date"].dt.month
    dates["month_name"] = dates["full_date"].dt.month_name()
    dates["quarter"] = dates["full_date"].dt.quarter
    dates["year"] = dates["full_date"].dt.year

    records = dates.to_dict(orient="records")

    insert_query = text("""
        INSERT INTO dim_date (
            date_key, full_date, day,
            month, month_name, quarter, year
        )
        VALUES (
            :date_key, :full_date, :day,
            :month, :month_name, :quarter, :year
        )
        ON DUPLICATE KEY UPDATE
            full_date = VALUES(full_date)
    """)

    try:
        with engine.begin() as connection:

            connection.execute(
                text("DELETE FROM dim_date")
            )

            connection.execute(insert_query, records)

        print("Dates loaded successfully!")
        print("Unique dates:", len(records))

    except Exception as e:
        print("Date loading failed!")
        print("Error:", e)



def load_fact_sales(df):

    print("\nLoading fact sales...")

    # Prepare a copy
    sales = df.copy()

    # Normalize customer IDs
    sales["customer_id"] = sales["Customer ID"].apply(
        lambda x: "CASH_SALES" if x == "CASH_SALES"
        else str(int(float(x)))
    )

    # Normalize product codes
    sales["stock_code"] = (
        sales["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Prepare transaction dates
    sales["transaction_date"] = (
        pd.to_datetime(sales["InvoiceDate"]).dt.date
    )

    # Prepare database insert query
    insert_query = text("""
        INSERT INTO fact_sales (
            invoice, customer_key, product_key,
            country_key, date_key, quantity,
            price_gbp, gross_gbp, fx_rate,
            fx_rate_date, gross_usd,
            is_cancellation, is_stock_writeoff,
            is_non_product, is_free_sample
        )
        VALUES (
            :invoice, :customer_key, :product_key,
            :country_key, :date_key, :quantity,
            :price_gbp, :gross_gbp, :fx_rate,
            :fx_rate_date, :gross_usd,
            :is_cancellation, :is_stock_writeoff,
            :is_non_product, :is_free_sample
        )
    """)

    chunk_size = 10000

    try:

        with engine.begin() as connection:

            # Fetch dimension key mappings
            customer_rows = connection.execute(
                text("""
                    SELECT customer_id, customer_key
                    FROM dim_customer
                """)
            ).mappings().all()

            product_rows = connection.execute(
                text("""
                    SELECT stock_code, product_key
                    FROM dim_product
                """)
            ).mappings().all()

            country_rows = connection.execute(
                text("""
                    SELECT country_name, country_key
                    FROM dim_country
                """)
            ).mappings().all()

            date_rows = connection.execute(
                text("""
                    SELECT full_date, date_key
                    FROM dim_date
                """)
            ).mappings().all()

            # Create lookup dictionaries
            customer_map = {
                row["customer_id"]: row["customer_key"]
                for row in customer_rows
            }

            product_map = {
                row["stock_code"]: row["product_key"]
                for row in product_rows
            }

            country_map = {
                row["country_name"]: row["country_key"]
                for row in country_rows
            }

            date_map = {
                row["full_date"]: row["date_key"]
                for row in date_rows
            }

            # Clear old fact records for reload
            connection.execute(
                text("DELETE FROM fact_sales")
            )

            total_inserted = 0

            # Process data in chunks
            for start in range(0, len(sales), chunk_size):

                chunk = sales.iloc[start:start + chunk_size].copy()

                # Map dimension keys
                chunk["customer_key"] = (
                    chunk["customer_id"].map(customer_map)
                )

                chunk["product_key"] = (
                    chunk["stock_code"].map(product_map)
                )

                chunk["country_key"] = (
                    chunk["country_name"].map(country_map)
                )

                chunk["date_key"] = (
                    chunk["transaction_date"].map(date_map)
                )

                # Validate foreign keys
                key_columns = [
                    "customer_key",
                    "product_key",
                    "country_key",
                    "date_key"
                ]

                missing_keys = chunk[key_columns].isna().sum()

                if missing_keys.sum() > 0:
                    raise ValueError(
                        f"Missing dimension keys:\n{missing_keys}"
                    )

                # Prepare records
                records = []

                columns = [
                    "Invoice", "customer_key", "product_key",
                    "country_key", "date_key", "Quantity",
                    "Price", "Gross_GBP", "FX_Rate",
                    "FX_Rate_Date", "Gross_USD",
                    "Is_Cancellation", "Is_Stock_Writeoff",
                    "Is_Non_Product", "Is_Free_Sample"
                ]

                for row in chunk[columns].itertuples(
                    index=False, name=None
                ):

                    (
                        invoice, customer_key, product_key,
                        country_key, date_key, quantity,
                        price, gross_gbp, fx_rate,
                        fx_rate_date, gross_usd,
                        cancellation, writeoff,
                        non_product, free_sample
                    ) = row

                    records.append({
                        "invoice": str(invoice),
                        "customer_key": int(customer_key),
                        "product_key": int(product_key),
                        "country_key": int(country_key),
                        "date_key": int(date_key),
                        "quantity": int(quantity),
                        "price_gbp": Decimal(str(price)),
                        "gross_gbp": Decimal(str(gross_gbp)),
                        "fx_rate": Decimal(str(fx_rate)),
                        "fx_rate_date": pd.Timestamp(
                            fx_rate_date
                        ).date(),
                        "gross_usd": Decimal(str(gross_usd)),
                        "is_cancellation": bool(cancellation),
                        "is_stock_writeoff": bool(writeoff),
                        "is_non_product": bool(non_product),
                        "is_free_sample": bool(free_sample)
                    })

                # Insert current chunk
                connection.execute(insert_query, records)

                total_inserted += len(records)

                print(
                    f"Inserted {total_inserted} / {len(sales)} rows"
                )

        print("\nFact sales loaded successfully!")
        print("Total fact records:", total_inserted)

    except Exception as e:

        print("\nFact sales loading failed!")
        print("Error:", e)

def load_data_quality_issues(invalid_price_df):
    print("\nLoading data quality issues...")

    if invalid_price_df.empty:
        print("No data quality issues found!")
        return

    records = []

    for _, row in invalid_price_df.iterrows():
        records.append({
            "invoice": str(row["Invoice"]),
            "stock_code": str(row["StockCode"]),
            "rule_code": "R5",
            "issue_description": "Negative Price",
            "issue_date": pd.to_datetime(row["InvoiceDate"]).to_pydatetime(),
            "original_data": json.dumps(row.to_dict(), default=str)
        })

    insert_query = text("""
        INSERT INTO data_quality_issue (
            invoice,
            stock_code,
            rule_code,
            issue_description,
            issue_date,
            original_data
        )
        VALUES (
            :invoice,
            :stock_code,
            :rule_code,
            :issue_description,
            :issue_date,
            :original_data
        )
    """)

    try:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM data_quality_issue")
            )
            connection.execute(insert_query, records)

        print("Data quality issues loaded successfully!")
        print("Total issues:", len(records))

    except Exception as e:
        print("Data quality issue loading failed!")
        print("Error:", e)


# if __name__ == "__main__":

#     df = load_processed_data()

#     check_database_connection()

#     load_customers(df)

#     load_products(df)

#     load_countries(df)

#     load_dates(df)

#     load_fact_sales(df)

if __name__ == "__main__":
    df = load_processed_data()

    invalid_price_path = (
        BASE_DIR / "data" / "processed" / "invalid_price_records.csv"
    )

    invalid_price_df = pd.read_csv(invalid_price_path)

    check_database_connection()

    load_customers(df)
    load_products(df)
    load_countries(df)
    load_dates(df)

    load_fact_sales(df)

    load_data_quality_issues(invalid_price_df)