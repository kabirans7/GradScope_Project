import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
from backend.db_queries_roles import (
    get_emerging_declining_roles,
    get_role_trend,
    get_career_options,
    get_roles_by_industry,
)
from visuals.salary import show as show_salary
from visuals.geography import show as show_geography
from visuals.experience import show as show_experience


# ---------------------------------------------------------------
# Use Case 3 — Emerging & Declining Roles
# ---------------------------------------------------------------
def show():
    plotly_config = {"displayModeBar": False}

    for key, default in [
        ("roles_page", "overview"),
        ("selected_role", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    # Page 1 — Emerging & Declining Roles overview
    if st.session_state.roles_page == "overview":

        col1, col2, spacer = st.columns([1, 1, 2])
        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="roles_year")
        with col2:
            status_options = ["All", "Growing", "Declining"]
            selected_status = st.selectbox("Status", status_options, index=0, key="roles_status")

        finyear = parse_year(selected_year)
        df = get_emerging_declining_roles(finyear=finyear)

        if df.empty:
            st.warning("No role data available.")
            return

        df["status"] = df["pct_change"].apply(lambda x: "Growing" if x >= 0 else "Declining")

        if selected_status != "All":
            df = df[df["status"] == selected_status]

        if df.empty:
            st.info(f"No {selected_status.lower()} roles found.")
            return

        df = df.sort_values("pct_change", ascending=True)
        colours = df["status"].map({"Growing": "#4C9BE8", "Declining": "#B0BEC5"}).tolist()

        x_min = df["pct_change"].min()
        x_max = df["pct_change"].max()
        x_pad_left = abs(x_min) * 0.45
        x_pad_right = abs(x_max) * 0.30

        # Build tick values in steps of 10
        import math
        tick_start = math.floor((x_min - x_pad_left) / 10) * 10
        tick_end = math.ceil((x_max + x_pad_right) / 10) * 10
        tick_vals = list(range(int(tick_start), int(tick_end) + 1, 10))

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=df["job_title"],
            x=df["pct_change"],
            orientation="h",
            marker=dict(color=colours, line=dict(width=0, color="rgba(0,0,0,0)")),
            text=df["pct_change"].apply(lambda x: f"{x:+.1f}%"),
            textposition="outside",
            textangle=0,
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>% Change: %{x:.1f}%<br><i>🔍 Click to explore deeper insights</i><extra></extra>",
            showlegend=False,
        ))

        fig.add_trace(go.Bar(
            y=[None], x=[None], orientation="h",
            marker=dict(color="#4C9BE8", line=dict(width=0)),
            name="Growing", showlegend=True,
        ))
        fig.add_trace(go.Bar(
            y=[None], x=[None], orientation="h",
            marker=dict(color="#B0BEC5", line=dict(width=0)),
            name="Declining", showlegend=True,
        ))

        fig.update_layout(
            title=dict(text="Growing & Declining Roles", x=0.5),
            xaxis=dict(
                title="% Change in Job Demand",
                zeroline=True,
                zerolinecolor="grey",
                zerolinewidth=2,
                range=[x_min - x_pad_left, x_max + x_pad_right],
                tickvals=tick_vals[::2],
                ticktext=[f"{v}%" for v in tick_vals[::2]],
                tickangle=-45,
            ),
            yaxis=dict(title="Job Roles"),
            legend=dict(orientation="v", x=1.02, y=1),
            height=600,
            margin=dict(l=20, r=20, t=60, b=60),
        )

        event = st.plotly_chart(
            fig, on_select="rerun", key="roles_chart",
            use_container_width=True, config=plotly_config,
        )

        if event and event.selection and event.selection.get("points"):
            st.session_state.selected_role = event.selection["points"][0]["y"]
            st.session_state.roles_page = "trend"
            st.rerun()

    # Page 2 — Demand trend for a single job role
    elif st.session_state.roles_page == "trend":
        role = st.session_state.selected_role

        nav_col, col1, spacer = st.columns([0.5, 1, 2])

        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back", key="roles_back"):
                st.session_state.roles_page = "overview"
                st.session_state.selected_role = None
                st.rerun()

        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="role_trend_year")

        finyear = parse_year(selected_year)
        df = get_role_trend(role, finyear=finyear)

        if df.empty:
            st.warning("No trend data available for this role.")
            return

        fig = px.line(
            df, x="month_label", y="demand_count", markers=True,
            labels={"month_label": "Month", "demand_count": "Number of postings"},
            title=f"Demand Trends Over Time For {role}",
        )

        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of<br>postings",
            yaxis=dict(rangemode="tozero"),
            xaxis=dict(tickangle=-30),
            title_x=0.5,
        )

        st.plotly_chart(fig, use_container_width=True, config=plotly_config)


