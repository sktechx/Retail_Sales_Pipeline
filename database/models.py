from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    DateTime,
    DECIMAL,
    Boolean,
    Text,
    ForeignKey
)

from database.connection import Base


# 1. Customer Dimension
class Customer(Base):
    __tablename__ = "dim_customer"

    customer_key = Column(Integer,primary_key=True,autoincrement=True)
    customer_id = Column(String(50),unique=True)

# 2. Product Dimension
class Product(Base):
    __tablename__ = "dim_product"

    product_key = Column(Integer,primary_key=True,autoincrement=True)
    stock_code = Column(String(50),unique=True)
    description = Column(String(255))
    
# 3. Country Dimension
class Country(Base):

    __tablename__ = "dim_country"

    country_key = Column(Integer, primary_key=True, autoincrement=True)
    country_name = Column(String(100), unique=True)
    region = Column(String(100))


# 4. Date Dimension
class DateDimension(Base):

    __tablename__ = "dim_date"

    date_key = Column(Integer, primary_key=True)
    full_date = Column(Date, unique=True)
    day = Column(Integer)
    month = Column(Integer)
    month_name = Column(String(20))
    quarter = Column(Integer)
    year = Column(Integer)


# 5. Sales Fact Table
class FactSales(Base):

    __tablename__ = "fact_sales"

    sales_key = Column(BigInteger, primary_key=True, autoincrement=True)

    invoice = Column(String(30))

    customer_key = Column(Integer, ForeignKey("dim_customer.customer_key"))
    product_key = Column(Integer, ForeignKey("dim_product.product_key"))
    country_key = Column(Integer, ForeignKey("dim_country.country_key"))
    date_key = Column(Integer, ForeignKey("dim_date.date_key"))

    quantity = Column(Integer)
    price_gbp = Column(DECIMAL(12, 4))
    gross_gbp = Column(DECIMAL(15, 4))

    fx_rate = Column(DECIMAL(12, 6))
    fx_rate_date = Column(Date)
    gross_usd = Column(DECIMAL(15, 4))

    is_cancellation = Column(Boolean)
    is_stock_writeoff = Column(Boolean)
    is_non_product = Column(Boolean)
    is_free_sample = Column(Boolean)


# 6. Data Quality Issue Table
class DataQualityIssue(Base):

    __tablename__ = "data_quality_issue"

    issue_id = Column(BigInteger, primary_key=True, autoincrement=True)

    invoice = Column(String(30))
    stock_code = Column(String(50))
    rule_code = Column(String(10))
    issue_description = Column(String(255))
    issue_date = Column(DateTime)
    original_data = Column(Text)
