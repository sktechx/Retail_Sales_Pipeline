# from fastapi import FastAPI
# from fastapi import FastAPI, HTTPException
# from sqlalchemy import text
# from database.connection import engine

# app = FastAPI(
#     title="Retail Sales Analytics API",
#     description="API for retail sales data and business analytics",
#     version="1.0.0"
# )

# @app.get("/health")
# def health_check():
#     return {
#         "status": "healthy",
#         "message": "Retail Sales API is running successfully"
#     }


# @app.get("/customers/{customer_id}/summary")
# def customer_summary(customer_id: str):

#     query = text("""
#         SELECT
#             c.customer_id,
#             COUNT(DISTINCT f.invoice) AS total_orders,
#             SUM(f.quantity) AS total_quantity,
#             SUM(
#                 CASE
#                     WHEN f.is_non_product = 0
#                     AND f.is_cancellation = 0
#                     AND f.is_stock_writeoff = 0
#                     THEN f.gross_gbp
#                     ELSE 0
#                 END
#             ) AS total_gbp,
#             SUM(
#                 CASE
#                     WHEN f.is_non_product = 0
#                     AND f.is_cancellation = 0
#                     AND f.is_stock_writeoff = 0
#                     THEN f.gross_usd
#                     ELSE 0
#                 END
#             ) AS total_usd

#         FROM dim_customer c
#         LEFT JOIN fact_sales f
#             ON c.customer_key = f.customer_key

#         WHERE c.customer_id = :customer_id
#         AND c.customer_id != 'CASH_SALES'

#         GROUP BY c.customer_id
#     """)

#     with engine.connect() as connection:
#         result = connection.execute(
#             query,
#             {"customer_id": customer_id}
#         ).mappings().first()

#     if result is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Customer not found"
#         )

#     return dict(result)











from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import text
from database.connection import engine
from datetime import datetime, date
from typing import Optional


app = FastAPI(
    title="Retail Sales Analytics API",
    description="API for Retail Sales Pipeline and Business Analytics",
    version="1.0.0"
)


# --------------------------------------------------
# 1. HEALTH CHECK API
# --------------------------------------------------

@app.get("/health")
def health_check():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "message": "Retail Sales API is running successfully"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )


# --------------------------------------------------
# 2. CUSTOMER SUMMARY API
# --------------------------------------------------

@app.get("/customers/{customer_id}/summary")
def customer_summary(customer_id: str):

    query = text("""
        SELECT
            c.customer_id,

            COUNT(DISTINCT f.invoice) AS total_orders,

            COALESCE(SUM(f.quantity), 0) AS total_quantity,

            COALESCE(SUM(
                CASE
                    WHEN f.is_non_product = 0
                    THEN f.gross_gbp
                    ELSE 0
                END
            ), 0) AS total_gbp,

            COALESCE(SUM(
                CASE
                    WHEN f.is_non_product = 0
                    THEN f.gross_usd
                    ELSE 0
                END
            ), 0) AS total_usd

        FROM dim_customer c

        LEFT JOIN fact_sales f
            ON c.customer_key = f.customer_key

        WHERE c.customer_id = :customer_id
        AND c.customer_id != 'CASH_SALES'

        GROUP BY c.customer_id
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return dict(result)


# --------------------------------------------------
# 3. TOP PRODUCTS API
# --------------------------------------------------

@app.get("/products/top")
def top_products(
    month: str,
    limit: int = Query(default=10, ge=1, le=100)
):

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid month format. Use YYYY-MM"
        )

    query = text("""
        SELECT
            p.stock_code,
            p.description,

            SUM(f.quantity) AS total_quantity,

            SUM(f.gross_gbp) AS total_gbp,

            SUM(f.gross_usd) AS total_usd

        FROM fact_sales f

        JOIN dim_product p
            ON f.product_key = p.product_key

        JOIN dim_date d
            ON f.date_key = d.date_key

        WHERE DATE_FORMAT(d.full_date, '%Y-%m') = :month

        AND f.is_non_product = 0
        AND f.is_cancellation = 0
        AND f.is_stock_writeoff = 0

        GROUP BY
            p.stock_code,
            p.description

        ORDER BY total_usd DESC

        LIMIT :limit
    """)

    with engine.connect() as connection:

        results = connection.execute(
            query,
            {
                "month": month,
                "limit": limit
            }
        ).mappings().all()

    return {
        "month": month,
        "limit": limit,
        "total_products": len(results),
        "products": [dict(row) for row in results]
    }


# --------------------------------------------------
# 4. MONTHLY KPI API
# --------------------------------------------------

@app.get("/kpis/monthly")
def monthly_kpis(
    start: str,
    end: str,
    region: Optional[str] = None
):

    try:
        start_date = datetime.strptime(start, "%Y-%m").date()
        end_date = datetime.strptime(end, "%Y-%m").date()

    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid date format. Use YYYY-MM"
        )

    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="Start month cannot be after end month"
        )

    query = text("""
        SELECT
            d.year,
            d.month,
            d.month_name,

            COUNT(DISTINCT f.invoice) AS total_orders,

            SUM(f.quantity) AS total_quantity,

            SUM(
                CASE
                    WHEN f.is_non_product = 0
                    THEN f.gross_gbp
                    ELSE 0
                END
            ) AS total_gbp,

            SUM(
                CASE
                    WHEN f.is_non_product = 0
                    THEN f.gross_usd
                    ELSE 0
                END
            ) AS total_usd

        FROM fact_sales f

        JOIN dim_date d
            ON f.date_key = d.date_key

        JOIN dim_country c
            ON f.country_key = c.country_key

        WHERE d.full_date >= :start_date
        AND d.full_date < :end_date_exclusive

        AND (
            :region IS NULL
            OR c.region = :region
        )

        GROUP BY
            d.year,
            d.month,
            d.month_name

        ORDER BY
            d.year,
            d.month
    """)

    # First day of month after the requested end month
    if end_date.month == 12:
        end_date_exclusive = date(end_date.year + 1, 1, 1)
    else:
        end_date_exclusive = date(
            end_date.year,
            end_date.month + 1,
            1
        )

    with engine.connect() as connection:

        results = connection.execute(
            query,
            {
                "start_date": start_date,
                "end_date_exclusive": end_date_exclusive,
                "region": region
            }
        ).mappings().all()

    return {
        "start": start,
        "end": end,
        "region": region,
        "monthly_kpis": [dict(row) for row in results]
    }


# --------------------------------------------------
# 5. DATA QUALITY SUMMARY API
# --------------------------------------------------

@app.get("/data-quality/summary")
def data_quality_summary():

    query = text("""
        SELECT
            rule_code,
            issue_description,
            COUNT(*) AS total_issues

        FROM data_quality_issue

        GROUP BY
            rule_code,
            issue_description

        ORDER BY rule_code
    """)

    total_query = text("""
        SELECT COUNT(*)
        FROM data_quality_issue
    """)

    with engine.connect() as connection:

        results = connection.execute(
            query
        ).mappings().all()

        total_issues = connection.execute(
            total_query
        ).scalar()

    return {
        "total_issues": total_issues,
        "issues_by_rule": [dict(row) for row in results]
    }
