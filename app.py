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

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")

divisions = sorted(df["Division"].dropna().unique())
regions = sorted(df["Region"].dropna().unique())

selected_divisions = st.sidebar.multiselect("Division", divisions, default=divisions)
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

filtered_df = df[
    df["Division"].isin(selected_divisions) & df["Region"].isin(selected_regions)
]

if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust filters.")
    st.stop()

st.write("Dataset Preview")
st.dataframe(filtered_df)

# ---------------- KPI CALCULATIONS ----------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()
gross_margin = (total_profit / total_sales) * 100 if total_sales else 0

st.markdown("## Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Gross Profit", f"${total_profit:,.2f}")
col3.metric("Gross Margin", f"{gross_margin:.2f}%")
col4.metric("Total Units Sold", f"{int(total_units):,}")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Product Profitability", "Divisional Performance", "Margin Risk"]
)

# ---- TAB 1: OVERVIEW ----
with tab1:
    st.markdown("### Sales & Profit Overview")
    overview_by_division = (
        filtered_df.groupby("Division")[["Sales", "Gross Profit"]].sum().reset_index()
    )
    st.bar_chart(overview_by_division.set_index("Division"))

    st.markdown("### Top 10 Products by Sales")
    top_products = (
        filtered_df.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(top_products)

# ---- TAB 2: PRODUCT PROFITABILITY ----
with tab2:
    st.markdown("### Product-wise Profitability")
    product_perf = (
        filtered_df.groupby("Product Name")[["Sales", "Gross Profit", "Units"]]
        .sum()
        .reset_index()
    )
    product_perf["Margin %"] = (
        product_perf["Gross Profit"] / product_perf["Sales"] * 100
    ).round(2)
    product_perf = product_perf.sort_values("Sales", ascending=False)

    st.dataframe(product_perf)

    st.markdown("### Top 10 Products by Gross Profit")
    top_profit_products = product_perf.set_index("Product Name")["Gross Profit"].head(10)
    st.bar_chart(top_profit_products)

# ---- TAB 3: DIVISIONAL PERFORMANCE ----
with tab3:
    st.markdown("### Performance by Division")
    division_perf = (
        filtered_df.groupby("Division")[["Sales", "Gross Profit", "Units"]]
        .sum()
        .reset_index()
    )
    division_perf["Margin %"] = (
        division_perf["Gross Profit"] / division_perf["Sales"] * 100
    ).round(2)
    st.dataframe(division_perf)

    st.markdown("### Sales Split by Division")
    st.bar_chart(division_perf.set_index("Division")["Sales"])

    st.markdown("### Performance by Region")
    region_perf = (
        filtered_df.groupby("Region")[["Sales", "Gross Profit", "Units"]]
        .sum()
        .reset_index()
    )
    st.dataframe(region_perf)
    st.bar_chart(region_perf.set_index("Region")["Sales"])

# ---- TAB 4: MARGIN RISK ----
with tab4:
    st.markdown("### Margin Risk Analysis")
    st.write(
        "Products with gross margin below 20% are flagged as high risk "
        "(low profitability relative to sales)."
    )

    product_perf_risk = (
        filtered_df.groupby("Product Name")[["Sales", "Gross Profit"]]
        .sum()
        .reset_index()
    )
    product_perf_risk["Margin %"] = (
        product_perf_risk["Gross Profit"] / product_perf_risk["Sales"] * 100
    ).round(2)

    risk_threshold = st.slider("Margin Risk Threshold (%)", 0, 50, 20)
    at_risk = product_perf_risk[product_perf_risk["Margin %"] < risk_threshold].sort_values(
        "Margin %"
    )

    st.write(f"Products below {risk_threshold}% margin: {len(at_risk)}")
    st.dataframe(at_risk)

    if not at_risk.empty:
        st.markdown("### Lowest Margin Products")
        st.bar_chart(at_risk.set_index("Product Name")["Margin %"])