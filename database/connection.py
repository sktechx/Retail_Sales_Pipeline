import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env
load_dotenv()

# Read MySQL credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Create MySQL database URL
#URL.create() password ke special characters ko safely handle karta h
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)

# Create database session
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base class for SQLAlchemy models
Base = declarative_base()

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT DATABASE()")
            )

            database_name = result.scalar()

            print("Database connected successfully!")
            print("Connected Database:", database_name)

    except Exception as e:
        print("Database connection failed!")
        print("Error:", e)