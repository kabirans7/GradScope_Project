import psycopg2
from psycopg2.extras import execute_values
from .db import get_connection
from .config import (
    FACT_JOB_POSTING_TABLE,
    DIM_COMPANY_TABLE,
    DIM_JOB_TITLE_TABLE,
    DIM_JOB_TYPE_TABLE,
    DIM_EXPERIENCE_LEVEL_TABLE,
    DIM_DATE_POSTED_TABLE,
    DIM_LOCATION_TABLE,
    DIM_INDUSTRY_TABLE,
    DIM_SKILL_TABLE,
    FACT_JOB_SKILL_TABLE,
    FACT_JOB_LOCATION_TABLE,
    FACT_COMPANY_INDUSTRY_TABLE,
)

#Execute values
def _execute_values(cursor, table: str, columns: list[str], rows: list[tuple]) -> None:
    """Bulk insert rows into table using execute_values for performance."""
    if not rows:
        print(f"No rows to insert into {table}, skipping.")
        return
    col_str = ", ".join(f'"{c}"' for c in columns)
    sql = f'INSERT INTO "{table}" ({col_str}) VALUES %s ON CONFLICT DO NOTHING'
    execute_values(cursor, sql, rows)


def _df_to_rows(df, columns: list[str]) -> list[tuple]:
    """Convert a DataFrame to a list of tuples for the given columns."""
    return [tuple(row) for row in df[columns].itertuples(index=False)]


#Load in the tables
#Dim Tables
def _load_dim_company(cursor, tables: dict) -> None:
    df = tables["dim_company"]
    cols = ["company_id", "company_name"]
    _execute_values(cursor, DIM_COMPANY_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_COMPANY_TABLE}: {len(df)} rows loaded.")


def _load_dim_job_title(cursor, tables: dict) -> None:
    df = tables["dim_job_title"]
    cols = ["job_title_id", "job_title"]
    _execute_values(cursor, DIM_JOB_TITLE_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_JOB_TITLE_TABLE}: {len(df)} rows loaded.")


def _load_dim_job_type(cursor, tables: dict) -> None:
    df = tables["dim_job_type"]
    cols = ["job_type_id", "job_type"]
    _execute_values(cursor, DIM_JOB_TYPE_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_JOB_TYPE_TABLE}: {len(df)} rows loaded.")


def _load_dim_experience_level(cursor, tables: dict) -> None:
    df = tables["dim_experience_level"]
    cols = ["experience_level_id", "experience_level"]
    _execute_values(cursor, DIM_EXPERIENCE_LEVEL_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_EXPERIENCE_LEVEL_TABLE}: {len(df)} rows loaded.")


def _load_dim_location(cursor, tables: dict) -> None:
    df = tables["dim_location"]
    cols = ["location_id", "country", "city"]
    _execute_values(cursor, DIM_LOCATION_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_LOCATION_TABLE}: {len(df)} rows loaded.")


def _load_dim_industry(cursor, tables: dict) -> None:
    df = tables["dim_industry"]
    cols = ["industry_id", "industry_name"]
    _execute_values(cursor, DIM_INDUSTRY_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_INDUSTRY_TABLE}: {len(df)} rows loaded.")


def _load_dim_skill(cursor, tables: dict) -> None:
    df = tables["dim_skill"]
    cols = ["skill_id", "skill_name", "skill_group", "skill_type", "skill_category"]
    _execute_values(cursor, DIM_SKILL_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_SKILL_TABLE}: {len(df)} rows loaded.")


def _load_dim_date_posted(cursor, tables: dict) -> None:
    df = tables["dim_date_posted"]
    cols = [
        "date", "dateint", "dayinweek", "dayofmonth", "dayofweekname",
        "finmonth", "finquarter", "finquarternumber", "finyear",
    ]
    _execute_values(cursor, DIM_DATE_POSTED_TABLE, cols, _df_to_rows(df, cols))
    print(f"{DIM_DATE_POSTED_TABLE}: {len(df)} rows loaded.")


#Main FACT table
def _load_fact_job_posting(cursor, tables: dict) -> None:
    df = tables["fact_job_posting"]
    cols = [
        "job_posting_id", "company_id", "date_posted", "job_title_id",
        "job_type_id", "experience_level_id", "salary_min", "salary_max", "salary_text",
    ]
    _execute_values(cursor, FACT_JOB_POSTING_TABLE, cols, _df_to_rows(df, cols))
    print(f"{FACT_JOB_POSTING_TABLE}: {len(df)} rows loaded.")


#Bridge Tables
def _load_fact_job_skill(cursor, tables: dict) -> None:
    df = tables["fact_job_skill"]
    cols = ["job_posting_id", "skill_id"]
    _execute_values(cursor, FACT_JOB_SKILL_TABLE, cols, _df_to_rows(df, cols))
    print(f"{FACT_JOB_SKILL_TABLE}: {len(df)} rows loaded.")


def _load_fact_job_location(cursor, tables: dict) -> None:
    df = tables["fact_job_location"]
    cols = ["job_posting_id", "location_id"]
    _execute_values(cursor, FACT_JOB_LOCATION_TABLE, cols, _df_to_rows(df, cols))
    print(f"{FACT_JOB_LOCATION_TABLE}: {len(df)} rows loaded.")


def _load_fact_company_industry(cursor, tables: dict) -> None:
    df = tables["fact_company_industry"]
    cols = ["company_id", "industry_id"]
    _execute_values(cursor, FACT_COMPANY_INDUSTRY_TABLE, cols, _df_to_rows(df, cols))
    print(f"{FACT_COMPANY_INDUSTRY_TABLE}: {len(df)} rows loaded.")


#Load Data
def load_data(tables: dict) -> None:
    """
    Loads all transformed tables into PostgreSQL in FK-safe order:
      1. All dimension tables first (no foreign key dependencies)
      2. FACT_Job_Posting (depends on all dims)
      3. Bridge/factless fact tables last (depend on FACT_Job_Posting)

    Uses a single transaction — rolls back everything if any step fails.
    """
    print("\nStep 3: Load (L)")

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                # DIM TABLES
                print("\n[1/3] Loading dimension tables...")
                _load_dim_company(cur, tables)
                _load_dim_job_title(cur, tables)
                _load_dim_job_type(cur, tables)
                _load_dim_experience_level(cur, tables)
                _load_dim_location(cur, tables)
                _load_dim_industry(cur, tables)
                _load_dim_skill(cur, tables)
                _load_dim_date_posted(cur, tables)

                # Main fact table
                print("\n[2/3] Loading fact table...")
                _load_fact_job_posting(cur, tables)

                # Bridge tables (depend on fact + dims)
                print("\n[3/3] Loading bridge tables...")
                _load_fact_job_skill(cur, tables)
                _load_fact_job_location(cur, tables)
                _load_fact_company_industry(cur, tables)

        print("\nAll tables loaded successfully. Transaction committed.\n")

    except psycopg2.Error as e:
        print(f"\nLoad failed: {e}")
        print("Transaction rolled back. No data was written to the database.")
        raise

    finally:
        conn.close()
        print("Database connection closed.")