from contextlib import contextmanager
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Retail Pulse Dashboard", page_icon="📈", layout="wide")


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def initialize_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                sale_date TEXT NOT NULL
            )
            """
        )

        count = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        if count == 0:
            sample_data = [
                ("iPhone 15", "Phone", 6, 1500000, "2026-01-10"),
                ("Samsung A55", "Phone", 8, 600000, "2026-01-18"),
                ("Dell XPS 13", "Laptop", 3, 2400000, "2026-01-28"),
                ("AirPods Pro", "Accessories", 12, 280000, "2026-02-04"),
                ("Xiaomi 14", "Phone", 5, 1000000, "2026-02-16"),
                ("Redmi Note", "Phone", 14, 320000, "2026-02-22"),
                ("Lenovo Yoga", "Laptop", 4, 2300000, "2026-03-02"),
                ("Smart Watch", "Accessories", 18, 250000, "2026-03-12"),
                ("iPhone 15", "Phone", 4, 1500000, "2026-03-19"),
                ("Samsung A55", "Phone", 7, 600000, "2026-03-27"),
                ("HP Spectre", "Laptop", 2, 2700000, "2026-04-05"),
                ("USB Hub", "Accessories", 25, 95000, "2026-04-19"),
                ("Xiaomi 14", "Phone", 6, 1000000, "2026-04-26"),
                ("AirPods Pro", "Accessories", 11, 280000, "2026-05-03"),
                ("Lenovo Yoga", "Laptop", 5, 2300000, "2026-05-14"),
                ("Samsung A55", "Phone", 9, 600000, "2026-05-20"),
                ("iPhone 15", "Phone", 5, 1500000, "2026-06-09"),
                ("Smart Watch", "Accessories", 21, 250000, "2026-06-17"),
            ]

            conn.executemany(
                """
                INSERT INTO sales (product, category, quantity, price, sale_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                sample_data,
            )


def get_sales():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM sales ORDER BY sale_date DESC").fetchall()
    return pd.DataFrame([dict(row) for row in rows])


def add_sale(product, category, quantity, price, sale_date):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sales (product, category, quantity, price, sale_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (product, category, quantity, price, sale_date),
        )


initialize_database()

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #0b1020 0%, #111827 48%, #1f2937 100%);
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero {
            background: linear-gradient(135deg, rgba(59,130,246,0.22), rgba(168,85,247,0.14));
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 22px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
        }
        .hero h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.04em;
        }
        .hero p {
            margin-top: 0.5rem;
            color: #dbeafe;
            font-size: 1rem;
        }
        .metric-card {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148,163,184,0.14);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            min-height: 115px;
        }
        .metric-card .label {
            font-size: 0.82rem;
            color: #93c5fd;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-card .value {
            font-size: 2rem;
            font-weight: 700;
            margin-top: 0.45rem;
            color: white;
        }
        .metric-card .sub {
            color: #cbd5e1;
            font-size: 0.86rem;
            margin-top: 0.2rem;
        }
        div[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.94);
        }
        .stTabs [role="tablist"] {
            gap: 0.5rem;
        }
        .stTabs [role="tab"] {
            border-radius: 10px 10px 0 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


df = get_sales()
if df.empty:
    st.warning("No sales data available yet.")
    st.stop()

df["sale_date"] = pd.to_datetime(df["sale_date"])
df["total"] = df["quantity"] * df["price"]
df["month"] = df["sale_date"].dt.to_period("M").astype(str)

with st.sidebar:
    st.header("🧭 Controls")
    st.caption("Filter your retail story")

    min_date = df["sale_date"].min().date()
    max_date = df["sale_date"].max().date()
    start_date = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("To", max_date, min_value=min_date, max_value=max_date)

    categories = sorted(df["category"].unique().tolist())
    selected_categories = st.multiselect("Categories", categories, default=categories)

    st.markdown("---")
    st.caption("Quick insight")
    top_product = df.groupby("product")["total"].sum().idxmax()
    st.write(f"Best performer: {top_product}")

filtered = df[
    (df["sale_date"].dt.date >= start_date)
    & (df["sale_date"].dt.date <= end_date)
    & (df["category"].isin(selected_categories))
].copy()

st.markdown(
    """
    <div class="hero">
        <h1>Retail Pulse Dashboard</h1>
        <p>Performance overview across products, revenue, and sales momentum.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No sales match the selected filters.")
    st.stop()

revenue = float(filtered["total"].sum())
orders = int(len(filtered))
avg_order = float(filtered["total"].mean())
best_product = filtered.groupby("product")["total"].sum().idxmax()

metrics = [
    ("Revenue", f"{revenue:,.0f} Ks", "Total channel income"),
    ("Orders", f"{orders:,}", "Completed sales"),
    ("Avg. Order", f"{avg_order:,.0f} Ks", "Average basket value"),
    ("Top Seller", best_product, "Highest product revenue"),
]

for metric in metrics:
    with st.container():
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="label">{metric[0]}</div>
                <div class="value">{metric[1]}</div>
                <div class="sub">{metric[2]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    monthly = (
        filtered.groupby("month", as_index=False)["total"].sum().rename(columns={"total": "revenue"})
    )
    monthly["month"] = pd.to_datetime(monthly["month"]).dt.strftime("%b %Y")
    fig_curve = px.line(
        monthly,
        x="month",
        y="revenue",
        title="Revenue Trend",
        markers=True,
        template="plotly_dark",
    )
    fig_curve.update_traces(line=dict(color="#60a5fa", width=3))
    st.plotly_chart(fig_curve, use_container_width=True)

with right:
    category_sales = filtered.groupby("category")["total"].sum().reset_index()
    fig_pie = px.pie(
        category_sales,
        names="category",
        values="total",
        title="Category Contribution",
        template="plotly_dark",
        hole=0.45,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    product_sales = filtered.groupby("product", as_index=False)["total"].sum().sort_values("total", ascending=False)
    fig_bar = px.bar(
        product_sales,
        x="product",
        y="total",
        title="Top Product Revenue",
        template="plotly_dark",
        color="total",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with bottom_right:
    quantity_by_product = (
        filtered.groupby("product", as_index=False)["quantity"].sum().sort_values("quantity", ascending=False)
    )
    fig_qty = px.bar(
        quantity_by_product,
        x="product",
        y="quantity",
        title="Units Sold by Product",
        template="plotly_dark",
        color="quantity",
        color_continuous_scale="Cividis",
    )
    st.plotly_chart(fig_qty, use_container_width=True)

st.markdown("### Recent sales")
recent = filtered.sort_values("sale_date", ascending=False)[["sale_date", "product", "category", "quantity", "price", "total"]]
recent = recent.rename(columns={"sale_date": "Date", "product": "Product", "category": "Category", "quantity": "Qty", "price": "Price", "total": "Revenue"})
st.dataframe(recent, use_container_width=True)

with st.expander("Add a sale"):
    with st.form("add_sale_form"):
        product = st.text_input("Product")
        category = st.selectbox("Category", ["Phone", "Laptop", "Accessories", "Other"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Unit price (Ks)", min_value=1.0, step=1000.0)
        sale_date = st.date_input("Sale date")

        if st.form_submit_button("Save sale"):
            if product.strip():
                add_sale(product.strip(), category, int(quantity), float(price), sale_date.isoformat())
                st.success("Sale saved successfully.")
                st.rerun()
            else:
                st.error("Product name is required.")
