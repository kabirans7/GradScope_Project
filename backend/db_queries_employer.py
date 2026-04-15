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


# Use Case 5 - Most Active Employers
def get_active_employers(finyear: int | None = None):
    sql = """
        SELECT
            dc.company_name,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Company" dc ON jp.company_id = dc.company_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE (%s IS NULL OR d.finyear = %s)
        GROUP BY dc.company_name
        ORDER BY demand_count DESC
        LIMIT 10
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(finyear, finyear))


# Use Case 5 Drill-Down - Roles offered by a specific company
def get_roles_by_company(company_name: str, finyear: int | None = None):
    sql = """
        SELECT
            jt.job_title,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Company" dc ON jp.company_id = dc.company_id
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE dc.company_name = %s
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY jt.job_title
        ORDER BY demand_count DESC
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(company_name, finyear, finyear))


# Use Case 5 Drill-Down - Skills required by a specific company
def get_skills_by_company(company_name: str, finyear: int | None = None):
    sql = """
        SELECT
            s.skill_name,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Company" dc ON jp.company_id = dc.company_id
        JOIN "FACT_Job_Skill" fs ON jp.job_posting_id = fs.job_posting_id
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE dc.company_name = %s
          AND (%s IS NULL OR d.finyear = %s)
        GROUP BY s.skill_name
        ORDER BY demand_count DESC
        LIMIT 10
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=(company_name, finyear, finyear))