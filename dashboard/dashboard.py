from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set_style("whitegrid")

st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
MAIN_DATA_PATH = BASE_DIR / "main_data.csv"

# CSS
st.markdown("""
<style>
.sidebar-title {
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 25px;
}

/* Jangan paksa warna sidebar agar mengikuti tema Streamlit */
section[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128, 128, 128, 0.25);
}

/* Tombol menu sidebar */
div.stButton > button {
    width: 100%;
    height: 46px;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-weight: 600;
    border: 1px solid rgba(128, 128, 128, 0.35);

    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

/* Tombol aktif */
div.stButton > button[kind="primary"] {
    background-color: #ff5a4f;
    color: white;
    border: none;
}

/* Metric card mengikuti tema, tidak dipaksa putih */
div[data-testid="stMetric"] {
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(128, 128, 128, 0.25);
}

/* Supaya chart container tetap rapi */
div[data-testid="stPyplot"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# Load Data
main_df = pd.read_csv(MAIN_DATA_PATH)

main_df["order_purchase_timestamp"] = pd.to_datetime(main_df["order_purchase_timestamp"])
main_df["product_category_name"] = main_df["product_category_name"].fillna("unknown")

main_df.sort_values(by="order_purchase_timestamp", inplace=True)
main_df.reset_index(drop=True, inplace=True)

# Mapping state agar filter lebih mudah dipahami
state_name_map = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba",
    "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins"
}

state_code_map = {v: k for k, v in state_name_map.items()}
main_df["customer_state_name"] = main_df["customer_state"].map(state_name_map)

# Helper Functions
def get_order_level_df(df):
    return df.groupby("order_id", as_index=False).agg({
        "customer_id": "first",
        "customer_state": "first",
        "customer_state_name": "first",
        "order_purchase_timestamp": "max",
        "payment_value": "max"
    })


def create_monthly_orders_df(df):
    order_df = get_order_level_df(df)

    monthly_orders_df = order_df.resample(
        rule="ME",
        on="order_purchase_timestamp"
    ).agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return monthly_orders_df


def create_product_performance_df(df):
    item_count_df = df.groupby("order_id")["order_item_id"].count().rename("item_count")
    temp_df = df.merge(item_count_df, on="order_id", how="left")

    temp_df["allocated_payment"] = temp_df["payment_value"] / temp_df["item_count"]

    product_performance_df = temp_df.groupby("product_category_name", as_index=False).agg({
        "order_item_id": "count",
        "allocated_payment": "sum"
    })

    product_performance_df.rename(columns={
        "order_item_id": "total_items_sold",
        "allocated_payment": "total_revenue"
    }, inplace=True)

    return product_performance_df.sort_values(by="total_revenue", ascending=False)


def create_state_performance_df(df):
    order_df = get_order_level_df(df)

    state_performance_df = order_df.groupby("customer_state", as_index=False).agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })

    state_performance_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "total_revenue"
    }, inplace=True)

    return state_performance_df.sort_values(by="total_revenue", ascending=False)


def create_rfm_df(df):
    order_df = get_order_level_df(df)

    rfm_df = order_df.groupby("customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    recent_date = rfm_df["max_order_timestamp"].max()
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days

    return rfm_df


def create_customer_segment_df(df):
    rfm_df = create_rfm_df(df).copy()

    rfm_df["r_rank"] = rfm_df["recency"].rank(ascending=False)
    rfm_df["f_rank"] = rfm_df["frequency"].rank(ascending=True)
    rfm_df["m_rank"] = rfm_df["monetary"].rank(ascending=True)

    rfm_df["r_rank_norm"] = (rfm_df["r_rank"] / rfm_df["r_rank"].max()) * 100
    rfm_df["f_rank_norm"] = (rfm_df["f_rank"] / rfm_df["f_rank"].max()) * 100
    rfm_df["m_rank_norm"] = (rfm_df["m_rank"] / rfm_df["m_rank"].max()) * 100

    rfm_df["RFM_score"] = (
        0.15 * rfm_df["r_rank_norm"] +
        0.28 * rfm_df["f_rank_norm"] +
        0.57 * rfm_df["m_rank_norm"]
    ) * 0.05

    rfm_df["RFM_score"] = rfm_df["RFM_score"].round(2)

    rfm_df["customer_segment"] = pd.cut(
        rfm_df["RFM_score"],
        bins=[0, 1.6, 3, 4, 4.5, 5],
        labels=[
            "Lost Customers",
            "Low Value Customers",
            "Medium Value Customers",
            "High Value Customers",
            "Top Customers"
        ],
        include_lowest=True
    )

    customer_segment_df = rfm_df.groupby("customer_segment", as_index=False)["customer_id"].nunique()

    customer_segment_df["customer_segment"] = pd.Categorical(
        customer_segment_df["customer_segment"],
        categories=[
            "Lost Customers",
            "Low Value Customers",
            "Medium Value Customers",
            "High Value Customers",
            "Top Customers"
        ],
        ordered=True
    )

    return customer_segment_df, rfm_df


# Sidebar
with st.sidebar:
    st.markdown('<h1 class="sidebar-title">🛒 E-Commerce</h1>', unsafe_allow_html=True)
    st.markdown("### Menu")

    if "page" not in st.session_state:
        st.session_state.page = "visualisasi"

    with st.container():
        if st.button(
            "📊 Data Visualization",
            type="primary" if st.session_state.page == "visualisasi" else "secondary",
            use_container_width=True
        ):
            st.session_state.page = "visualisasi"

    with st.container():
        if st.button(
            "👥 RFM Analysis",
            type="primary" if st.session_state.page == "rfm" else "secondary",
            use_container_width=True
        ):
            st.session_state.page = "rfm"

    st.markdown("---")
    st.markdown("### Dashboard Filters")

    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()

    start_date, end_date = st.date_input(
        "📅 Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    available_states = sorted(main_df["customer_state_name"].dropna().unique().tolist())

    selected_state_names = st.multiselect(
        "🌍 Select State",
        options=["All States"] + available_states,
        default=["All States"]
    )

    st.markdown("---")
    st.info("Use date and state filters to explore data dynamically.")

# Apply Filter
filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) &
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
].copy()

if "All States" not in selected_state_names:
    selected_state_codes = [state_code_map[state] for state in selected_state_names]
    filtered_df = filtered_df[filtered_df["customer_state"].isin(selected_state_codes)].copy()

if filtered_df.empty:
    st.warning("Tidak ada data pada kombinasi filter yang dipilih.")
    st.stop()

# Derived Data
order_level_df = get_order_level_df(filtered_df)
monthly_orders_df = create_monthly_orders_df(filtered_df)
product_performance_df = create_product_performance_df(filtered_df)
state_performance_df = create_state_performance_df(filtered_df)
customer_segment_df, rfm_df = create_customer_segment_df(filtered_df)

# Header & KPI
st.title("E-Commerce Public Dataset Dashboard")
st.caption("Dashboard interaktif untuk menganalisis performa penjualan, kategori produk, wilayah, dan segmentasi pelanggan.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Orders", f"{order_level_df['order_id'].nunique():,}")

with col2:
    total_revenue = order_level_df["payment_value"].sum()
    st.metric("Total Revenue", format_currency(total_revenue, "BRL", locale="pt_BR"))

with col3:
    st.metric("Total Customers", f"{order_level_df['customer_id'].nunique():,}")

# Page 1 - Visualisasi Data
if st.session_state.page == "visualisasi":
    st.markdown("## 📊 Data Visualization & Business Insights")

    st.subheader("📈 Monthly Sales Trends")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(
            monthly_orders_df["order_purchase_timestamp"],
            monthly_orders_df["order_count"],
            marker="o",
            linewidth=2,
            color="#72BCD4"
        )
        ax.set_title("Number of Orders per Month")
        ax.set_xlabel(None)
        ax.set_ylabel(None)
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.plot(
            monthly_orders_df["order_purchase_timestamp"],
            monthly_orders_df["revenue"],
            marker="o",
            linewidth=2,
            color="#72BCD4"
        )
        ax.set_title("Total Revenue per Month")
        ax.set_xlabel(None)
        ax.set_ylabel(None)
        ax.tick_params(axis="x", rotation=45)
        st.pyplot(fig)

    st.subheader("📦 Product Category Performance")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))

    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        x="total_revenue",
        y="product_category_name",
        data=product_performance_df.head(5),
        palette=colors,
        ax=ax[0]
    )
    ax[0].set_title("Top 5 Best Performing Categories")
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)

    sns.barplot(
        x="total_revenue",
        y="product_category_name",
        data=product_performance_df.sort_values(by="total_revenue", ascending=True).head(5),
        palette=colors,
        ax=ax[1]
    )
    ax[1].set_title("Top 5 Worst Performing Categories")
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()

    st.pyplot(fig)

    st.subheader("🌍 Regional Contribution Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(
            x="total_revenue",
            y="customer_state",
            data=state_performance_df.head(10),
            palette=["#72BCD4"] + ["#D3D3D3"] * 9,
            ax=ax
        )
        ax.set_title("Top 10 States by Revenue")
        ax.set_xlabel(None)
        ax.set_ylabel(None)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(
            x="order_count",
            y="customer_state",
            data=state_performance_df.sort_values(by="order_count", ascending=False).head(10),
            palette=["#72BCD4"] + ["#D3D3D3"] * 9,
            ax=ax
        )
        ax.set_title("Top 10 States by Orders")
        ax.set_xlabel(None)
        ax.set_ylabel(None)
        st.pyplot(fig)

    st.subheader("🔍 Exploratory Data Overview")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        sns.histplot(order_level_df["payment_value"], kde=True, color="#72BCD4", ax=ax)
        ax.set_title("Distribution of Payment Value")
        ax.set_xlabel("Payment Value")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        sns.boxplot(x=order_level_df["payment_value"], color="#72BCD4", ax=ax)
        ax.set_title("Boxplot of Payment Value")
        ax.set_xlabel("Payment Value")
        st.pyplot(fig)

# Page 2 - RFM
else:
    st.markdown("## 👥 Customer Segmentation (RFM Analysis)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Average Recency (days)", round(rfm_df["recency"].mean(), 1))

    with col2:
        st.metric("Average Frequency", round(rfm_df["frequency"].mean(), 2))

    with col3:
        avg_monetary = format_currency(rfm_df["monetary"].mean(), "BRL", locale="pt_BR")
        st.metric("Average Monetary", avg_monetary)

    st.subheader("🏆 Top Customers by RFM Metrics")

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

    sns.barplot(
        y="recency",
        x="customer_id",
        data=rfm_df.sort_values(by="recency").head(5),
        palette=["#72BCD4"] * 5,
        ax=ax[0]
    )
    ax[0].set_title("Top by Recency")
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis="x", rotation=45, labelsize=8)

    sns.barplot(
        y="frequency",
        x="customer_id",
        data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
        palette=["#72BCD4"] * 5,
        ax=ax[1]
    )
    ax[1].set_title("Top by Frequency")
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis="x", rotation=45, labelsize=8)

    sns.barplot(
        y="monetary",
        x="customer_id",
        data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
        palette=["#72BCD4"] * 5,
        ax=ax[2]
    )
    ax[2].set_title("Top by Monetary")
    ax[2].set_xlabel(None)
    ax[2].set_ylabel(None)
    ax[2].tick_params(axis="x", rotation=45, labelsize=8)

    st.pyplot(fig)

    st.subheader("📊 Customer Segmentation Distribution")

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        x="customer_id",
        y="customer_segment",
        data=customer_segment_df.sort_values(by="customer_segment", ascending=False),
        palette=["#72BCD4", "#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"],
        ax=ax
    )
    ax.set_title("Number of Customers for Each Segment")
    ax.set_xlabel(None)
    ax.set_ylabel(None)

    st.pyplot(fig)

st.caption("Dashboard Analisis E-Commerce | Dicoding Submission by Almas Ikramina")