# ---------------------------------------------------------------
# Use Case 4 — Career Options by Industry
# ---------------------------------------------------------------
def show_careers():
    plotly_config = {"displayModeBar": False}

    for key, default in [
        ("careers_page", "treemap"),
        ("selected_industry", None),
        ("selected_job_title", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    # ---------------------------------------------------------------
    # Page 1 — Bar chart: Job roles grouped by industry
    # ---------------------------------------------------------------
    if st.session_state.careers_page == "treemap":

        col1, col2 = st.columns([1, 1])
        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="careers_year")

        finyear = parse_year(selected_year)
        df = get_career_options(finyear=finyear)

        if df.empty:
            st.warning("No career data available.")
            return

        # Industry filter
        industries = ["All"] + sorted(df["industry_name"].dropna().unique().tolist())
        with col2:
            selected_industry = st.selectbox("Industry", industries, index=0, key="careers_industry")

        if selected_industry != "All":
            df = df[df["industry_name"] == selected_industry]

        # Top 20 roles by demand for readability
        df = df.sort_values("demand_count", ascending=True).tail(20)

        fig = px.bar(
            df,
            x="demand_count",
            y="job_title",
            color="industry_name",
            orientation="h",
            labels={
                "job_title": "Job Role",
                "demand_count": "Number of Postings",
                "industry_name": "Industry",
            },
            title="Career Options Related to Industry",
        )

        fig.update_layout(
            title_x=0.5,
            xaxis_title="Number of Postings",
            yaxis_title="Job Role",
            height=600,
            margin=dict(l=20, r=20, t=60, b=40),
            legend=dict(orientation="v", x=1.02, y=1),
        )

        event = st.plotly_chart(
            fig,
            on_select="rerun",
            key="careers_bar",
            use_container_width=True,
            config=plotly_config,
        )

        if event and event.selection and event.selection.get("points"):
            st.session_state.selected_job_title = event.selection["points"][0]["y"]
            st.session_state.careers_page = "job_detail"
            st.rerun()

    # ---------------------------------------------------------------
    # Page 2 — Bar chart: Job roles within selected industry
    # ---------------------------------------------------------------
    elif st.session_state.careers_page == "industry_roles":
        industry = st.session_state.selected_industry

        nav_col, col1, spacer = st.columns([0.5, 1, 2])

        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back", key="industry_back"):
                st.session_state.careers_page = "treemap"
                st.session_state.selected_industry = None
                st.rerun()

        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="industry_year")

        finyear = parse_year(selected_year)
        df = get_roles_by_industry(industry, finyear=finyear)

        if df.empty:
            st.warning(f"No role data available for {industry}.")
            return

        fig = px.bar(
            df,
            x="job_title",
            y="demand_count",
            color="job_title",
            labels={"job_title": "Job Role", "demand_count": "Number of postings"},
            title=f"Job Roles in {industry}",
        )

        fig.update_layout(
            showlegend=False,
            xaxis_tickangle=-30,
            xaxis_title="Job Role",
            yaxis_title="Number of<br>postings",
            yaxis=dict(rangemode="tozero"),
            title_x=0.5,
            height=600,
        )

        st.plotly_chart(fig, use_container_width=True, config=plotly_config)

    # ---------------------------------------------------------------
    # Page 3 — Salary, Geography & Experience tabs for selected job role
    # ---------------------------------------------------------------
    elif st.session_state.careers_page == "job_detail":
        job_title = st.session_state.selected_job_title

        nav_col, col1, col2, spacer = st.columns([0.5, 1, 1, 1])

        with nav_col:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("< Back", key="job_detail_back"):
                st.session_state.careers_page = "treemap"
                st.session_state.selected_job_title = None
                st.rerun()

        with col1:
            selected_year = st.selectbox("Year", year_options, index=0, key="job_detail_year")

        finyear = parse_year(selected_year)

        st.markdown(f"### {job_title}")

        # Three tabs for drill-down insights
        tab1, tab2, tab3 = st.tabs(["Salary", "Geographic", "Experience"])

        with tab1:
            show_salary(job_title, finyear=finyear)

        with tab2:
            # Location filters only shown in geographic tab
            nation_cities = {
                "England":  ["London", "Manchester", "Birmingham", "Leeds", "Bristol", "Newcastle", "Sheffield", "Liverpool", "Nottingham"],
                "Scotland": ["Edinburgh", "Glasgow"],
                "Wales":    ["Cardiff"],
            }
            geo_col1, geo_col2, geo_spacer = st.columns([1, 1, 2])
            with geo_col1:
                nations = ["All", "England", "Scotland", "Wales"]
                selected_nation = st.selectbox("Country", nations, index=0, key="job_detail_nation")
            if selected_nation == "All":
                city_options = ["All"] + sorted([c for cities in nation_cities.values() for c in cities])
            else:
                city_options = ["All"] + nation_cities.get(selected_nation, [])
            with geo_col2:
                selected_city = st.selectbox("City", city_options, index=0, key="job_detail_city")

            nation = None if selected_nation == "All" else selected_nation
            city = None if selected_city == "All" else selected_city

            col_l, col_m, col_r = st.columns([0.5, 2, 0.5])
            with col_m:
                show_geography(job_title, finyear=finyear, nation=nation, city=city)

        with tab3:
            show_experience(job_title, finyear=finyear)




