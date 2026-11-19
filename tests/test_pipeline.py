
import pandas as pd

from etl.transform import (
    flag_cancellations_and_writeoffs,
    convert_gbp_to_usd
)


# R2: Cancellation and Stock Write-off Test

def test_cancellation_and_stock_writeoff():

    df = pd.DataFrame({
        "Invoice": ["C536365", "536366", "536367", "536368"],
        "Quantity": [-2, -3, 5, 10]
    })

    result = flag_cancellations_and_writeoffs(df)

    assert result["Is_Cancellation"].tolist() == [
        True, False, False, False
    ]

    assert result["Is_Stock_Writeoff"].tolist() == [
        False, True, False, False
    ]


# R7: Currency Conversion Test

def test_gbp_to_usd_conversion():

    df = pd.DataFrame({
        "InvoiceDate": [
            "2011-12-09 10:00:00",
            "2011-12-10 10:00:00"
        ],
        "Gross_GBP": [100, 200]
    })

    result = convert_gbp_to_usd(df)

    # Both dates should receive a valid FX rate.
    assert result["FX_Rate"].notna().all()

    # Weekend date should use the most recent previous rate.
    friday_rate = result.iloc[0]["FX_Rate"]
    saturday_rate = result.iloc[1]["FX_Rate"]

    assert friday_rate == saturday_rate

    # USD revenue should equal GBP revenue multiplied by FX rate.
    assert result.iloc[0]["Gross_USD"] == (
        result.iloc[0]["Gross_GBP"] * result.iloc[0]["FX_Rate"]
    )
