import streamlit as st
import plotly.express as px
from backend.db_queries_roles import get_experience_by_role


def show(job_title: str, finyear: int | None = None):
    plotly_config = {"displayModeBar": False}

    df = get_experience_by_role(job_title, finyear=finyear)

    if df.empty:
        st.info(f"No experience data available for {job_title}.")
        return

    df = df.sort_values("demand_count", ascending=True)

    fig = px.bar(
        df,
        x="demand_count",
        y="experience_level",
        orientation="h",
        labels={
            "experience_level": "Experience Level",
            "demand_count": "Number of Job Postings",
        },
        title=f"Experience Requirements for {job_title}",
        color="demand_count",
        color_continuous_scale="Greens",
    )

    fig.update_layout(
        title_x=0.5,
        xaxis_title="Number of Job Postings",
        yaxis_title="Experience Level",
        coloraxis_showscale=False,
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=60, b=40),
    )

    st.plotly_chart(fig, use_container_width=True, config=plotly_config)