# # ---------------------------------------------------------------
# # Use Case 4 — Career Options by Industry - This will be removed soon
# # ---------------------------------------------------------------
# def show_careers():
#     plotly_config = {"displayModeBar": False}

#     for key, default in [
#         ("careers_page", "treemap"),
#         ("selected_industry", None),
#         ("selected_job_title", None),
#     ]:
#         if key not in st.session_state:
#             st.session_state[key] = default

#     fin_years = [2019, 2020, 2021, 2022, 2023]
#     year_options = ["All Time"] + [str(y) for y in fin_years]

#     def parse_year(selected: str) -> int | None:
#         return None if selected == "All Time" else int(selected)

#     # ---------------------------------------------------------------
#     # Page 1 — Styled dataframe with progress column
#     # ---------------------------------------------------------------
#     if st.session_state.careers_page == "treemap":

#         col1, col2, spacer = st.columns([1, 1, 1])
#         with col1:
#             selected_year = st.selectbox("Year", year_options, index=0, key="careers_year")

#         finyear = parse_year(selected_year)
#         df = get_career_options(finyear=finyear)

#         if df.empty:
#             st.warning("No career data available.")
#             return

#         industries = ["All"] + sorted(df["industry_name"].dropna().unique().tolist())
#         with col2:
#             selected_industry = st.selectbox("Industry", industries, index=0, key="careers_industry")

#         roles = ["All"] + sorted(df["job_title"].dropna().unique().tolist())
#         with spacer:
#             selected_role_filter = st.selectbox("Job Role", roles, index=0, key="careers_role_filter")

#         if selected_industry != "All":
#             df = df[df["industry_name"] == selected_industry]

#         if selected_role_filter != "All":
#             df = df[df["job_title"] == selected_role_filter]

#         df_display = df[["industry_name", "job_title", "demand_count"]].rename(columns={
#             "industry_name": "Industry",
#             "job_title": "Job Role",
#             "demand_count": "Number of Postings",
#         }).sort_values("Number of Postings", ascending=False).reset_index(drop=True)

#         st.markdown("##### Career Options Related to Industry")
#         st.caption("🖱️ Click any row to explore salary, location and experience insights for that role.")

#         event = st.dataframe(
#             df_display,
#             use_container_width=True,
#             hide_index=True,
#             on_select="rerun",
#             selection_mode="single-row",
#             height=500,
#             column_config={
#                 "Industry": st.column_config.TextColumn("🏭 Industry", width="medium"),
#                 "Job Role": st.column_config.TextColumn("👔 Job Role", width="medium"),
#                 "Number of Postings": st.column_config.ProgressColumn(
#                     "📊 Demand",
#                     min_value=0,
#                     max_value=int(df_display["Number of Postings"].max()),
#                     format="%d",
#                     width="medium",
#                 ),
#             }
#         )

