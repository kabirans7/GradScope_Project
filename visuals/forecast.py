import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LinearRegression


def apply_forecast(fig, df, x_col="month_label", y_col="demand_count", color=None):
    """
    Applies Linear Regression forecast to an existing Plotly figure.
    """
    if len(df) < 2:
        return fig

    X_train = np.arange(len(df)).reshape(-1, 1)
    y_train = df[y_col].values

    model = LinearRegression().fit(X_train, y_train)

    X_forecast = np.arange(len(df), len(df) + 12).reshape(-1, 1)
    predicted_demand = model.predict(X_forecast)
    predicted_demand = np.maximum(predicted_demand, 0)

    R_squared_score = model.score(X_train, y_train) * 100
    accuracy = "{0:.2f}".format(R_squared_score)

    last_date = pd.to_datetime(df[x_col].iloc[-1], format="%b %Y")
    future_labels = [
        (last_date + pd.DateOffset(months=i)).strftime("%b %Y")
        for i in range(1, 13)
    ]

    fig.add_trace(go.Scatter(
        x=future_labels,
        y=predicted_demand,
        mode="lines+markers",
        line=dict(dash="dash", color=color or "#4C9BE8"),
        marker=dict(size=8, color=color or "#4C9BE8", line=dict(width=0)),
        name=f"Forecast (R²: {accuracy}%)",
        showlegend=True,
    ))

    # Declutter x-axis — show every 3rd label only
    all_labels = list(df[x_col]) + future_labels
    tick_labels = [l if i % 3 == 0 else "" for i, l in enumerate(all_labels)]

    fig.update_layout(
        xaxis=dict(
            tickvals=all_labels,
            ticktext=tick_labels,
            tickangle=-30,
        )
    )

    return fig
