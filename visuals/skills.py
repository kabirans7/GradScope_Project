import streamlit as st
import plotly.express as px
from backend.db_queries_skill import (
    get_skill_categories,
    get_skills_by_category,
    get_skill_trend,
)


def show():
    # Initialise session state
    for key, default in [
        ("skill_page", "category"),
        ("selected_category", None),
        ("selected_group", None),
        ("selected_skill", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    plotly_config = {"displayModeBar": False}

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    # ---------------------------------------------------------------
    # Page 1 — Skill Categories
    # ---------------------------------------------------------------
    if st.session_state.skill_page == "category":

        col1, spacer = st.columns([1, 2])
        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="cat_year")

        finyear = parse_year(selected_year)
        df = get_skill_categories(skill_type=None, finyear=finyear)

        if df.empty:
            st.warning("No skill category data available.")
            return

        fig = px.bar(
            df,
            x="skill_category",
            y="demand_count",
            color="skill_category",
            labels={
                "skill_category": "Skill Category",
                "demand_count": "Number of postings",
            },
            title="Technical & Soft Skills Demand",
        )

        fig.update_layout(
            showlegend=False,
            xaxis_tickangle=-30,
            xaxis_title="Skill Category",
            yaxis_title="Number of<br>postings",
            yaxis=dict(rangemode="tozero"),
            title_x=0.5,
            height=600,
            transition={"duration": 600, "easing": "cubic-in-out"},
        )

        fig.update_traces(
            marker=dict(line=dict(width=0)),
        )

        event = st.plotly_chart(
            fig,
            on_select="rerun",
            key="category_chart",
            use_container_width=True,
            config=plotly_config,
        )

        if event and event.selection and event.selection.get("points"):
            st.session_state.selected_category = event.selection["points"][0]["x"]
            st.session_state.selected_group = None
            st.session_state.selected_skill = None
            st.session_state.skill_page = "skills"
            st.rerun()

    # ---------------------------------------------------------------
    # Page 2 — Skills within a Category
    # ---------------------------------------------------------------
    elif st.session_state.skill_page == "skills":
        category = st.session_state.selected_category

        nav_col, col1, col2, col3 = st.columns([0.5, 1, 1, 1])

        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back"):
                st.session_state.skill_page = "category"
                st.session_state.selected_category = None
                st.session_state.selected_group = None
                st.session_state.selected_skill = None
                st.rerun()

        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="skills_year")

        df_all = get_skills_by_category(category, skill_type=None, finyear=None)
        if not df_all.empty:
            df_all["skill_group"] = df_all["skill_group"].fillna("Other")
        group_names = (
            ["All"] + df_all["skill_group"].dropna().unique().tolist()
            if not df_all.empty else ["All"]
        )

        with col2:
            selected_group_filter = st.selectbox(
                "Skill Group", group_names, index=0, key="skills_group_filter"
            )

        with col3:
            skill_type_options = ["All", "Technical", "Soft"]
            selected_skill_type_ui = st.selectbox(
                "Skill Type", skill_type_options, index=0, key="skills_type_filter"
            )

        skill_type_map = {"All": None, "Technical": "tech", "Soft": "soft"}
        selected_skill_type = skill_type_map[selected_skill_type_ui]
        finyear = parse_year(selected_year)

        df = get_skills_by_category(category, skill_type=selected_skill_type, finyear=finyear)
        if not df.empty:
            df["skill_group"] = df["skill_group"].fillna("Other")

        if df.empty:
            st.warning("No skills found for the selected filters.")
            return

        if selected_group_filter != "All":
            df = df[df["skill_group"] == selected_group_filter]

        group_df = df.head(10)

        if group_df.empty:
            st.warning("No skills available for the selected filters.")
            return

        fig = px.bar(
            group_df,
            x="skill_name",
            y="demand_count",
            color="skill_name",
            labels={
                "skill_name": "Skill",
                "demand_count": "Number of postings",
            },
            title="Technical & Soft Skills Demand",
        )

        fig.update_layout(
            showlegend=False,
            xaxis_tickangle=-30,
            xaxis_title="Skill",
            yaxis_title="Number of<br>postings",
            yaxis=dict(rangemode="tozero"),
            title_x=0.5,
            height=600,
            transition={"duration": 600, "easing": "cubic-in-out"},
        )

        fig.update_traces(
            marker=dict(line=dict(width=0)),
        )

        event = st.plotly_chart(
            fig,
            on_select="rerun",
            key="skills_chart",
            use_container_width=True,
            config=plotly_config,
        )

        if event and event.selection and event.selection.get("points"):
            st.session_state.selected_skill = event.selection["points"][0]["x"]
            st.session_state.skill_page = "trend"
            st.rerun()

    # ---------------------------------------------------------------
    # Page 3 — Demand Trend by Month for a single skill
    # ---------------------------------------------------------------
    elif st.session_state.skill_page == "trend":
        skill = st.session_state.selected_skill

        nav_col, col1, spacer = st.columns([0.5, 1, 2])

        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back"):
                st.session_state.skill_page = "skills"
                st.rerun()

        with col1:
            selected_year = st.selectbox(
                "Year", year_options, index=0, key="trend_year"
            )

        finyear = parse_year(selected_year)
        df = get_skill_trend(skill, skill_type=None, finyear=finyear)

        if df.empty:
            st.warning("No trend data available for this skill.")
            return

        fig = px.line(
            df,
            x="month_label",
            y="demand_count",
            markers=True,
            labels={
                "month_label": "Month",
                "demand_count": "Number of postings",
            },
            title=f"Demand Trends Over Time For {skill}",
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of<br>postings",
            yaxis=dict(rangemode="tozero"),
            xaxis=dict(tickangle=-30),
            title_x=0.5,
            transition={"duration": 600, "easing": "cubic-in-out"},
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=plotly_config,
        )