import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf


# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Global Gold Price Analytics",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align: center;'>🌍 Global Gold Price Analytics – Century View (1924–2024)</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: gray;'>Interactive Analysis of Gold Price Behavior Over 100 Years</p>",
    unsafe_allow_html=True
)

# ---------------------------
# DATA COLLECTION (FIXED)
# ---------------------------
@st.cache_data
def load_gold_data():
    gold = yf.download(
        "GC=F",
        start="1924-01-01",
        end="2024-12-31",
        auto_adjust=True,
        progress=False
    )

    # 🔧 FIX: flatten columns
    if isinstance(gold.columns, pd.MultiIndex):
        gold.columns = gold.columns.get_level_values(0)

    gold = gold.reset_index()
    gold["Year"] = gold["Date"].dt.year

    gold = (
        gold.groupby("Year", as_index=False)["Close"]
        .mean()
        .rename(columns={"Close": "Gold_Price_USD"})
    )

    return gold


@st.cache_data
def load_cpi_data():
    cpi = yf.download(
        "^CPI",
        start="1924-01-01",
        progress=False
    )

    if isinstance(cpi.columns, pd.MultiIndex):
        cpi.columns = cpi.columns.get_level_values(0)

    cpi = cpi.reset_index()
    cpi["Year"] = cpi["Date"].dt.year

    cpi = (
        cpi.groupby("Year", as_index=False)["Close"]
        .mean()
        .rename(columns={"Close": "CPI"})
    )

    return cpi



@st.cache_data
def load_usd_index():
    usd = yf.download(
        "DX-Y.NYB",
        start="1970-01-01",
        end="2024-12-31",
        auto_adjust=True,
        progress=False
    )

    # 🔧 FIX: flatten columns
    if isinstance(usd.columns, pd.MultiIndex):
        usd.columns = usd.columns.get_level_values(0)

    usd = usd.reset_index()
    usd["Year"] = usd["Date"].dt.year

    usd = (
        usd.groupby("Year", as_index=False)["Close"]
        .mean()
        .rename(columns={"Close": "USD_Index"})
    )

    return usd


# ---------------------------
# LOAD DATA
# ---------------------------
gold_df = load_gold_data()
cpi_df = load_cpi_data()
usd_df = load_usd_index()

# 🔧 MERGE (NOW SAFE)
df = gold_df.merge(cpi_df, on="Year", how="left")
df = df.merge(usd_df, on="Year", how="left")

# Yearly returns
df["Yearly_Return"] = df["Gold_Price_USD"].pct_change() * 100


st.sidebar.header("Controls")

start_year, end_year = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=(1924, 2024)
)

filtered_df = df[(df["Year"] >= start_year) & (df["Year"] <= end_year)]

col1, col2, col3, col4 = st.columns(4)

current_price = filtered_df.iloc[-1]["Gold_Price_USD"]
ath_price = df["Gold_Price_USD"].max()
years = end_year - start_year

cagr = (
    (current_price / filtered_df.iloc[0]["Gold_Price_USD"]) ** (1 / years) - 1
) * 100 if years > 0 else 0

col1.metric("Current Gold Price", f"${current_price:,.2f}")
col2.metric("All-Time High", f"${ath_price:,.2f}")
col3.metric("CAGR", f"{cagr:.2f}%")
col4.metric("Period", f"{years} Years")

st.divider()


fig1 = px.line(
    filtered_df,
    x="Year",
    y="Gold_Price_USD",
    title="Historical Gold Price Trend",
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

st.info("**Conclusion:** Gold shows a persistent long-term upward trend, confirming its role as a store of value.")


fig2 = px.bar(
    filtered_df,
    x="Year",
    y="Yearly_Return",
    title="Yearly Gold Returns (%)",
    template="plotly_dark"
)
st.plotly_chart(fig2, use_container_width=True)

st.info("**Conclusion:** Gold returns are volatile yearly, but downturns are often followed by recovery.")

fig3 = px.scatter(
    filtered_df,
    x="Year",
    y="Gold_Price_USD",
    size="Gold_Price_USD",
    title="Year-wise Gold Price Comparison",
    template="plotly_dark"
)
st.plotly_chart(fig3, use_container_width=True)

st.info("**Conclusion:** Price dominance in later decades highlights compounding growth.")


fig6 = px.histogram(
    filtered_df,
    x="Gold_Price_USD",
    nbins=30,
    title="Gold Price Distribution",
    template="plotly_dark"
)
st.plotly_chart(fig6, use_container_width=True)

st.info("**Conclusion:** Gold prices are right-skewed, showing long stability followed by sharp appreciation.")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown(
    "<p style='text-align:center; color:gray;'>Data Source: Yahoo Finance & FRED | Academic & Portfolio Use</p>",
    unsafe_allow_html=True
)
