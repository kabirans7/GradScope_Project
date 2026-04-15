import streamlit as st
import plotly.express as px
from backend.db_queries_employer import (
    get_active_employers,
    get_roles_by_company,
    get_skills_by_company,
)


# Use Case 5 - Active Employers
def show():
    plotly_config = {"displayModeBar": False}

    for key, default in [
        ("employers_page", "overview"),
        ("selected_company", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    # ---------------------------------------------------------------
    # Page 1 — Active Employers bar chart
    # ---------------------------------------------------------------
    if st.session_state.employers_page == "overview":

        col1, spacer = st.columns([1, 2])
        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="employers_year")

        finyear = parse_year(selected_year)
        df = get_active_employers(finyear=finyear)

        if df.empty:
            st.warning("No employer data available.")
            return

        df = df.sort_values("demand_count", ascending=True)

        fig = px.bar(
            df,
            x="demand_count",
            y="company_name",
            orientation="h",
            labels={
                "company_name": "Company",
                "demand_count": "Number of Job Postings",
            },
            title="Active Employers",
            color="demand_count",
            color_continuous_scale="Blues",
        )

        fig.update_layout(
            title_x=0.5,
            xaxis_title="Number of Job Postings",
            yaxis_title="Company",
            coloraxis_showscale=False,
            showlegend=False,
            height=600,
            margin=dict(l=20, r=20, t=60, b=60),
        )

        event = st.plotly_chart(
            fig,
            on_select="rerun",
            key="employers_chart",
            use_container_width=True,
            config=plotly_config,
        )

        if event and event.selection and event.selection.get("points"):
            st.session_state.selected_company = event.selection["points"][0]["y"]
            st.session_state.employers_page = "company_detail"
            st.rerun()

    # ---------------------------------------------------------------
    # Page 2 — Roles & Skills tabs for selected company
    # ---------------------------------------------------------------
    elif st.session_state.employers_page == "company_detail":
        company = st.session_state.selected_company

        nav_col, col1, spacer = st.columns([0.5, 1, 2])

        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back", key="employers_back"):
                st.session_state.employers_page = "overview"
                st.session_state.selected_company = None
                st.rerun()

        with col1:
            selected_year = st.selectbox(
                "Year", year_options, index=0, key="company_detail_year"
            )

        finyear = parse_year(selected_year)

        # Tabs
        tab1, tab2 = st.tabs(["Roles", "Skills"])

        # --- Tab 1: Roles ---
        with tab1:
            roles_df = get_roles_by_company(company, finyear=finyear)

            if roles_df.empty:
                st.warning(f"No role data available for {company}.")
            else:
                roles_df = roles_df.sort_values("demand_count", ascending=True)

                fig_roles = px.bar(
                    roles_df,
                    x="demand_count",
                    y="job_title",
                    orientation="h",
                    labels={
                        "job_title": "Job Role",
                        "demand_count": "Number of Job Postings",
                    },
                    title=f"Roles Offered by {company}",
                    color="demand_count",
                    color_continuous_scale="Blues",
                )

                fig_roles.update_layout(
                    title_x=0.5,
                    xaxis_title="Number of Job Postings",
                    yaxis_title="Job Role",
                    coloraxis_showscale=False,
                    showlegend=False,
                    height=500,
                    margin=dict(l=20, r=20, t=60, b=60),
                )

                st.plotly_chart(fig_roles, use_container_width=True, config=plotly_config)

        # --- Tab 2: Skills ---
        with tab2:
            skills_df = get_skills_by_company(company, finyear=finyear)

            if skills_df.empty:
                st.warning(f"No skill data available for {company}.")
            else:
                skills_df = skills_df.sort_values("demand_count", ascending=True)

                fig_skills = px.bar(
                    skills_df,
                    x="demand_count",
                    y="skill_name",
                    orientation="h",
                    labels={
                        "skill_name": "Skill Name",
                        "demand_count": "Number of Job Postings",
                    },
                    title=f"Required Skills Needed by {company}",
                    color="demand_count",
                    color_continuous_scale="Blues",
                )

                fig_skills.update_layout(
                    title_x=0.5,
                    xaxis_title="Number of Job Postings",
                    yaxis_title="Skill Name",
                    coloraxis_showscale=False,
                    showlegend=False,
                    height=500,
                    margin=dict(l=20, r=20, t=60, b=60),
                )

                st.plotly_chart(fig_skills, use_container_width=True, config=plotly_config)