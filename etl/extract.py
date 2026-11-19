import pandas as pd
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Original dataset path
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "online_retail_II.csv"


def extract_data():

    print("Reading original retail dataset...")

    df = pd.read_csv(
        RAW_DATA_PATH,
        header=None,
        skiprows=1
    )

    df.columns = [
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "Price",
        "Customer ID",
        "Country"
    ]

    print("Dataset extracted successfully!")
    print("Total rows:", len(df))
    print("Total columns:", len(df.columns))

    return df
