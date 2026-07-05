from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data"

st.set_page_config(
    page_title="Product Line Profitability & Margin Performance Analysis",
    layout="wide",
)

st.title("Product Line Profitability & Margin Performance Analysis")
st.subheader("Nassau Candy Distributor")

st.write("Welcome to the Product Line Profitability & Margin Performance Analysis Dashboard.")

name = st.text_input("Enter your name")
if name:
    st.success(f"Welcome, {name}")

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find the data file at {DATA_PATH}")
    st.stop()

st.write("Dataset Preview")
st.dataframe(df)
# KPI Calculations
total_sales = df["Sales"].sum()
total_profit = df["Gross Profit"].sum()
total_units = df["Units"].sum()
gross_margin = (total_profit / total_sales) * 100

st.markdown("## Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Gross Profit", f"${total_profit:,.2f}")
col3.metric("Gross Margin", f"{gross_margin:.2f}%")
col4.metric("Total Units Sold", f"{int(total_units):,}")