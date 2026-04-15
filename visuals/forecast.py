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

    # Define X (month index) and y (demand count)
    X_train = np.arange(len(df)).reshape(-1, 1)
    y_train = df[y_col].values

    # Train Linear Regression Model
    model = LinearRegression().fit(X_train, y_train)

    # Predict in 12 months
    X_forecast = np.arange(len(df), len(df) + 12).reshape(-1, 1)
    predicted_demand = model.predict(X_forecast)
    predicted_demand = np.maximum(predicted_demand, 0)  # no negative postings

    # Compute R-squared accuracy
    R_squared_score = model.score(X_train, y_train) * 100
    accuracy = "{0:.2f}".format(R_squared_score)

    # Formulate model equation
    alpha = model.intercept_
    beta = model.coef_[0]
    sign = "-" if beta < 0 else "+"

    # Generate future month labels for next year
    last_date = pd.to_datetime(df[x_col].iloc[-1], format="%b %Y")
    future_labels = [
        (last_date + pd.DateOffset(months=i)).strftime("%b %Y")
        for i in range(1, 13)
    ]

    # Add dashed forecast trace
    fig.add_trace(go.Scatter(
        x=future_labels,
        y=predicted_demand,
        mode="lines+markers",
        line=dict(dash="dash", color=color or "#4C9BE8"),
        name=f"Forecast (R²: {accuracy}%)",
        showlegend=True,
    ))

    # Show model equation below chart
    st.caption(
        f"Linear Regression Model: ŷ = {alpha:.4f} {sign} {abs(beta):.4f}(month) "
        f"— R² Accuracy: {accuracy}%"
    )

    return fig