#         if event and event.selection and event.selection.get("rows"):
#             selected_row = event.selection["rows"][0]
#             st.session_state.selected_job_title = df_display.iloc[selected_row]["Job Role"]
#             st.session_state.selected_industry = df_display.iloc[selected_row]["Industry"]
#             st.session_state.careers_page = "job_detail"
#             st.rerun()

#     # ---------------------------------------------------------------
#     # Page 2 — Bar chart: Job roles within selected industry
#     # ---------------------------------------------------------------
#     elif st.session_state.careers_page == "industry_roles":
#         industry = st.session_state.selected_industry

#         nav_col, col1, spacer = st.columns([0.5, 1, 2])

#         with nav_col:
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("< Back", key="industry_back"):
#                 st.session_state.careers_page = "treemap"
#                 st.session_state.selected_industry = None
#                 st.rerun()

#         with col1:
#             selected_year = st.selectbox("Year", year_options, index=0, key="industry_year")

#         finyear = parse_year(selected_year)
#         df = get_roles_by_industry(industry, finyear=finyear)

#         if df.empty:
#             st.warning(f"No role data available for {industry}.")
#             return

#         fig = px.bar(
#             df,
#             x="job_title",
#             y="demand_count",
#             color="job_title",
#             labels={"job_title": "Job Role", "demand_count": "Number of postings"},
#             title=f"Job Roles in {industry}",
#         )

#         fig.update_layout(
#             showlegend=False,
#             xaxis_tickangle=-30,
#             xaxis_title="Job Role",
#             yaxis_title="Number of<br>postings",
#             yaxis=dict(rangemode="tozero"),
#             title_x=0.5,
#             height=600,
#         )

#         event = st.plotly_chart(
#             fig,
#             on_select="rerun",
#             key="industry_roles_chart",
#             use_container_width=True,
#             config=plotly_config,
#         )

#         if event and event.selection and event.selection.get("points"):
#             st.session_state.selected_job_title = event.selection["points"][0]["x"]
#             st.session_state.careers_page = "job_detail"
#             st.rerun()

#     # ---------------------------------------------------------------
#     # Page 3 — Salary, Geography & Experience tabs for selected job role
#     # ---------------------------------------------------------------
#     elif st.session_state.careers_page == "job_detail":
#         job_title = st.session_state.selected_job_title

#         nav_col, col1, col2, col3, spacer = st.columns([0.5, 1, 1, 1, 0.5])
#         with nav_col:
#             st.markdown("<br>", unsafe_allow_html=True)
#             if st.button("< Back", key="job_detail_back"):
#                 st.session_state.careers_page = "treemap"
#                 st.session_state.selected_job_title = None
#                 st.rerun()
#         with col1:
#             selected_year = st.selectbox("Year", year_options, index=0, key="job_detail_year")
#         with col2:
#             selected_view = st.selectbox("View", ["💰 Salary", "🗺️ Geographic", "📋 Experience"], key="job_detail_view")

#         finyear = parse_year(selected_year)

#         st.markdown(f"### {job_title}")
#         st.markdown("---")

#         if selected_view == "💰 Salary":
#             show_salary(job_title, finyear=finyear)

#         elif selected_view == "🗺️ Geographic":
#             nation_cities = {
#                 "England":  ["London", "Manchester", "Birmingham", "Leeds", "Bristol", "Newcastle", "Sheffield", "Liverpool", "Nottingham"],
#                 "Scotland": ["Edinburgh", "Glasgow"],
#                 "Wales":    ["Cardiff"],
#             }
#             geo_col1, geo_col2, geo_spacer = st.columns([1, 1, 2])
#             with geo_col1:
#                 nations = ["All", "England", "Scotland", "Wales"]
#                 selected_nation = st.selectbox("Country", nations, index=0, key="job_detail_nation")
#             if selected_nation == "All":
#                 city_options = ["All"] + sorted([c for cities in nation_cities.values() for c in cities])
#             else:
#                 city_options = ["All"] + nation_cities.get(selected_nation, [])
#             with geo_col2:
#                 selected_city = st.selectbox("City", city_options, index=0, key="job_detail_city")
#             nation = None if selected_nation == "All" else selected_nation
#             city = None if selected_city == "All" else selected_city
#             col_l, col_m, col_r = st.columns([0.5, 2, 0.5])
#             with col_m:
#                 show_geography(job_title, finyear=finyear, nation=nation, city=city)

#         elif selected_view == "📋 Experience":
#             show_experience(job_title, finyear=finyear)
