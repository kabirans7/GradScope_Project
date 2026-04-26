import streamlit as st
import plotly.graph_objects as go
from backend.db_queries_roles import get_salary_by_role


def show(job_title: str, finyear: int | None = None):
    plotly_config = {"displayModeBar": False}

    df = get_salary_by_role(job_title, finyear=finyear)

    if df.empty:
        st.info(f"No salary data available for {job_title}.")
        return

    q1     = df["salary_min"].quantile(0.25)
    median = df["salary_mid"].median()
    q3     = df["salary_max"].quantile(0.75)
    low    = df["salary_min"].min()
    high   = df["salary_max"].max()
    mean   = df["salary_mid"].mean()

    def fmt(val):
        return f"£{val/1000:.0f}k"

    fig = go.Figure()

    fig.add_trace(go.Box(
        q1=[q1],
        median=[median],
        q3=[q3],
        lowerfence=[low],
        upperfence=[high],
        mean=[mean],
        y=[job_title],
        name=job_title,
        orientation="h",
        width=0.4,
        marker_color="#5B8DB8",
        line=dict(color="#8FB3CF", width=1.5),
        fillcolor="#4A74A6",
        boxmean=False,
        customdata=[[fmt(low), fmt(q1), fmt(median), fmt(mean), fmt(q3), fmt(high)]],
        hovertemplate=(
            "<b>Min:</b> %{customdata[0]}<br>"
            "<b>Q1:</b> %{customdata[1]}<br>"
            "<b>Median:</b> %{customdata[2]}<br>"
            "<b>Mean:</b> %{customdata[3]}<br>"
            "<b>Q3:</b> %{customdata[4]}<br>"
            "<b>Max:</b> %{customdata[5]}"
            "<extra></extra>"
        ),
    ))

    x_min = low
    x_max = high
    x_pad = (x_max - x_min) * 0.15

    tick_step = 5000
    import math
    tick_start = math.floor(x_min / tick_step) * tick_step
    tick_end   = math.ceil(x_max / tick_step) * tick_step
    tick_vals  = list(range(int(tick_start), int(tick_end) + tick_step, tick_step))

    fig.update_layout(
        title=dict(text=f"Salary Distribution for {job_title}", x=0.5),
        xaxis_title="Salary (£)",
        yaxis_title="Job Role",
        height=350,
        showlegend=False,
        margin=dict(l=20, r=40, t=60, b=40),
        yaxis=dict(range=[-0.5, 0.5]),
        xaxis=dict(
            range=[x_min - x_pad, x_max + x_pad],
            tickvals=tick_vals,
            ticktext=[f"£{v // 1000}k" for v in tick_vals],
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config=plotly_config)
