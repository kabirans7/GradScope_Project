import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from backend.db_queries_jobdemand import (
    get_sectors_by_demand,
    get_roles_within_sector,
    get_skills_within_sector,
    get_salary_within_sector,
)


# Use Case 8 — Sectors with High Graduate Hiring Demand
def show():
    plotly_config = {"displayModeBar": False}

    for key, default in [
        ("sectors_page", "overview"),
        ("selected_sector", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    # ---------------------------------------------------------------
    # Page 1 — Sectors ranked by demand
    # ---------------------------------------------------------------
    if st.session_state.sectors_page == "overview":

        col1, spacer = st.columns([1, 2])
        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="sectors_year")

        finyear = parse_year(selected_year)
        df = get_sectors_by_demand(finyear=finyear)

        if df.empty:
            st.warning("No sector data available.")
            return

        df = df.head(15).sort_values("demand_count", ascending=True)

        fig = px.bar(
            df,
            x="demand_count",
            y="industry_name",
            orientation="h",
            labels={
                "industry_name": "Industry Sector",
                "demand_count": "Number of Job Postings",
            },
            title="Sectors with High Hiring Demand",
            color="demand_count",
            color_continuous_scale="Blues",
        )

        fig.update_layout(
            title_x=0.5,
            xaxis_title="Number of Job Postings",
            yaxis_title="Industry Sector",
            coloraxis_showscale=False,
            showlegend=False,
            height=600,
            margin=dict(l=180, r=20, t=60, b=60),
            yaxis=dict(automargin=True, tickfont=dict(size=11)),
        )

        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Postings: %{x}<br><i>🔍 Click to explore deeper insights</i><extra></extra>",
        )

        event = st.plotly_chart(
            fig,
            on_select="rerun",
            key="sectors_chart",
            use_container_width=True,
            config=plotly_config,
        )

        if event and event.selection and event.selection.get("points"):
            st.session_state.selected_sector = event.selection["points"][0]["y"]
            st.session_state.sectors_page = "detail"
            st.rerun()

    # ---------------------------------------------------------------
    # Page 2 — Tabbed drill-down for selected sector
    # ---------------------------------------------------------------
    elif st.session_state.sectors_page == "detail":
        sector = st.session_state.selected_sector

        nav_col, col1, col2, spacer = st.columns([0.5, 1, 1, 1])
        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back", key="sectors_back"):
                st.session_state.sectors_page = "overview"
                st.session_state.selected_sector = None
                st.rerun()
        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="sector_detail_year")
        with col2:
            selected_view = st.selectbox("View", ["Roles", "Skills", "Salary"], key="sector_detail_view")

        finyear = parse_year(selected_year)

        st.markdown(f"### {sector}")
        st.markdown("---")

        if selected_view == "Roles":
            roles_df = get_roles_within_sector(sector, finyear=finyear)
            if not roles_df.empty:
                roles_df = roles_df.sort_values("demand_count", ascending=True)
                fig_roles = px.bar(
                    roles_df,
                    x="demand_count",
                    y="job_title",
                    orientation="h",
                    labels={"job_title": "Job Role", "demand_count": "Number of Job Postings"},
                    title=f"Roles Within {sector}",
                    color="demand_count",
                    color_continuous_scale="Blues",
                    range_color=[0, roles_df["demand_count"].max()],
                )
                fig_roles.update_layout(
                    title_x=0.5,
                    xaxis_title="Number of Job Postings",
                    yaxis_title="Job Role",
                    coloraxis_showscale=False,
                    showlegend=False,
                    height=500,
                    margin=dict(l=20, r=20, t=60, b=40),
                )
                st.plotly_chart(fig_roles, use_container_width=True, config=plotly_config)
            else:
                st.info(f"No role data available for {sector}.")

        elif selected_view == "Skills":
            skills_df = get_skills_within_sector(sector, finyear=finyear)
            if not skills_df.empty:
                skills_df = skills_df.sort_values("frequency", ascending=True)
                fig_skills = px.bar(
                    skills_df,
                    x="frequency",
                    y="skill_name",
                    orientation="h",
                    labels={"skill_name": "Skill", "frequency": "Number of Postings"},
                    title=f"Skills Required Within {sector}",
                    color="frequency",
                    color_continuous_scale=["#B8D4E8", "#6AAACD", "#1B3A6B"],
                    range_color=[0, skills_df["frequency"].max()],
                )
                fig_skills.update_layout(
                    title_x=0.5,
                    xaxis_title="Number of Postings",
                    yaxis_title="Skill",
                    coloraxis_showscale=False,
                    showlegend=False,
                    height=500,
                    margin=dict(l=20, r=20, t=60, b=40),
                )
                st.plotly_chart(fig_skills, use_container_width=True, config=plotly_config)
            else:
                st.info(f"No skill data available for {sector}.")

        elif selected_view == "Salary":
            salary_df = get_salary_within_sector(sector, finyear=finyear)
            if not salary_df.empty:
                fig_salary = go.Figure()
                fig_salary.add_trace(go.Box(
                    q1=[salary_df["salary_min"].quantile(0.25)],
                    median=[salary_df["salary_mid"].median()],
                    q3=[salary_df["salary_max"].quantile(0.75)],
                    lowerfence=[salary_df["salary_min"].min()],
                    upperfence=[salary_df["salary_max"].max()],
                    mean=[salary_df["salary_mid"].mean()],
                    y=[sector],
                    name=sector,
                    orientation="h",
                    width=0.4,
                    marker_color="#5B8DB8",
                    line=dict(color="#FFFFFF", width=1.5),
                    fillcolor="#4A74A6",
                    boxmean=False,
                    boxpoints=False,
                    hovertemplate=(
                        "Min: £%{lowerfence:,.0f}<br>"
                        "Q1: £%{q1:,.0f}<br>"
                        "Median: £%{median:,.0f}<br>"
                        "Q3: £%{q3:,.0f}<br>"
                        "Max: £%{upperfence:,.0f}"
                        "<extra></extra>"
                    ),
                ))
                x_min = salary_df["salary_min"].min()
                x_max = salary_df["salary_max"].max()
                x_pad = (x_max - x_min) * 0.30
                fig_salary.update_layout(
                    title=dict(text=f"Salary Distribution for {sector}", x=0.5),
                    xaxis_title="Salary (£)",
                    yaxis_title="Industry Sector",
                    height=400,
                    showlegend=False,
                    margin=dict(l=20, r=40, t=60, b=40),
                    yaxis=dict(range=[-0.5, 0.5]),
                    xaxis=dict(range=[x_min - x_pad, x_max + x_pad]),
                )
                st.plotly_chart(fig_salary, use_container_width=True, config=plotly_config)
            else:
                st.info(f"No salary data available for {sector}.")
