import pandas as pd
import streamlit as st
from sqlalchemy import text
from backend.db import get_engine


def _query(sql: str, params: dict) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


@st.cache_data(ttl=600)
def get_trend_by_role(job_title: str, finyear: int | None = None):
    sql = """
        SELECT
            d.finyear,
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE jt.job_title = :job_title
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY d.finyear, d.finmonth
        ORDER BY d.finyear, d.finmonth
    """
    df = _query(sql, {"job_title": job_title, "finyear": finyear})
    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finyear"].astype(str) + "-" + df["finmonth"].astype(str).str.zfill(2) + "-01"
        ).dt.strftime("%b %Y")
    return df


@st.cache_data(ttl=600)
def get_trend_by_sector(industry_name: str, finyear: int | None = None):
    sql = """
        SELECT
            d.finyear,
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE di.industry_name = :industry_name
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY d.finyear, d.finmonth
        ORDER BY d.finyear, d.finmonth
    """
    df = _query(sql, {"industry_name": industry_name, "finyear": finyear})
    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finyear"].astype(str) + "-" + df["finmonth"].astype(str).str.zfill(2) + "-01"
        ).dt.strftime("%b %Y")
    return df


@st.cache_data(ttl=600)
def get_trend_by_location(city: str, finyear: int | None = None):
    sql = """
        SELECT
            d.finyear,
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Job_Location" fjl ON jp.job_posting_id = fjl.job_posting_id
        JOIN "DIM_Location" dl ON fjl.location_id = dl.location_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE dl.city = :city
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY d.finyear, d.finmonth
        ORDER BY d.finyear, d.finmonth
    """
    df = _query(sql, {"city": city, "finyear": finyear})
    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finyear"].astype(str) + "-" + df["finmonth"].astype(str).str.zfill(2) + "-01"
        ).dt.strftime("%b %Y")
    return df


@st.cache_data(ttl=3600)
def get_all_industries():
    sql = """SELECT DISTINCT industry_name FROM "DIM_Industry" ORDER BY industry_name"""
    return _query(sql, {})["industry_name"].tolist()


@st.cache_data(ttl=3600)
def get_all_cities():
    sql = """SELECT DISTINCT city FROM "DIM_Location" ORDER BY city"""
    return _query(sql, {})["city"].tolist()


@st.cache_data(ttl=3600)
def get_all_job_titles():
    sql = """SELECT DISTINCT job_title FROM "DIM_Job_Title" ORDER BY job_title"""
    return _query(sql, {})["job_title"].tolist()


@st.cache_data(ttl=600)
def get_monthly_postings(
    finyear: int | None = None,
    industry_name: str | None = None,
    city: str | None = None,
    job_title: str | None = None,
):
    sql = """
        SELECT
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        LEFT JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        LEFT JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        LEFT JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        LEFT JOIN "FACT_Job_Location" fjl ON jp.job_posting_id = fjl.job_posting_id
        LEFT JOIN "DIM_Location" dl ON fjl.location_id = dl.location_id
        WHERE (:finyear IS NULL OR d.finyear = :finyear)
          AND (:industry_name IS NULL OR di.industry_name = :industry_name)
          AND (:city IS NULL OR dl.city = :city)
          AND (:job_title IS NULL OR jt.job_title = :job_title)
        GROUP BY d.finmonth
        ORDER BY d.finmonth
    """
    df = _query(sql, {
        "finyear": finyear,
        "industry_name": industry_name,
        "city": city,
        "job_title": job_title,
    })
    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finmonth"].astype(str).str.zfill(2), format="%m"
        ).dt.strftime("%b")
    return df


@st.cache_data(ttl=600)
def get_sectors_by_demand(finyear: int | None = None):
    sql = """
        SELECT
            di.industry_name,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY di.industry_name
        ORDER BY demand_count DESC
    """
    return _query(sql, {"finyear": finyear})


@st.cache_data(ttl=600)
def get_roles_within_sector(industry_name: str, finyear: int | None = None):
    sql = """
        SELECT
            jt.job_title,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "DIM_Job_Title" jt ON jp.job_title_id = jt.job_title_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE di.industry_name = :industry_name
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY jt.job_title
        ORDER BY demand_count DESC
    """
    return _query(sql, {"industry_name": industry_name, "finyear": finyear})


@st.cache_data(ttl=600)
def get_skills_within_sector(industry_name: str, finyear: int | None = None):
    sql = """
        SELECT
            s.skill_name,
            COUNT(*) AS frequency
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "FACT_Job_Skill" fs ON jp.job_posting_id = fs.job_posting_id
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE di.industry_name = :industry_name
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY s.skill_name
        ORDER BY frequency DESC
        LIMIT 10
    """
    return _query(sql, {"industry_name": industry_name, "finyear": finyear})


@st.cache_data(ttl=600)
def get_salary_within_sector(industry_name: str, finyear: int | None = None):
    sql = """
        SELECT
            di.industry_name,
            jp.salary_min,
            jp.salary_max,
            ((jp.salary_min + jp.salary_max) / 2.0) AS salary_mid
        FROM "FACT_Job_Posting" jp
        JOIN "FACT_Company_Industry" fci ON jp.company_id = fci.company_id
        JOIN "DIM_Industry" di ON fci.industry_id = di.industry_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE di.industry_name = :industry_name
          AND jp.salary_min IS NOT NULL
          AND jp.salary_max IS NOT NULL
          AND (:finyear IS NULL OR d.finyear = :finyear)
    """
    return _query(sql, {"industry_name": industry_name, "finyear": finyear})
