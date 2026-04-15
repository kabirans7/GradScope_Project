import streamlit as st
import plotly.graph_objects as go
from backend.db_queries_roles import get_salary_by_role


def show(job_title: str, finyear: int | None = None):
    plotly_config = {"displayModeBar": False}

    df = get_salary_by_role(job_title, finyear=finyear)

    if df.empty:
        st.info(f"No salary data available for {job_title}.")
        return

    fig = go.Figure()
    fig.add_trace(go.Box(
        q1=[df["salary_min"].quantile(0.25)],
        median=[df["salary_mid"].median()],
        q3=[df["salary_max"].quantile(0.75)],
        lowerfence=[df["salary_min"].min()],
        upperfence=[df["salary_max"].max()],
        mean=[df["salary_mid"].mean()],
        y=[job_title],
        name=job_title,
        orientation="h",
        width=0.4,
        marker_color="#4C9BE8",
        boxmean=True,
        hovertemplate="Salary: £%{x:,.0f}<extra></extra>",
    ))

    x_min = df["salary_min"].min()
    x_max = df["salary_max"].max()
    x_pad = (x_max - x_min) * 0.15

    fig.update_layout(
        title=dict(text=f"Salary Distribution for {job_title}", x=0.5),
        xaxis_title="Salary (£)",
        yaxis_title="Job Role",
        height=350,
        showlegend=False,
        margin=dict(l=20, r=40, t=60, b=40),
        yaxis=dict(range=[-0.5, 0.5]),
        xaxis=dict(range=[x_min - x_pad, x_max + x_pad]),
    )

    st.plotly_chart(fig, use_container_width=True, config=plotly_config)