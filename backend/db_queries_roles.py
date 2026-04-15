import pandas as pd
import psycopg2
from etl.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


# ---------------------------------------------------------------
# Use Case 3 — Emerging & Declining Roles
# ---------------------------------------------------------------

def get_emerging_declining_roles(finyear: int | None = None):
    # Use selected year vs previous year, or 2019 vs 2023 for All Time
    year_end = finyear if finyear else 2023
    year_start = year_end - 1 if finyear else 2019

    sql = f"""
        WITH counts AS (
            SELECT
                jt.job_title,
                SUM(CASE WHEN d.finyear = {year_start} THEN 1 ELSE 0 END) AS count_start,
                SUM(CASE WHEN d.finyear = {year_end} THEN 1 ELSE 0 END) AS count_end
            FROM "FACT_Job_Posting" jp
            JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
            JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
            WHERE d.finyear IN ({year_start}, {year_end})
            GROUP BY jt.job_title
        ),
        pct_change AS (
            SELECT
                job_title,
                count_start,
                count_end,
                CASE
                    WHEN count_start = 0 THEN 100.0
                    ELSE ROUND(((count_end - count_start) * 100.0 / count_start), 1)
                END AS pct_change
            FROM counts
            WHERE count_start > 0 OR count_end > 0
        )
        SELECT * FROM (
            SELECT job_title, count_start, count_end, pct_change FROM pct_change
            WHERE pct_change > 0
            ORDER BY pct_change DESC LIMIT 10
        ) emerging
        UNION ALL
        SELECT * FROM (
            SELECT job_title, count_start, count_end, pct_change FROM pct_change
            WHERE pct_change < 0
            ORDER BY pct_change ASC LIMIT 10
        ) declining
        ORDER BY pct_change DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn)


def get_role_trend(job_title: str, finyear: int | None = None):
    sql = """
        SELECT
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE jt.job_title = %s
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY d.finmonth
        ORDER BY d.finmonth
    """
    with get_connection() as conn:
        df = pd.read_sql(sql, conn, params=(job_title, finyear, finyear))

    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finmonth"].astype(str).str.zfill(2), format="%m"
        ).dt.strftime("%b")

    return df


# ---------------------------------------------------------------
# Use Case 4 — Career Options by Industry
# ---------------------------------------------------------------

def get_career_options(finyear: int | None = None):
    sql = """
        SELECT
            di.industry_name,
            jt.job_title,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE (%s IS NULL OR d.finyear = %s)
        GROUP BY di.industry_name, jt.job_title
        ORDER BY di.industry_name, demand_count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(finyear, finyear))


def get_roles_by_industry(industry_name: str, finyear: int | None = None):
    sql = """
        SELECT
            jt.job_title,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE di.industry_name = %s
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY jt.job_title
        ORDER BY demand_count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(industry_name, finyear, finyear))


# Use Case 4 Drill-Down — Salary by job role
def get_salary_by_role(job_title: str, finyear: int | None = None):
    sql = """
        SELECT
            jt.job_title,
            jp.salary_min,
            jp.salary_max,
            ((jp.salary_min + jp.salary_max) / 2.0) AS salary_mid
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE jt.job_title = %s
          AND jp.salary_min IS NOT NULL
          AND jp.salary_max IS NOT NULL
          AND (%s IS NULL OR d.finyear = %s)
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(job_title, finyear, finyear))


# Use Case 4 Drill-Down — Geographic distribution by job role
def get_geography_by_role(job_title: str, finyear: int | None = None, city: str | None = None):
    sql = """
        SELECT
            dl.country,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "FACT_Job_Location" fjl ON jp.job_posting_id = fjl.job_posting_id
        JOIN "DIM_Location" dl ON fjl.location_id = dl.location_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE jt.job_title = %s
          AND (%s IS NULL OR d.finyear = %s)
          AND (%s IS NULL OR dl.city = %s)
        GROUP BY dl.country
        ORDER BY demand_count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(job_title, finyear, finyear, city, city))


# Use Case 4 Drill-Down — Experience requirements by job role
def get_experience_by_role(job_title: str, finyear: int | None = None):
    sql = """
        SELECT
            el.experience_level,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Experience_Level" el ON jp.experience_level_id = el.experience_level_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE jt.job_title = %s
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY el.experience_level
        ORDER BY demand_count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(job_title, finyear, finyear))