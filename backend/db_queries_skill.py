import pandas as pd
import streamlit as st
from sqlalchemy import text
from backend.db import get_engine


def _query(sql: str, params: dict) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


@st.cache_data(ttl=600)
def get_skill_categories(skill_type: str | None = None, finyear: int | None = None):
    sql = """
        SELECT
            s.skill_category,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Skill" fs
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "FACT_Job_Posting" jp ON fs.job_posting_id = jp.job_posting_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE (:skill_type IS NULL OR s.skill_type = :skill_type)
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY s.skill_category
        ORDER BY demand_count DESC
    """
    return _query(sql, {"skill_type": skill_type, "finyear": finyear})


@st.cache_data(ttl=600)
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
        WHERE s.skill_category = :category
          AND (:skill_type IS NULL OR s.skill_type = :skill_type)
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY
            COALESCE(s.skill_group, 'Other'),
            s.skill_name,
            s.skill_type
        ORDER BY skill_group ASC, demand_count DESC, s.skill_name ASC
    """
    return _query(sql, {"category": category, "skill_type": skill_type, "finyear": finyear})


@st.cache_data(ttl=600)
def get_skill_trend(skill: str, skill_type: str | None = None, finyear: int | None = None):
    sql = """
        SELECT
            d.finmonth,
            COUNT(*) AS demand_count
        FROM "FACT_Job_Skill" fs
        JOIN "DIM_Skill" s ON fs.skill_id = s.skill_id
        JOIN "FACT_Job_Posting" jp ON fs.job_posting_id = jp.job_posting_id
        JOIN "DIM_Date_Posted" d ON jp.date_posted = d.date
        WHERE s.skill_name = :skill
          AND (:skill_type IS NULL OR s.skill_type = :skill_type)
          AND (:finyear IS NULL OR d.finyear = :finyear)
        GROUP BY d.finmonth
        ORDER BY d.finmonth
    """
    df = _query(sql, {"skill": skill, "skill_type": skill_type, "finyear": finyear})
    if not df.empty:
        df["month_label"] = pd.to_datetime(
            df["finmonth"].astype(str).str.zfill(2), format="%m"
        ).dt.strftime("%b")
    return df
