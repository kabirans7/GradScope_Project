import psycopg2
from .config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# Establish Connection to PostgreSQL DB
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        print(f"Successfully connected to PostgreSQL Database: {DB_NAME}")
        return conn

    except psycopg2.Error as e:
        print(f"DB Connection Failed. Error: {e}")
        print("Please check DB service and credentials.")
        raise