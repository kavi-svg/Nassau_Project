from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data"

st.set_page_config(page_title="Nassau Candy", page_icon="🍬", layout="wide")

st.markdown(
    """
    <style>
    html, body, .stApp { background: #fdf7ef; color: #2d241d; }
    .main .block-container { padding-top: 0.2rem; padding-bottom: 2rem; }
    .top-banner { background: #2d241d; color: #fff; text-align: center; padding: 0.4rem 0; font-size: 0.9rem; }
    .top-nav { display: flex; justify-content: space-between; align-items: center; padding: 0.9rem 0.2rem 0.7rem; border-bottom: 1px solid #e6dcc8; }
    .brand { font-size: 1.35rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: #b21f2d; }
    .nav-links a { color: #2d241d; text-decoration: none; margin-left: 1rem; font-weight: 600; }
    .hero { background: linear-gradient(120deg, #ffffff 0%, #fff4e0 100%); border: 1px solid #e7dcc8; border-radius: 24px; padding: 1.3rem; margin: 1rem 0 1.2rem; box-shadow: 0 10px 25px rgba(45,36,29,0.06); }
    .hero h1 { font-size: 2.15rem; color: #2d241d; margin-bottom: 0.35rem; }
    .hero p { color: #635546; line-height: 1.5; }
    .hero-buttons a { display: inline-block; padding: 0.72rem 1rem; border-radius: 999px; text-decoration: none; font-weight: 700; margin-right: 0.6rem; background: #b21f2d; color: white; }
    .hero-buttons a.secondary { background: #f2b94b; color: #2d241d; }
    .section-card { background: white; border: 1px solid #eadbc3; border-radius: 16px; padding: 1rem; margin-bottom: 0.9rem; }
    .section-title { font-size: 1.15rem; font-weight: 800; color: #2d241d; margin: 1rem 0 0.55rem; }
    .product-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.8rem; }
    .product-card { background: #fff; border: 1px solid #eadbc3; border-radius: 14px; padding: 0.9rem; box-shadow: 0 4px 12px rgba(45,36,29,0.04); text-align: center; }
    .product-image-wrapper { margin-bottom: 0.85rem; border-radius: 14px; overflow: hidden; background: #f8f3ec; }
    .product-image { width: 100%; height: auto; object-fit: cover; display: block; }
    .product-price { color: #2d241d; font-weight: 700; margin-bottom: 0.55rem; }
    .product-card strong { color: #b21f2d; display: block; margin-bottom: 0.25rem; }
    .product-card .meta { color: #6d5d49; font-size: 0.95rem; margin-bottom: 0.2rem; }
    .metric-card { background: white; border: 1px solid #eadbc3; border-radius: 14px; padding: 0.9rem 1rem; margin-bottom: 0.6rem; }
    .footer { margin-top: 1.2rem; padding-top: 0.8rem; border-top: 1px solid #e6dcc8; color: #6d5d49; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="top-banner">Welcome to Nassau Candy</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="top-nav">
      <div class="brand">Nassau Candy</div>
      <div class="nav-links">
        <a href="#products">Products</a>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Bringing beloved candy and confections to every market.</h1>
      <p>From iconic sweets to wholesale solutions, Nassau Candy serves retailers, distributors, and specialty buyers with trusted quality and service.</p>
      <div class="hero-buttons">
        <a href="#products">Explore Products</a>
        <a href="#insights" class="secondary">View Insights</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find the data file at {DATA_PATH}")
    st.stop()

required_columns = {"Division", "Region", "Sales", "Gross Profit", "Units", "Product Name"}
missing = required_columns.difference(df.columns)
if missing:
    st.error(f"The dataset is missing required columns: {sorted(missing)}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    divisions = sorted(df["Division"].dropna().unique())
    regions = sorted(df["Region"].dropna().unique())
    selected_divisions = st.multiselect("Division", divisions, default=divisions)
    selected_regions = st.multiselect("Region", regions, default=regions)
    st.markdown("---")
    st.caption("Nassau Candy distributor analytics")

filtered_df = df[df["Division"].isin(selected_divisions) & df["Region"].isin(selected_regions)]
if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust filters.")
    st.stop()

st.markdown('<div id="products" class="section-title">Featured Products</div>', unsafe_allow_html=True)
product_perf = (
    filtered_df.groupby("Product Name")[["Sales", "Gross Profit", "Units"]]
    .sum()
    .reset_index()
)
product_perf["Average Price"] = (product_perf["Sales"] / product_perf["Units"]).round(2)
product_perf["Margin %"] = (product_perf["Gross Profit"] / product_perf["Sales"] * 100).round(2)
product_perf = product_perf.sort_values("Sales", ascending=False).head(6)

product_cards = []
for row in product_perf.itertuples(index=False):
    product_name = row[0]
    average_price = row[4]
    image_url = f"https://via.placeholder.com/320x220/ffffff/333333?text={quote_plus(product_name)}"
    product_cards.append(
        f"<div class='product-card'>"
        f"  <div class='product-image-wrapper'>"
        f"    <img src='{image_url}' alt='{product_name}' class='product-image' />"
        f"  </div>"
        f"  <strong>{product_name}</strong>"
        f"  <div class='product-price'>Price: ${average_price:,.2f}</div>"
        f"  <div class='meta'>Sales: ${row[1]:,.2f}</div>"
        f"  <div class='meta'>Gross Profit: ${row[2]:,.2f}</div>"
        f"  <div class='meta'>Units: {int(row[3]):,}</div>"
        f"  <div class='meta'>Margin: {row[5]:.2f}%</div>"
        f"</div>"
    )
st.markdown(f"<div class='product-row'>{''.join(product_cards)}</div>", unsafe_allow_html=True)

st.markdown('<div id="insights" class="section-title">Performance Insights</div>', unsafe_allow_html=True)
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()
gross_margin = (total_profit / total_sales) * 100 if total_sales else 0

kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown(f"<div class='metric-card'><strong>Total Sales</strong><br>${total_sales:,.2f}</div>", unsafe_allow_html=True)
with kpi_cols[1]:
    st.markdown(f"<div class='metric-card'><strong>Total Gross Profit</strong><br>${total_profit:,.2f}</div>", unsafe_allow_html=True)
with kpi_cols[2]:
    st.markdown(f"<div class='metric-card'><strong>Gross Margin</strong><br>{gross_margin:.2f}%</div>", unsafe_allow_html=True)
with kpi_cols[3]:
    st.markdown(f"<div class='metric-card'><strong>Total Units</strong><br>{int(total_units):,}</div>", unsafe_allow_html=True)

st.markdown('<div id="about" class="section-title">About Nassau Candy</div>', unsafe_allow_html=True)
st.markdown('<div class="section-card">Nassau Candy is a trusted wholesale candy distributor known for dependable service, broad product selection, and a long-standing reputation in the confectionery market.</div>', unsafe_allow_html=True)

st.markdown('<div id="contact" class="footer">Contact • About • Delivery • FAQs</div>', unsafe_allow_html=True)
