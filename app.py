"""
KPI Sentiment Dashboard
------------------------
Streamlit + TextBlob + Plotly dashboard that analyzes customer review
sentiment and surfaces headline KPIs, trends, and breakdowns.

Run with:
    streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.sentiment import enrich_dataframe, compute_kpis

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Sentiment KPI Dashboard",
    page_icon="📊",
    layout="wide",
)

# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    return df


@st.cache_data
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    return enrich_dataframe(df, text_col="review")


st.title("📊 Customer Sentiment KPI Dashboard")
st.caption("Powered by TextBlob (sentiment) · Plotly (visuals) · Streamlit (UI)")

# --------------------------------------------------------------------------
# Sidebar: data source + filters
# --------------------------------------------------------------------------
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader(
    "Upload your own CSV (needs columns: date, review; optional: rating, product, customer)",
    type=["csv"],
)

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file, parse_dates=["date"])
else:
    raw_df = load_data("data/sample_reviews.csv")

df = process_data(raw_df)

st.sidebar.header("Filters")

min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if "product" in df.columns:
    products = sorted(df["product"].dropna().unique().tolist())
    selected_products = st.sidebar.multiselect("Product", products, default=products)
else:
    selected_products = None

sentiment_options = ["Positive", "Neutral", "Negative"]
selected_sentiments = st.sidebar.multiselect(
    "Sentiment", sentiment_options, default=sentiment_options
)

# Apply filters
mask = (df["date"] >= pd.to_datetime(date_range[0])) & (
    df["date"] <= pd.to_datetime(date_range[-1])
)
if selected_products is not None:
    mask &= df["product"].isin(selected_products)
mask &= df["sentiment"].isin(selected_sentiments)

filtered_df = df.loc[mask].copy()

# --------------------------------------------------------------------------
# KPI cards
# --------------------------------------------------------------------------
kpis = compute_kpis(filtered_df)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Reviews", kpis["total_reviews"])
k2.metric("Avg. Sentiment Polarity", kpis["avg_polarity"])
if kpis["avg_rating"] is not None:
    k3.metric("Avg. Rating", f"{kpis['avg_rating']} / 5")
else:
    k3.metric("Avg. Rating", "N/A")
k4.metric("% Positive", f"{kpis['pct_positive']}%")
k5.metric("% Negative", f"{kpis['pct_negative']}%")

st.divider()

# --------------------------------------------------------------------------
# Charts row 1: sentiment distribution + trend over time
# --------------------------------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Sentiment Distribution")
    if len(filtered_df):
        dist = filtered_df["sentiment"].value_counts().reindex(sentiment_options).fillna(0)
        fig_pie = px.pie(
            names=dist.index,
            values=dist.values,
            color=dist.index,
            color_discrete_map={
                "Positive": "#2ecc71",
                "Neutral": "#f1c40f",
                "Negative": "#e74c3c",
            },
            hole=0.45,
        )
        fig_pie.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

with col2:
    st.subheader("Sentiment Trend Over Time")
    if len(filtered_df):
        trend = (
            filtered_df.groupby([pd.Grouper(key="date", freq="D"), "sentiment"])
            .size()
            .reset_index(name="count")
        )
        fig_trend = px.line(
            trend,
            x="date",
            y="count",
            color="sentiment",
            markers=True,
            color_discrete_map={
                "Positive": "#2ecc71",
                "Neutral": "#f1c40f",
                "Negative": "#e74c3c",
            },
        )
        fig_trend.update_layout(legend_title_text="Sentiment", xaxis_title="Date", yaxis_title="Reviews")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

# --------------------------------------------------------------------------
# Charts row 2: polarity histogram + rating vs sentiment
# --------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Polarity Score Distribution")
    if len(filtered_df):
        fig_hist = px.histogram(
            filtered_df,
            x="polarity",
            nbins=20,
            color="sentiment",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Neutral": "#f1c40f",
                "Negative": "#e74c3c",
            },
        )
        fig_hist.update_layout(xaxis_title="Polarity (-1 to 1)", yaxis_title="Count")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

with col4:
    st.subheader("Average Rating by Product")
    if len(filtered_df) and "product" in filtered_df.columns and "rating" in filtered_df.columns:
        avg_rating = (
            filtered_df.groupby("product")["rating"].mean().sort_values(ascending=False).reset_index()
        )
        fig_bar = px.bar(
            avg_rating,
            x="product",
            y="rating",
            color="rating",
            color_continuous_scale="Blues",
            text_auto=".2f",
        )
        fig_bar.update_layout(xaxis_title="Product", yaxis_title="Avg. Rating", yaxis_range=[0, 5])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No product/rating data available for this chart.")

st.divider()

# --------------------------------------------------------------------------
# Gauge: overall sentiment health
# --------------------------------------------------------------------------
st.subheader("Overall Sentiment Health")
gauge_val = kpis["avg_polarity"] if kpis["total_reviews"] else 0
fig_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=gauge_val,
        number={"valueformat": ".2f"},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [-1, 1]},
            "bar": {"color": "#3498db"},
            "steps": [
                {"range": [-1, -0.05], "color": "#f5b7b1"},
                {"range": [-0.05, 0.05], "color": "#f9e79f"},
                {"range": [0.05, 1], "color": "#abebc6"},
            ],
        },
        title={"text": "Average Polarity (-1 Negative → +1 Positive)"},
    )
)
st.plotly_chart(fig_gauge, use_container_width=True)

# --------------------------------------------------------------------------
# Data table
# --------------------------------------------------------------------------
st.subheader("Review Detail")
display_cols = [c for c in ["date", "customer", "product", "rating", "review", "polarity", "subjectivity", "sentiment"] if c in filtered_df.columns]
st.dataframe(
    filtered_df[display_cols].sort_values("date", ascending=False),
    use_container_width=True,
    height=350,
)

csv_download = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download filtered data as CSV",
    data=csv_download,
    file_name="filtered_sentiment_data.csv",
    mime="text/csv",
)
