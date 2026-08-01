from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Pulse | Sales Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://docs.streamlit.io/",
        "Report a bug": None,
        "About": "Pulse Sales Analytics — a local sales performance dashboard.",
    },
)

MONTH_SEQUENCE = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
REQUIRED_COLUMNS = {"Product", "Category", "Sales", "Profit"}


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """Read the bundled sample data."""
    return pd.read_csv(Path(__file__).with_name("sales_data.csv"))


def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize data from the sample file or an uploaded CSV."""
    data = data.copy()
    data.columns = data.columns.str.strip().str.title()
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(sorted(missing)))

    data["Sales"] = pd.to_numeric(data["Sales"], errors="coerce")
    data["Profit"] = pd.to_numeric(data["Profit"], errors="coerce")
    data = data.dropna(subset=["Product", "Category", "Sales", "Profit"])
    if data.empty:
        raise ValueError("No valid records were found after cleaning the data.")
    if (data["Sales"] < 0).any():
        raise ValueError("Sales values cannot be negative.")

    if "Date" in data.columns:
        dates = pd.to_datetime(data["Date"], errors="coerce")
        data["Month"] = dates.dt.month_name().fillna("Unknown")
    elif "Month" not in data.columns:
        fallback_months = MONTH_SEQUENCE * ((len(data) // len(MONTH_SEQUENCE)) + 1)
        data["Month"] = fallback_months[: len(data)]
    else:
        data["Month"] = data["Month"].astype(str).str.strip()
    return data


def reset_filters() -> None:
    st.session_state["months_filter"] = available_months.copy()
    st.session_state["categories_filter"] = sorted(data["Category"].unique().tolist())


def currency(value: float) -> str:
    return f"Rs. {value:,.0f}"


def csv_download(dataframe: pd.DataFrame) -> bytes:
    """Create a UTF-8 CSV that opens cleanly in spreadsheet applications."""
    return dataframe.to_csv(index=False).encode("utf-8-sig")


st.markdown(
    """
    <style>
        .block-container {max-width: 1500px; padding-top: 1.8rem; padding-bottom: 2.2rem;}
        [data-testid="stSidebar"] {background: linear-gradient(180deg, #f8fafc 0%, #eef6ff 100%);}
        [data-testid="stMetric"] {background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
          box-shadow: 0 2px 10px rgba(15, 23, 42, .04); padding: .95rem 1.1rem;}
        [data-testid="stMetricLabel"] {color: #64748b; font-size: .84rem;}
        [data-testid="stMetricValue"] {color: #0f172a; font-weight: 700;}
        div[data-testid="stExpander"] {border: 1px solid #e5e7eb; border-radius: 10px;}
        .eyebrow {font-size: .75rem; color: #2563eb; font-weight: 700; letter-spacing: .11em; text-transform: uppercase;}
        .section-note {color: #64748b; font-size: .88rem; margin-top: -.45rem; margin-bottom: .5rem;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Pulse")
    st.caption("Sales performance workspace")
    uploaded_file = st.file_uploader("Upload sales CSV", type="csv", help="Required: Product, Category, Sales, Profit. Optional: Month or Date.")

if uploaded_file is not None:
    try:
        data = prepare_data(pd.read_csv(uploaded_file))
        data_source = uploaded_file.name
    except (ValueError, pd.errors.ParserError) as error:
        st.error(f"Unable to load the uploaded file: {error}")
        st.stop()
else:
    data = prepare_data(load_sample_data())
    data_source = "Bundled sample data"

available_months = [month for month in MONTH_SEQUENCE if month in data["Month"].unique()]
available_months += sorted(set(data["Month"]) - set(available_months))
available_categories = sorted(data["Category"].unique().tolist())

if "months_filter" not in st.session_state or not set(st.session_state["months_filter"]).issubset(available_months):
    st.session_state["months_filter"] = available_months.copy()
if "categories_filter" not in st.session_state or not set(st.session_state["categories_filter"]).issubset(available_categories):
    st.session_state["categories_filter"] = available_categories.copy()

with st.sidebar:
    st.divider()
    st.markdown("#### View controls")
    st.multiselect("Period", available_months, key="months_filter")
    st.multiselect("Category", available_categories, key="categories_filter")
    sales_target = st.number_input("Sales target (Rs.)", min_value=0, value=50000, step=5000)
    st.button("Reset filters", width="stretch", on_click=reset_filters)
    st.divider()
    st.caption(f"Source: {data_source}")
    st.caption(f"{len(data):,} valid records loaded")

filtered = data[data["Month"].isin(st.session_state["months_filter"]) & data["Category"].isin(st.session_state["categories_filter"])].copy()
if filtered.empty:
    st.warning("No records match the selected filters. Reset filters or select another combination.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
order_count = len(filtered)
profit_margin = total_profit / total_sales if total_sales else 0
target_progress = min(total_sales / sales_target, 1.0) if sales_target else 1.0

st.markdown("<div class='eyebrow'>Executive overview</div>", unsafe_allow_html=True)
title_col, status_col = st.columns((4, 1))
with title_col:
    st.title("Sales performance")
    st.caption("Track revenue, profitability, and the products creating the most value.")
with status_col:
    st.metric("Target status", f"{target_progress:.0%}", "achieved" if total_sales >= sales_target else "in progress")

metrics = st.columns(4)
metrics[0].metric("Net sales", currency(total_sales), f"{total_sales / data['Sales'].sum():.0%} of loaded data")
metrics[1].metric("Gross profit", currency(total_profit), f"{total_profit / data['Profit'].sum():.0%} of loaded data")
metrics[2].metric("Transactions", f"{order_count:,}", f"{order_count / len(data):.0%} selected")
metrics[3].metric("Profit margin", f"{profit_margin:.1%}", "profit / sales")

st.divider()
trend_col, target_col = st.columns((1.85, 1), gap="large")
monthly = filtered.groupby("Month", sort=False)[["Sales", "Profit"]].sum().reindex(st.session_state["months_filter"]).dropna()

with trend_col:
    st.subheader("Revenue and profit trend")
    st.markdown("<div class='section-note'>Compare sales volume with the profit it generates over time.</div>", unsafe_allow_html=True)
    st.line_chart(monthly, color=["#2563eb", "#16a34a"], height=310)

with target_col:
    st.subheader("Target progress")
    st.markdown("<div class='section-note'>Current selection against your sales goal.</div>", unsafe_allow_html=True)
    st.progress(target_progress, text=f"{currency(total_sales)} of {currency(sales_target)}")
    remaining = max(sales_target - total_sales, 0)
    if remaining:
        st.warning(f"{currency(remaining)} remains to hit the target.")
    else:
        st.success(f"Target exceeded by {currency(total_sales - sales_target)}.")
    st.metric("Average order value", currency(total_sales / order_count))
    st.metric("Average profit / order", currency(total_profit / order_count))

st.divider()
category_col, product_col = st.columns((1.05, 1), gap="large")
category_summary = (filtered.groupby("Category", as_index=False)
                    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
                    .sort_values("Sales", ascending=True))

with category_col:
    st.subheader("Category contribution")
    st.markdown("<div class='section-note'>Sales and profit contribution by category.</div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    fig.patch.set_facecolor("white")
    positions = range(len(category_summary))
    ax.barh([x - .18 for x in positions], category_summary["Sales"], height=.34, color="#2563eb", label="Sales")
    ax.barh([x + .18 for x in positions], category_summary["Profit"], height=.34, color="#22c55e", label="Profit")
    ax.set_yticks(list(positions), category_summary["Category"])
    ax.xaxis.set_visible(False)
    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    st.pyplot(fig, width="stretch")
    plt.close(fig)

with product_col:
    st.subheader("Product leaderboard")
    st.markdown("<div class='section-note'>Top products ranked by sales, with profitability context.</div>", unsafe_allow_html=True)
    product_summary = (filtered.groupby(["Product", "Category"], as_index=False)
                       .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
                       .assign(**{"Profit margin": lambda x: x["Profit"] / x["Sales"]})
                       .sort_values("Sales", ascending=False))
    st.dataframe(product_summary, column_config={
        "Sales": st.column_config.NumberColumn(format="Rs. %d"),
        "Profit": st.column_config.NumberColumn(format="Rs. %d"),
        "Profit margin": st.column_config.NumberColumn(format="%.1f%%"),
    }, hide_index=True, width="stretch", height=250)

st.divider()
insight_col, details_col = st.columns((1, 1.35), gap="large")
top_product = product_summary.iloc[0]
best_margin = product_summary.loc[product_summary["Profit margin"].idxmax()]
category_leader = category_summary.iloc[-1]

with insight_col:
    st.subheader("Executive highlights")
    st.markdown("<div class='section-note'>Automatically derived from the current selection.</div>", unsafe_allow_html=True)
    st.info(f"**{top_product['Product']}** is the sales leader, contributing {currency(top_product['Sales'])}.")
    st.success(f"**{best_margin['Product']}** has the strongest margin at {best_margin['Profit margin']:.1%}.")
    st.caption(f"Largest category: {category_leader['Category']} ({currency(category_leader['Sales'])} in sales).")

with details_col:
    st.subheader("Transaction detail")
    st.markdown("<div class='section-note'>Review the selected records or export them for follow-up.</div>", unsafe_allow_html=True)
    detail_columns = ["Product", "Category", "Month", "Sales", "Profit"]
    display_df = filtered[detail_columns].sort_values("Sales", ascending=False)
    st.dataframe(display_df, column_config={
        "Sales": st.column_config.NumberColumn(format="Rs. %d"),
        "Profit": st.column_config.NumberColumn(format="Rs. %d"),
    }, hide_index=True, width="stretch", height=220)
    st.download_button("Download current view", csv_download(display_df),
                       "sales_export.csv", "text/csv", width="content")

st.caption("Pulse Sales Analytics | All visuals reflect the selected filters.")
