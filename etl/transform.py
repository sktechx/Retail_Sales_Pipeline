# def remove_duplicates(df):

#     total_rows_before = len(df)

#     # Remove exact duplicate rows
#     df = df.drop_duplicates().copy()

#     # Calculate removed duplicate count
#     duplicates_removed = total_rows_before - len(df)

#     print("R1: Duplicate Removal")
#     print("Rows before:", total_rows_before)
#     print("Duplicates removed:", duplicates_removed)
#     print("Rows after:", len(df))

#     return df, duplicates_removed


# def flag_cancellations_and_writeoffs(df):

#     # Identify cancellation invoices
#     df["Is_Cancellation"] = (
#         df["Invoice"]
#         .astype(str)
#         .str.startswith("C", na=False)
#     )

#     # Identify negative quantity in normal invoices
#     df["Is_Stock_Writeoff"] = (
#         (df["Quantity"] < 0) &
#         (~df["Is_Cancellation"])
#     )

#     # Count cancellations
#     cancellation_count = df["Is_Cancellation"].sum()

#     # Count stock write-offs
#     writeoff_count = df["Is_Stock_Writeoff"].sum()

#     print("\nR2: Cancellation and Stock Write-off")

#     print("Cancellations:", cancellation_count)
#     print("Stock Write-offs:", writeoff_count)

#     return df


# def handle_missing_customers(df):

#     # Count missing customer IDs
#     cash_sales_count = df["Customer ID"].isna().sum()

#     # Replace missing IDs
#     df["Customer ID"] = (
#         df["Customer ID"].fillna("CASH_SALES")
#     )

#     print("\nR3: Cash Sales Handling")
#     print("Cash Sales Rows:", cash_sales_count)
#     print(
#         "Missing Customer IDs:",
#         df["Customer ID"].isna().sum()
#     )

#     return df
import pandas as pd
from pathlib import Path


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Reference files
REFERENCE_DIR = BASE_DIR / "data" / "reference"


# R1: Remove exact duplicates
def remove_duplicates(df):

    total_rows_before = len(df)

    df = df.drop_duplicates().copy()

    duplicates_removed = total_rows_before - len(df)

    print("\nR1: Duplicate Removal")
    print("Rows before:", total_rows_before)
    print("Duplicates removed:", duplicates_removed)
    print("Rows after:", len(df))

    return df, duplicates_removed


# R2: Cancellation and Stock Write-off
def flag_cancellations_and_writeoffs(df):

    df["Is_Cancellation"] = (
        df["Invoice"].astype(str).str.startswith("C", na=False)
    )

    df["Is_Stock_Writeoff"] = (
        (df["Quantity"] < 0) &
        (~df["Is_Cancellation"])
    )

    print("\nR2: Cancellation and Stock Write-off")
    print("Cancellations:", df["Is_Cancellation"].sum())
    print("Stock Write-offs:", df["Is_Stock_Writeoff"].sum())

    return df


# R3: Handle missing Customer IDs
def handle_missing_customers(df):

    cash_sales_count = df["Customer ID"].isna().sum()

    df["Customer ID"] = (
        df["Customer ID"].fillna("CASH_SALES")
    )

    print("\nR3: Cash Sales Handling")
    print("Cash Sales Rows:", cash_sales_count)
    print("Missing Customer IDs:", df["Customer ID"].isna().sum())

    return df


# R4: Identify non-product Stock Codes
def flag_non_products(df):

    non_product_path = REFERENCE_DIR / "non_product_codes.csv"

    non_product_df = pd.read_csv(non_product_path)

    non_product_codes = (
        non_product_df["stock_code"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
    )

    df["Is_Non_Product"] = (
        df["StockCode"]
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(non_product_codes)
    )

    print("\nR4: Non-Product Identification")
    print("Non-Product Rows:", df["Is_Non_Product"].sum())

    return df


# R5: Handle free samples and invalid prices
def handle_prices(df):

    df["Is_Free_Sample"] = df["Price"] == 0
    df["Is_Invalid_Price"] = df["Price"] < 0

    invalid_price_df = df[df["Is_Invalid_Price"]].copy()

    # Keep negative price records separately for quality logging
    invalid_price_df["Issue"] = "Negative Price"

    # Remove invalid price records from valid transactions
    df_valid = df[~df["Is_Invalid_Price"]].copy()

    print("\nR5: Price Validation")
    print("Free Samples:", df["Is_Free_Sample"].sum())
    print("Invalid Price Rows:", len(invalid_price_df))

    return df_valid, invalid_price_df


# R6: Calculate GBP revenue
def calculate_gbp_revenue(df):

    df["Gross_GBP"] = df["Quantity"] * df["Price"]

    print("\nR6: GBP Revenue Calculation")
    print("Gross GBP column created successfully")

    return df


# R7: Convert GBP to USD using latest prior FX rate
def convert_gbp_to_usd(df):

    fx_path = REFERENCE_DIR / "fx_rates_gbp_usd.csv"

    fx_df = pd.read_csv(fx_path)

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Invoice_Date"] = df["InvoiceDate"].dt.normalize()

    fx_df["rate_date"] = pd.to_datetime(fx_df["rate_date"])

    fx_df["from_currency"] = (
        fx_df["from_currency"].astype(str).str.upper()
    )

    fx_df["to_currency"] = (
        fx_df["to_currency"].astype(str).str.upper()
    )

    fx_rates = fx_df[
        (fx_df["from_currency"] == "GBP") &
        (fx_df["to_currency"] == "USD")
    ][["rate_date", "rate"]].copy()

    transactions = df.sort_values("Invoice_Date").copy()
    fx_rates = fx_rates.sort_values("rate_date")

    df = pd.merge_asof(
        transactions,
        fx_rates,
        left_on="Invoice_Date",
        right_on="rate_date",
        direction="backward"
    )

    df.rename(
        columns={
            "rate": "FX_Rate",
            "rate_date": "FX_Rate_Date"
        },
        inplace=True
    )

    df["Gross_USD"] = df["Gross_GBP"] * df["FX_Rate"]

    print("\nR7: Currency Conversion")
    print("Missing FX Rates:", df["FX_Rate"].isna().sum())
    print("Missing FX Dates:", df["FX_Rate_Date"].isna().sum())

    return df


# R8: Map countries to regions
def map_country_regions(df):

    country_path = REFERENCE_DIR / "country_region.csv"

    country_df = pd.read_csv(country_path)

    df = df.merge(
        country_df,
        left_on="Country",
        right_on="country_raw",
        how="left"
    )

    df["country_name"] = df["country_name"].fillna(df["Country"])
    df["region"] = df["region"].fillna("Unknown")

    print("\nR8: Country Region Mapping")
    print("Missing Regions:", df["region"].isna().sum())
    print("\nRegion Distribution:")
    print(df["region"].value_counts())

    return df


# Complete transformation pipeline
def transform_data(df):

    # R1
    df, duplicates_removed = remove_duplicates(df)

    # R2
    df = flag_cancellations_and_writeoffs(df)

    # R3
    df = handle_missing_customers(df)

    # R4
    df = flag_non_products(df)

    # R5
    df, invalid_price_df = handle_prices(df)

    # R6
    df = calculate_gbp_revenue(df)

    # R7
    df = convert_gbp_to_usd(df)

    # R8
    df = map_country_regions(df)

    print("\nTransformation completed successfully!")
    print("Final rows:", len(df))

    return df, duplicates_removed, invalid_price_df
