import pandas as pd
import streamlit as st
import psycopg2
# from etl.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT #Grab Analytics DB


#Establish DB Connection
def get_connection():
    pg = st.secrets["postgres"]
    return psycopg2.connect(
        dbname=pg["database"],
        user=pg["user"],
        password=pg["password"],
        host=pg["host"],
        port=pg["port"],
        sslmode="require"
    )
    # return psycopg2.connect(
    #     dbname=DB_NAME,
    #     user=DB_USER,
    #     password=DB_PASSWORD,
    #     host=DB_HOST,
    #     port=DB_PORT
    # )

#First Level (Skill Categories)
def get_skill_categories(skill_type: str | None = None, finyear: int | None = None):
    sql = """
        SELECT
            s.skill_category,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Skill" fs
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "FACT_Job_Posting" jp ON fs.job_posting_id = jp.job_posting_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE (%s IS NULL OR s.skill_type = %s)
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY s.skill_category
        ORDER BY demand_count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(skill_type, skill_type, finyear, finyear))


#Second Level — Skills within a selected category
def get_skills_by_category(category: str, skill_type: str | None = None, finyear: int | None = None):
    sql = """
        SELECT
            COALESCE(s.skill_group, 'Other') AS skill_group,
            s.skill_name,
            s.skill_type,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Skill" fs
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "FACT_Job_Posting" jp ON fs.job_posting_id = jp.job_posting_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE s.skill_category = %s
          AND (%s IS NULL OR s.skill_type = %s)
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY
            COALESCE(s.skill_group, 'Other'),
            s.skill_name,
            s.skill_type
        ORDER BY skill_group ASC, demand_count DESC, s.skill_name ASC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(category, skill_type, skill_type, finyear, finyear))


#Third Level — Trend by month for a single skill, optionally filtered by year
def get_skill_trend(skill: str, skill_type: str | None = None, finyear: int | None = None):
    sql = """
        SELECT
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Skill" fs
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "FACT_Job_Posting" jp ON fs.job_posting_id = jp.job_posting_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE s.skill_name = %s
          AND (%s IS NULL OR s.skill_type = %s)
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY d.finmonth
        ORDER BY d.finmonth
    """
    with get_connection() as conn:
        df = pd.read_sql(sql, conn, params=(skill, skill_type, skill_type, finyear, finyear)) #Dataframe running SQL Query against DB for Python 

    # Convert month number to abbreviated name: e.g. 1 --> Jan, 2 --> Feb
    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finmonth"].astype(str).str.zfill(2), format="%m"
        ).dt.strftime("%b")
    return df