# transform.py
import re
import pandas as pd
from .skills_dict import SKILLS_DICT


def transform_data(df: pd.DataFrame) -> dict:
    print("\n--- Step 2: Transformation (T) ---")

    # -------------------------------------------------------------------------
    # T1: Clean column names
    # -------------------------------------------------------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    print("T1 complete: Column names cleaned.")
    print(f"  Columns: {df.columns.tolist()}")

    # -------------------------------------------------------------------------
    # T2: Parse salary range → salary_min (int) & salary_max (int)
    # -------------------------------------------------------------------------
    def _parse_salary(s: str) -> tuple:
        nums = re.findall(r"\d[\d,]*", str(s).replace(",", ""))
        if len(nums) >= 2:
            return int(nums[0]), int(nums[1])
        return None, None

    df["salary_text"] = df["salary_range"]
    df[["salary_min", "salary_max"]] = (
        df["salary_range"].apply(lambda x: pd.Series(_parse_salary(x)))
    )
    df.drop(columns=["salary_range"], inplace=True)
    print(f"T2 complete: Salary parsed. Min range: £{df['salary_min'].min():,} | Max range: £{df['salary_max'].max():,}")

    # -------------------------------------------------------------------------
    # T3: Normalise & explode skills using SKILLS_DICT
    # -------------------------------------------------------------------------
    def _normalise_skills(raw: str) -> list[dict]:
        results = []
        seen = set()
        for raw_skill in str(raw).split(","):
            raw_skill = raw_skill.strip()
            mapped = SKILLS_DICT.get(raw_skill, "NOT_FOUND")
            if mapped == "NOT_FOUND":
                # Genuinely not in dict — flag as unmapped
                if raw_skill not in seen:
                    results.append({
                        "skill_name":     raw_skill,
                        "skill_group":    "UNMAPPED",
                        "skill_type":     None,
                        "skill_category": "UNMAPPED — Review Required",
                    })
                    seen.add(raw_skill)
            elif mapped is None:
                # Intentionally excluded — skip silently
                pass
            else:
                # Valid mapping — process normally
                for entry in mapped:
                    key = entry["skill_name"]
                    if key not in seen:
                        results.append(entry)
                        seen.add(key)
        return results

    df["skills_normalised"] = df["required_skills"].apply(_normalise_skills)

    unmapped = [
        s["skill_name"]
        for skills in df["skills_normalised"]
        for s in skills
        if s["skill_category"] == "UNMAPPED — Review Required"
    ]
    print("T3 complete: Skills normalised via SKILLS_DICT.")
    if unmapped:
        print(f"  ⚠ {len(set(unmapped))} unmapped skill(s) flagged for review: {sorted(set(unmapped))}")
    else:
        print("  ✓ All skills mapped successfully.")

    # -------------------------------------------------------------------------
    # T4: Build DIM_Skill — deduplicated canonical skill table
    # -------------------------------------------------------------------------
    all_skills = [s for skills in df["skills_normalised"] for s in skills]
    dim_skill = (
        pd.DataFrame(all_skills)
        .drop_duplicates(subset=["skill_name"])
        .reset_index(drop=True)
    )
    dim_skill.insert(0, "skill_id", range(1, len(dim_skill) + 1))

    # Ensure correct column order
    dim_skill = dim_skill[["skill_id", "skill_name", "skill_group", "skill_type", "skill_category"]]

    print(f"T4 complete: DIM_Skill built — {len(dim_skill)} unique skills across {dim_skill['skill_category'].nunique()} categories.")

    # -------------------------------------------------------------------------
    # T5: Build date dimension fields (UK financial year: April–March)
    # -------------------------------------------------------------------------
    df["date_posted"] = pd.to_datetime(df["date_posted"], dayfirst=True)

    dim_date = df["date_posted"].drop_duplicates().sort_values().reset_index(drop=True)
    dim_date = pd.DataFrame({"date": dim_date})
    dim_date["dateint"]          = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["dayinweek"]        = dim_date["date"].dt.dayofweek + 1
    dim_date["dayofmonth"]       = dim_date["date"].dt.day
    dim_date["dayofweekname"]    = dim_date["date"].dt.day_name()
    dim_date["finmonth"]         = dim_date["date"].dt.month
    dim_date["finquarternumber"] = dim_date["date"].apply(lambda d: ((d.month - 4) % 12) // 3 + 1)
    dim_date["finquarter"]       = "Q" + dim_date["finquarternumber"].astype(str)
    dim_date["finyear"]          = dim_date["date"].dt.year
    dim_date["date"]             = dim_date["date"].dt.date
    print(f"T5 complete: DIM_Date_Posted built — {len(dim_date)} unique dates ({dim_date['finyear'].min()}–{dim_date['finyear'].max()} FY).")

    # -------------------------------------------------------------------------
    # T6: Assign surrogate keys & build remaining dimension tables
    # -------------------------------------------------------------------------
    def _make_dim(series: pd.Series, id_col: str, val_col: str) -> pd.DataFrame:
        vals = series.drop_duplicates().reset_index(drop=True)
        return pd.DataFrame({id_col: range(1, len(vals) + 1), val_col: vals})

    dim_company   = _make_dim(df["company"],          "company_id",          "company_name")
    dim_job_title = _make_dim(df["job_title"],        "job_title_id",        "job_title")
    dim_job_type  = _make_dim(df["job_type"],         "job_type_id",         "job_type")
    dim_exp       = _make_dim(df["experience_level"], "experience_level_id", "experience_level")
    dim_industry  = _make_dim(df["industry"],         "industry_id",         "industry_name")

    cities = df["location"].drop_duplicates().reset_index(drop=True)

    def _map_nation(city: str) -> str:
        """
        Map city to UK nation.
        Extend this dict as new cities are added in future data loads.
        Any city not in the map defaults to England.
        """
        nation_map = {
            "Edinburgh": "Scotland",
            "Glasgow":   "Scotland",
            "Cardiff":   "Wales",
        }
        return nation_map.get(city, "England")

    dim_location = pd.DataFrame({
        "location_id": range(1, len(cities) + 1),
        "country":     cities.apply(_map_nation),
        "city":        cities,
    })

    print(
        f"T6 complete: Surrogate keys assigned.\n"
        f"  Companies: {len(dim_company)} | Titles: {len(dim_job_title)} | "
        f"Types: {len(dim_job_type)} | Experience levels: {len(dim_exp)} | "
        f"Industries: {len(dim_industry)} | Locations: {len(dim_location)}"
    )

    # -------------------------------------------------------------------------
    # T7: Build fact & bridge tables
    # -------------------------------------------------------------------------
    company_map = dim_company.set_index("company_name")["company_id"]
    title_map   = dim_job_title.set_index("job_title")["job_title_id"]
    type_map    = dim_job_type.set_index("job_type")["job_type_id"]
    exp_map     = dim_exp.set_index("experience_level")["experience_level_id"]
    loc_map     = dim_location.set_index("city")["location_id"]
    ind_map     = dim_industry.set_index("industry_name")["industry_id"]
    skill_map   = dim_skill.set_index("skill_name")["skill_id"]

    # FACT_Job_Posting
    fact_job = pd.DataFrame({
        "job_posting_id":      range(1, len(df) + 1),
        "company_id":          df["company"].map(company_map).values,
        "date_posted":         df["date_posted"].dt.date.values,
        "job_title_id":        df["job_title"].map(title_map).values,
        "job_type_id":         df["job_type"].map(type_map).values,
        "experience_level_id": df["experience_level"].map(exp_map).values,
        "salary_min":          df["salary_min"].values,
        "salary_max":          df["salary_max"].values,
        "salary_text":         df["salary_text"].values,
    })

    # FACT_Job_Skill (bridge — exploded)
    job_skill_rows = []
    for idx, row in df.iterrows():
        job_id = idx + 1
        for s in row["skills_normalised"]:
            sid = skill_map.get(s["skill_name"])
            if sid is not None:
                job_skill_rows.append({"job_posting_id": job_id, "skill_id": int(sid)})
    fact_job_skill = pd.DataFrame(job_skill_rows).drop_duplicates()

    # FACT_Job_Location (bridge)
    fact_job_location = pd.DataFrame({
        "job_posting_id": range(1, len(df) + 1),
        "location_id":    df["location"].map(loc_map).values,
    })

    # FACT_Company_Industry (bridge — deduped)
    co_ind_rows = []
    seen_pairs = set()
    for _, row in df.iterrows():
        cid = company_map.get(row["company"])
        iid = ind_map.get(row["industry"])
        if (cid, iid) not in seen_pairs:
            co_ind_rows.append({"company_id": int(cid), "industry_id": int(iid)})
            seen_pairs.add((cid, iid))
    fact_co_industry = pd.DataFrame(co_ind_rows)

    print(
        f"T7 complete: Fact & bridge tables built.\n"
        f"  FACT_Job_Posting: {len(fact_job)} rows\n"
        f"  FACT_Job_Skill:   {len(fact_job_skill)} rows\n"
        f"  FACT_Job_Location: {len(fact_job_location)} rows\n"
        f"  FACT_Company_Industry: {len(fact_co_industry)} rows"
    )

    print("\nAll transformation steps complete.\n")

    return {
        "dim_company":           dim_company,
        "dim_job_title":         dim_job_title,
        "dim_job_type":          dim_job_type,
        "dim_experience_level":  dim_exp,
        "dim_location":          dim_location,
        "dim_industry":          dim_industry,
        "dim_skill":             dim_skill,
        "dim_date_posted":       dim_date,
        "fact_job_posting":      fact_job,
        "fact_job_skill":        fact_job_skill,
        "fact_job_location":     fact_job_location,
        "fact_company_industry": fact_co_industry,
    }