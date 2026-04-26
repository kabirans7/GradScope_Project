import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from visuals.forecast import apply_forecast
from backend.db_queries_jobdemand import (
    get_trend_by_role,
    get_trend_by_sector,
    get_trend_by_location,
    get_monthly_postings,
    get_all_industries,
    get_all_cities,
    get_all_job_titles,
)


# Use Case 6 - Job Demand Trends Over Time
def show():
    plotly_config = {"displayModeBar": False}

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    def build_line_chart(df, title, x_col="month_label", y_col="demand_count",
                         color=None, show_forecast=False):
        """Helper to build a consistent line chart with optional forecast."""
        if df.empty:
            return None

        fig = px.line(
            df, x=x_col, y=y_col, markers=True,
            labels={x_col: "Time (Month-Year)", y_col: "Number of postings"},
            title=title,
        )
        if color:
            fig.update_traces(
                line=dict(color=color),
                marker=dict(
                    color=color,
                    size=12,
                    symbol="circle",
                    line=dict(width=0),
                ),
                name="Actual",
                showlegend=True,
            )

        fig.update_layout(
            title_x=0.5,
            xaxis_title="Time (Month-Year)",
            yaxis_title="Number of<br>postings",
            yaxis=dict(rangemode="tozero"),
            xaxis=dict(tickangle=-30),
            height=350,
            showlegend=True,
            legend=dict(orientation="h", x=0, y=1.1),
            margin=dict(l=20, r=20, t=80, b=60),
        )

        if show_forecast:
            fig = apply_forecast(fig, df, x_col=x_col, y_col=y_col, color=color)

        return fig

    # ---------------------------------------------------------------
    # Filters
    # ---------------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_year = st.selectbox("Year", year_options, index=0, key="trends_year")
    with col2:
        industries = ["All"] + get_all_industries()
        selected_sector = st.selectbox("Sector", industries, index=0, key="trends_sector")
    with col3:
        cities = ["All"] + get_all_cities()
        selected_city = st.selectbox("Location", cities, index=0, key="trends_location")
    with col4:
        roles = ["All"] + get_all_job_titles()
        selected_role = st.selectbox("Role", roles, index=0, key="trends_role")

    if selected_year == "All Time":
        show_forecast = st.toggle("Show Forecast", value=False, key="trends_forecast")
    else:
        show_forecast = False

    finyear = parse_year(selected_year)

    st.markdown("---")

    # ---------------------------------------------------------------
    # Chart 1 — Role trend
    # ---------------------------------------------------------------
    if selected_role != "All":
        df_role = get_trend_by_role(selected_role, finyear=finyear)
        fig = build_line_chart(
            df_role,
            title=f"Demand Over Time — {selected_role}",
            color="#4C9BE8",
            show_forecast=show_forecast,
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=plotly_config)
        else:
            st.info(f"No data available for role: {selected_role}")
    else:
        st.info("Select a Role to see its demand trend.")

    # ---------------------------------------------------------------
    # Chart 2 — Sector trend
    # ---------------------------------------------------------------
    if selected_sector != "All":
        df_sector = get_trend_by_sector(selected_sector, finyear=finyear)
        fig = build_line_chart(
            df_sector,
            title=f"Demand Over Time — {selected_sector} Sector",
            color="#F4A261",
            show_forecast=show_forecast,
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=plotly_config)
        else:
            st.info(f"No data available for sector: {selected_sector}")
    else:
        st.info("Select a Sector to see its demand trend.")

    # ---------------------------------------------------------------
    # Chart 3 — Location trend
    # ---------------------------------------------------------------
    if selected_city != "All":
        df_location = get_trend_by_location(selected_city, finyear=finyear)
        fig = build_line_chart(
            df_location,
            title=f"Demand Over Time — {selected_city}",
            color="#2A9D8F",
            show_forecast=show_forecast,
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True, config=plotly_config)
        else:
            st.info(f"No data available for location: {selected_city}")
    else:
        st.info("Select a Location to see its demand trend.")


# ---------------------------------------------------------------
# Use Case 7 — Total Number of Monthly Job Postings Over Time
# ---------------------------------------------------------------
def show_monthly():
    plotly_config = {"displayModeBar": False}

    fin_years = [2019, 2020, 2021, 2022, 2023]
    year_options = ["All Time"] + [str(y) for y in fin_years]

    def parse_year(selected: str) -> int | None:
        return None if selected == "All Time" else int(selected)

    col1, spacer = st.columns([1, 3])

    with col1:
        selected_year = st.selectbox("Year", [str(y) for y in fin_years], index=0, key="monthly_year")

    finyear = parse_year(selected_year)

    df = get_monthly_postings(finyear=finyear)

    if df.empty:
        st.warning("No data available for the selected filters.")
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
        title="Total Number of Monthly Job Postings Over Time",
    )

    fig.update_traces(
        line=dict(color="#56B4E9", width=2),
        marker=dict(
            color="#56B4E9",
            size=12,
            symbol="circle",
            line=dict(width=0),
        ),
    )

    fig.update_layout(
        title_x=0.5,
        xaxis_title="Month",
        yaxis_title="Number of<br>postings",
        yaxis=dict(rangemode="tozero"),
        height=500,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=60),
    )

    st.plotly_chart(fig, use_container_width=True, config=plotly_config)
