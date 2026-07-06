from base64 import b64encode
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data"
IMAGES_PATH = Path(__file__).resolve().parent / "images"


def _mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".gif":
        return "image/gif"
    return "application/octet-stream"


def _encode_image(path: Path) -> str:
    if not path.exists():
        return ""
    mime = _mime_type(path)
    data = b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def _safe_file_name(name: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ._-()&")
    return "".join(c if c in allowed else "_" for c in name).strip()


def get_product_image(product_name: str, rows: pd.DataFrame) -> str:
    if "Image URL" in rows.columns:
        image_url = rows.loc[rows["Product Name"] == product_name, "Image URL"].dropna().astype(str)
        if not image_url.empty and image_url.iloc[0].strip():
            return image_url.iloc[0].strip()

    if "Image Path" in rows.columns:
        image_path = rows.loc[rows["Product Name"] == product_name, "Image Path"].dropna().astype(str)
        if not image_path.empty and image_path.iloc[0].strip():
            path = IMAGES_PATH / image_path.iloc[0].strip()
            data_url = _encode_image(path)
            if data_url:
                return data_url

    safe_name = _safe_file_name(product_name)
    for suffix in [".png", ".jpg", ".jpeg", ".gif"]:
        candidate = IMAGES_PATH / f"{safe_name}{suffix}"
        if candidate.exists():
            data_url = _encode_image(candidate)
            if data_url:
                return data_url

    return f"https://via.placeholder.com/420x300/ffffff/333333?text={quote_plus(product_name)}"

st.set_page_config(page_title="Nassau Candy", page_icon="🍬", layout="wide")

st.markdown(
    """
    <style>
      * { box-sizing: border-box; }
      html, body, .stApp { background: #eef2f7; color: #111827; }
      .main .block-container { padding: 1rem 1.5rem 2rem; }

      .top-nav { display: flex; justify-content: space-between; align-items: center; gap: 1.2rem; margin-bottom: 1.2rem; }
      .brand { font-size: 1.6rem; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: #111827; }
      .nav-links { display: flex; gap: 1rem; flex-wrap: wrap; }
      .nav-links a { color: #374151; text-decoration: none; font-weight: 600; transition: color 0.2s ease; }
      .nav-links a:hover { color: #111827; }
      .header-actions { display: flex; gap: 1rem; align-items: center; color: #4b5563; font-size: 0.95rem; }
      .header-actions a { color: #111827; text-decoration: none; font-weight: 700; }

      .hero { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 1.5rem; align-items: center; padding: 2rem 1.2rem; border-radius: 1.5rem; background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); box-shadow: 0 24px 64px rgba(15, 23, 42, 0.08); }
      .hero-badge { margin-bottom: 1rem; display: inline-flex; align-items: center; gap: 0.65rem; padding: 0.8rem 1rem; border-radius: 999px; background: #111827; color: #f8fafc; font-weight: 700; font-size: 0.9rem; }
      .hero-copy h1 { font-size: clamp(2.3rem, 4vw, 3.4rem); line-height: 1.03; margin: 0 0 1rem; color: #111827; }
      .hero-copy p { margin: 0 0 1.6rem; color: #475569; font-size: 1.02rem; max-width: 680px; }
      .hero-actions { display: flex; flex-wrap: wrap; gap: 0.9rem; }
      .hero-actions a { display: inline-flex; align-items: center; justify-content: center; padding: 0.95rem 1.4rem; border-radius: 999px; text-decoration: none; font-weight: 700; transition: transform 0.2s ease; }
      .hero-actions a:hover { transform: translateY(-1px); }
      .hero-actions a.primary { background: #ffd814; color: #111827; }
      .hero-actions a.secondary { background: #f3f4f6; color: #111827; }
      .hero-image { border-radius: 1.4rem; overflow: hidden; min-height: 320px; background: linear-gradient(135deg, #fffaf2 0%, #f7f3ee 100%); display: flex; align-items: center; justify-content: center; }
      .hero-image img { width: 100%; height: auto; display: block; }

      .category-row { display: flex; flex-wrap: wrap; gap: 0.65rem; margin: 1.4rem 0 0; }
      .category-pill { display: inline-flex; align-items: center; padding: 0.75rem 1rem; border-radius: 999px; background: #ffffff; color: #1f2937; text-decoration: none; border: 1px solid #e5e7eb; font-weight: 600; transition: transform 0.2s ease, border-color 0.2s ease; }
      .category-pill:hover { transform: translateY(-1px); border-color: #111827; }

      .section-title { font-size: 1.55rem; font-weight: 800; color: #111827; margin-top: 2.2rem; margin-bottom: 1rem; }
      .product-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
      .product-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 1.2rem; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s ease, box-shadow 0.2s ease; }
      .product-card:hover { transform: translateY(-4px); box-shadow: 0 25px 40px rgba(15, 23, 42, 0.12); }
      .product-image-wrapper { position: relative; min-height: 200px; overflow: hidden; background: #f8fafc; }
      .product-image { width: 100%; height: 100%; object-fit: cover; display: block; }
      .product-content { padding: 1rem 1.1rem 1.2rem; display: flex; flex-direction: column; gap: 0.75rem; }
      .product-badge { font-size: 0.8rem; font-weight: 700; color: #047857; background: #d1fae5; border-radius: 999px; padding: 0.4rem 0.75rem; width: fit-content; }
      .product-title { font-size: 1rem; font-weight: 800; line-height: 1.4; color: #111827; min-height: 3rem; }
      .rating { display: flex; align-items: center; gap: 0.55rem; color: #475569; font-size: 0.95rem; }
      .product-price { font-size: 1.15rem; font-weight: 800; color: #b91c1c; }
      .product-meta { color: #6b7280; font-size: 0.92rem; line-height: 1.6; }
      .product-actions { display: grid; gap: 0.65rem; margin-top: auto; }
      .product-actions a { display: inline-flex; align-items: center; justify-content: center; padding: 0.9rem 1rem; border-radius: 0.95rem; text-decoration: none; font-weight: 700; }
      .product-actions a.buy { background: #ff9900; color: #111827; }
      .product-actions a.details { background: #f3f4f6; color: #111827; }

      .metric-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 1rem; padding: 1.1rem 1.2rem; min-height: 100px; }
      .metric-card strong { font-size: 1rem; font-weight: 700; color: #111827; }
      .metric-card div { margin-top: 0.5rem; font-size: 1.25rem; color: #1f2937; }

      .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem; }
      .feature-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 1.1rem; padding: 1rem; display: flex; gap: 0.85rem; align-items: flex-start; }
      .feature-icon { width: 2.4rem; height: 2.4rem; border-radius: 50%; display: grid; place-items: center; font-size: 1.05rem; color: #ffffff; background: #f97316; }
      .feature-copy strong { display: block; font-size: 1rem; margin-bottom: 0.35rem; color: #111827; }
      .feature-copy span { color: #4b5563; font-size: 0.95rem; }

      .section-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 1.1rem; padding: 1.2rem; color: #374151; }
      .footer { margin-top: 2rem; padding-top: 1.2rem; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.95rem; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 0.75rem; }
      .footer a { color: #374151; text-decoration: none; }

      @media(max-width: 940px) {
        .hero { grid-template-columns: 1fr; }
        .top-nav { flex-direction: column; align-items: flex-start; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="top-nav">
      <div class="brand">Nassau Candy</div>
      <div class="nav-links">
        <a href="#featured">Featured</a>
        <a href="#bestsellers">Best Sellers</a>
        <a href="#insights">Insights</a>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
      </div>
      <div class="header-actions">
        <span>Free shipping on wholesale orders</span>
        <a href="#contact">Help</a>
      </div>
    </div>
    <div class="hero">
      <div class="hero-copy">
        <div class="hero-badge">Wholesale candy marketplace with enterprise polish</div>
        <h1>Modern storefront design for premium confectionery distribution.</h1>
        <p>Find your top-selling candy, review performance at a glance, and position Nassau Candy as a professional marketplace partner that buyers can trust.</p>
        <div class="hero-actions">
          <a class="primary" href="#bestsellers">Shop Best Sellers</a>
          <a class="secondary" href="#insights">See Analytics</a>
        </div>
      </div>
      <div class="hero-image">
        <img src="https://via.placeholder.com/700x460/ffffff/333333?text=Candy+Marketplace" alt="Nassau Candy storefront" />
      </div>
    </div>
    <div class="category-row">
      <a class="category-pill" href="#bestsellers">Chocolate</a>
      <a class="category-pill" href="#bestsellers">Bulk Packs</a>
      <a class="category-pill" href="#bestsellers">Promotions</a>
      <a class="category-pill" href="#bestsellers">Fast Delivery</a>
      <a class="category-pill" href="#bestsellers">Top Rated</a>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find the data file at {DATA_PATH}")
    st.stop()
except pd.errors.ParserError as error:
    st.error(f"Unable to parse the dataset: {error}")
    st.stop()

required_columns = {"Division", "Region", "Sales", "Gross Profit", "Units", "Product Name"}
missing = required_columns.difference(df.columns)
if missing:
    st.error(f"The dataset is missing required columns: {sorted(missing)}")
    st.stop()

with st.sidebar:
    st.header("Search & filters")
    search_query = st.text_input("Search products", "")
    divisions = sorted(df["Division"].dropna().unique())
    regions = sorted(df["Region"].dropna().unique())
    selected_divisions = st.multiselect("Category", divisions, default=divisions)
    selected_regions = st.multiselect("Region", regions, default=regions)
    st.markdown("---")
    st.caption("Nassau Candy analytics for wholesale distribution")

filtered_df = df[df["Division"].isin(selected_divisions) & df["Region"].isin(selected_regions)]
if search_query:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(search_query, case=False, na=False)
        | filtered_df["Division"].str.contains(search_query, case=False, na=False)
        | filtered_df["Region"].str.contains(search_query, case=False, na=False)
    ]

if filtered_df.empty:
    st.warning("No matching items. Try a broader filter or search term.")
    st.stop()

st.markdown('<div id="bestsellers" class="section-title">Best-selling products</div>', unsafe_allow_html=True)

product_perf = (
    filtered_df.groupby("Product Name")[["Sales", "Gross Profit", "Units"]]
    .sum()
    .reset_index()
)
product_perf["Average Price"] = (product_perf["Sales"] / product_perf["Units"]).round(2)
product_perf["Margin"] = (product_perf["Gross Profit"] / product_perf["Sales"] * 100).round(1)
product_perf = product_perf.sort_values("Sales", ascending=False).head(8)

product_cards = []
for index, row in product_perf.reset_index(drop=True).iterrows():
    product_name = row["Product Name"]
    average_price = row["Average Price"]
    sales = row["Sales"]
    profit = row["Gross Profit"]
    units = row["Units"]
    margin = row["Margin"]
    badge = "Best Seller" if index == 0 else "Popular"
    rating = min(5.0, round(4.6 + index * 0.12, 1))
    region = filtered_df.loc[filtered_df["Product Name"] == product_name, "Region"].mode().iloc[0]
    division = filtered_df.loc[filtered_df["Product Name"] == product_name, "Division"].mode().iloc[0]
    image_url = get_product_image(product_name, filtered_df)
    product_cards.append(
        f"<div class='product-card'>"
        f"  <div class='product-image-wrapper'>"
        f"    <img src='{image_url}' alt='{product_name}' class='product-image' />"
        f"  </div>"
        f"  <div class='product-content'>"
        f"    <span class='product-badge'>{badge}</span>"
        f"    <div class='product-title'>{product_name}</div>"
        f"    <div class='rating'>{'⭐' * int(rating)} {rating} · {int(units):,} units sold</div>"
        f"    <div class='product-price'>${average_price:,.2f}</div>"
        f"    <div class='product-meta'>Category: {division}</div>"
        f"    <div class='product-meta'>Region: {region}</div>"
        f"    <div class='product-meta'>Revenue: ${sales:,.2f} · Margin: {margin:.1f}%</div>"
        f"    <div class='product-actions'>"
        f"      <a class='buy' href='#contact'>Order now</a>"
        f"      <a class='details' href='#insights'>View analytics</a>"
        f"    </div>"
        f"  </div>"
        f"</div>"
    )
st.markdown(f"<div class='product-row'>{''.join(product_cards)}</div>", unsafe_allow_html=True)

st.markdown('<div id="data" class="section-title">Product and order data</div>', unsafe_allow_html=True)
filtered_summary = (
  filtered_df.groupby(["Product Name", "Product ID", "Division", "Region"])[["Sales", "Gross Profit", "Units", "Cost"]]
  .sum()
  .reset_index()
)
filtered_summary["Average Price"] = (filtered_summary["Sales"] / filtered_summary["Units"]).round(2)
filtered_summary["Margin %"] = (filtered_summary["Gross Profit"] / filtered_summary["Sales"] * 100).round(1)

st.markdown(
  """
  <div class="section-card">
    <strong>Data overview:</strong> Product-level sales, profit, cost, units and margin details from the filtered dataset.
  </div>
  """,
  unsafe_allow_html=True,
)

st.dataframe(
  filtered_summary[
    ["Product Name", "Product ID", "Division", "Region", "Units", "Average Price", "Sales", "Gross Profit", "Margin %"]
  ].sort_values("Sales", ascending=False).reset_index(drop=True),
  use_container_width=True,
)

with st.expander("View full order detail table"):
  st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

st.markdown('<div id="insights" class="section-title">Marketplace insights</div>', unsafe_allow_html=True)

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()
gross_margin = (total_profit / total_sales) * 100 if total_sales else 0

kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown(f"<div class='metric-card'><strong>Total sales</strong><div>${total_sales:,.0f}</div></div>", unsafe_allow_html=True)
with kpi_cols[1]:
    st.markdown(f"<div class='metric-card'><strong>Total gross profit</strong><div>${total_profit:,.0f}</div></div>", unsafe_allow_html=True)
with kpi_cols[2]:
    st.markdown(f"<div class='metric-card'><strong>Average margin</strong><div>{gross_margin:.1f}%</div></div>", unsafe_allow_html=True)
with kpi_cols[3]:
    st.markdown(f"<div class='metric-card'><strong>Total units sold</strong><div>{int(total_units):,}</div></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-icon">🍫</div>
        <div class="feature-copy"><strong>Curated selection</strong><span>Top-performing products from the dataset, presented like a modern storefront.</span></div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🚚</div>
        <div class="feature-copy"><strong>Fast delivery</strong><span>Regional shipping and distribution insights built for wholesale buyers.</span></div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-copy"><strong>Performance driven</strong><span>Sales, profit, and margin metrics that support smarter ordering decisions.</span></div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">⭐</div>
        <div class="feature-copy"><strong>Premium storefront</strong><span>Sleek navigation, polished cards, and consistent visuals make the app feel more professional.</span></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div id="about" class="section-title">About Nassau Candy</div>', unsafe_allow_html=True)
st.markdown('<div class="section-card">Nassau Candy is a trusted wholesale candy distributor with a polished marketplace feel. We combine premium product visibility with the data-driven insights needed to support retailers, gift shops, and bulk buyers.</div>', unsafe_allow_html=True)
st.markdown('<div class="section-card"><strong>Owner:</strong> Kavyanjali Bouddha<br><strong>Location:</strong> New Delhi<br><strong>Mobile:</strong> 9568401180</div>', unsafe_allow_html=True)

st.markdown('<div id="contact" class="footer">Contact • About • Delivery • FAQs</div>', unsafe_allow_html=True)
