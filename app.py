import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Sales Forecasting Dashboard",
    page_icon="📈",
    layout="wide"
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("📈 Sales Forecasting Dashboard")

st.markdown(
    """
    ### Predictive Analytics Using Historical Data

    This interactive dashboard analyzes historical sales data,
    evaluates a Linear Regression model, and forecasts sales for
    the next 12 months.
    """
)

st.divider()


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

@st.cache_data
def load_data():

    data = pd.read_csv("data/historical_sales.csv")

    data["Date"] = pd.to_datetime(data["Date"])

    data = data.sort_values("Date").reset_index(drop=True)

    data["Month_Number"] = np.arange(1, len(data) + 1)

    data["Year"] = data["Date"].dt.year

    data["Month"] = data["Date"].dt.month

    return data


df = load_data()


# ---------------------------------------------------------
# MODEL TRAINING
# ---------------------------------------------------------

features = [
    "Month_Number",
    "Year",
    "Month"
]

X = df[features]
y = df["Sales"]


split_index = int(len(df) * 0.8)


X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


model = LinearRegression()

model.fit(X_train, y_train)


# ---------------------------------------------------------
# MODEL EVALUATION
# ---------------------------------------------------------

y_pred = model.predict(X_test)


mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


# ---------------------------------------------------------
# FORECAST NEXT 12 MONTHS
# ---------------------------------------------------------

last_month_number = df["Month_Number"].max()

last_date = df["Date"].max()


future_dates = pd.date_range(
    start=last_date + pd.DateOffset(months=1),
    periods=12,
    freq="MS"
)


future_data = pd.DataFrame({
    "Date": future_dates
})


future_data["Month_Number"] = np.arange(
    last_month_number + 1,
    last_month_number + 13
)


future_data["Year"] = future_data["Date"].dt.year

future_data["Month"] = future_data["Date"].dt.month


future_features = future_data[
    features
]


future_data["Forecasted Sales"] = model.predict(
    future_features
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.header("Dashboard Controls")

show_forecast = st.sidebar.checkbox(
    "Show 12-Month Forecast",
    value=True
)

show_model = st.sidebar.checkbox(
    "Show Model Performance",
    value=True
)


# ---------------------------------------------------------
# KPI SECTION
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Historical Sales",
        f"{df['Sales'].sum():,.0f}"
    )


with col2:

    st.metric(
        "Average Monthly Sales",
        f"{df['Sales'].mean():,.0f}"
    )


with col3:

    st.metric(
        "Best Historical Month",
        f"{df['Sales'].max():,.0f}"
    )


with col4:

    st.metric(
        "Forecast Growth",
        f"{((future_data['Forecasted Sales'].iloc[-1] - future_data['Forecasted Sales'].iloc[0]) / future_data['Forecasted Sales'].iloc[0]) * 100:.2f}%"
    )


st.divider()


# ---------------------------------------------------------
# HISTORICAL SALES TREND
# ---------------------------------------------------------

st.subheader("📊 Historical Sales Trend")


fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(
    df["Date"],
    df["Sales"],
    marker="o"
)

ax.set_xlabel("Date")

ax.set_ylabel("Sales")

ax.set_title(
    "Monthly Historical Sales"
)

ax.grid(True)

plt.xticks(rotation=45)

plt.tight_layout()

st.pyplot(fig)


# ---------------------------------------------------------
# FORECAST SECTION
# ---------------------------------------------------------

if show_forecast:

    st.subheader("🔮 12-Month Sales Forecast")


    fig, ax = plt.subplots(figsize=(12, 5))


    ax.plot(
        df["Date"],
        df["Sales"],
        marker="o",
        label="Historical Sales"
    )


    ax.plot(
        future_data["Date"],
        future_data["Forecasted Sales"],
        marker="o",
        linestyle="--",
        label="Forecasted Sales"
    )


    ax.set_xlabel("Date")

    ax.set_ylabel("Sales")

    ax.set_title(
        "Historical Sales and Future Forecast"
    )

    ax.legend()

    ax.grid(True)

    plt.xticks(rotation=45)

    plt.tight_layout()

    st.pyplot(fig)


    st.dataframe(
        future_data[
            ["Date", "Forecasted Sales"]
        ].style.format({
            "Forecasted Sales": "{:,.2f}"
        }),
        use_container_width=True
    )


# ---------------------------------------------------------
# MODEL PERFORMANCE
# ---------------------------------------------------------

if show_model:

    st.subheader("🤖 Model Performance")


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "MAE",
            f"{mae:,.2f}"
        )


    with col2:

        st.metric(
            "RMSE",
            f"{rmse:,.2f}"
        )


    with col3:

        st.metric(
            "R² Score",
            f"{r2:.4f}"
        )


    st.info(
        "The model uses Month Number, Year, and Month as "
        "time-based features for sales prediction."
    )


# ---------------------------------------------------------
# ACTUAL VS PREDICTED
# ---------------------------------------------------------

st.subheader("🎯 Actual vs Predicted Sales")


prediction_results = pd.DataFrame({

    "Date": df.loc[X_test.index, "Date"],

    "Actual Sales": y_test.values,

    "Predicted Sales": y_pred

})


fig, ax = plt.subplots(figsize=(12, 5))


ax.plot(
    prediction_results["Date"],
    prediction_results["Actual Sales"],
    marker="o",
    label="Actual Sales"
)


ax.plot(
    prediction_results["Date"],
    prediction_results["Predicted Sales"],
    marker="o",
    linestyle="--",
    label="Predicted Sales"
)


ax.set_xlabel("Date")

ax.set_ylabel("Sales")

ax.set_title(
    "Actual vs Predicted Sales"
)

ax.legend()

ax.grid(True)

plt.xticks(rotation=45)

plt.tight_layout()

st.pyplot(fig)


# ---------------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------------

st.subheader("💡 Key Business Insights")


st.markdown(
    f"""
    - Historical sales demonstrate an overall **upward trend**.
    - Average monthly sales are approximately **{df['Sales'].mean():,.0f}**.
    - The highest historical monthly sales value is approximately
      **{df['Sales'].max():,.0f}**.
    - The model achieved an **R² score of {r2:.4f}** on the test data.
    - Forecasted sales show a continued upward trend over the
      next 12 months.
    - The forecast increases from approximately
      **{future_data['Forecasted Sales'].iloc[0]:,.0f}**
      to **{future_data['Forecasted Sales'].iloc[-1]:,.0f}**.
    """
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Predictive Analytics Using Historical Data | "
    "Thiranex Data Analytics Internship"
)