import streamlit as st
import plotly.express as px
import pandas as pd
from backend.db_queries_roles import get_geography_by_role

# Comprehensive UK city coordinates
# Add new cities here as data expands
CITY_COORDS = {
    "London":       {"lat": 51.5074, "lon": -0.1278},
    "Manchester":   {"lat": 53.4808, "lon": -2.2426},
    "Birmingham":   {"lat": 52.4862, "lon": -1.8904},
    "Leeds":        {"lat": 53.8008, "lon": -1.5491},
    "Bristol":      {"lat": 51.4545, "lon": -2.5879},
    "Newcastle":    {"lat": 54.9783, "lon": -1.6178},
    "Sheffield":    {"lat": 53.3811, "lon": -1.4701},
    "Liverpool":    {"lat": 53.4084, "lon": -2.9916},
    "Nottingham":   {"lat": 52.9548, "lon": -1.1581},
    "Edinburgh":    {"lat": 55.9533, "lon": -3.1883},
    "Glasgow":      {"lat": 55.8642, "lon": -4.2518},
    "Cardiff":      {"lat": 51.4816, "lon": -3.1791},
}

# Nation centre coordinates (used when no city filter applied)
NATION_COORDS = {
    "England":  {"lat": 52.8,  "lon": -1.2},
    "Scotland": {"lat": 56.8,  "lon": -4.2},
    "Wales":    {"lat": 52.3,  "lon": -3.8},
}


def show(job_title: str, finyear: int | None = None, nation: str | None = None, city: str | None = None):
    plotly_config = {"displayModeBar": False}

    df = get_geography_by_role(job_title, finyear=finyear, city=city)

    if df.empty:
        st.info(f"No geographic data available for {job_title}.")
        return

    # Apply nation filter if selected
    if nation and nation != "All":
        df = df[df["country"] == nation]

    # If city filter applied, show city-level data
    if city and city != "All":
        # Use city coordinates
        df["lat"] = df["country"].map(lambda x: CITY_COORDS.get(city, {}).get("lat"))
        df["lon"] = df["country"].map(lambda x: CITY_COORDS.get(city, {}).get("lon"))
        df["label"] = city
    else:
        # Aggregate to nation level
        all_nations = pd.DataFrame([
            {"country": "England",  "demand_count": 0},
            {"country": "Scotland", "demand_count": 0},
            {"country": "Wales",    "demand_count": 0},
        ])
        df = all_nations.merge(df, on="country", how="left", suffixes=("_default", ""))
        df["demand_count"] = df["demand_count"].fillna(df["demand_count_default"]).fillna(0).astype(int)
        df = df[["country", "demand_count"]]
        df["lat"] = df["country"].map(lambda x: NATION_COORDS.get(x, {}).get("lat"))
        df["lon"] = df["country"].map(lambda x: NATION_COORDS.get(x, {}).get("lon"))
        df["label"] = df["country"]

    # Categorise demand
    max_count = df["demand_count"].max()
    def categorise(val):
        if max_count == 0:
            return "No Data"
        pct = val / max_count
        if pct >= 0.66:
            return "High"
        elif pct >= 0.33:
            return "Medium"
        else:
            return "Low"

    df["Demand"] = df["demand_count"].apply(categorise)

    color_map = {
        "High":    "#922B21",
        "Medium":  "#E8B4B8",
        "Low":     "#D5D8DC",
        "No Data": "#EAECEE",
    }

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        size="demand_count",
        color="Demand",
        text="label",
        color_discrete_map=color_map,
        size_max=60,
        title=f"Geographic Distribution of {job_title}",
        hover_data={"demand_count": True, "lat": False, "lon": False},
        labels={"demand_count": "Job Postings"},
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(opacity=0.8, line=dict(width=1, color="white")),
    )

    fig.update_geos(
        scope="europe",
        resolution=50,
        showcoastlines=True,
        coastlinecolor="lightgrey",
        showland=True,
        landcolor="#1E2A3A",
        showocean=True,
        oceancolor="#0E1117",
        showframe=False,
        showcountries=True,
        countrycolor="grey",
        center={"lat": 54.5, "lon": -3.0},
        lonaxis_range=[-14, 6],
        lataxis_range=[48, 62],
    )

    fig.update_layout(
        title_x=0.5,
        height=600,
        width=700,
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(
            title="Demand Level",
            orientation="v",
            x=1.0,
            y=0.9,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        geo_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True, config=plotly_config)