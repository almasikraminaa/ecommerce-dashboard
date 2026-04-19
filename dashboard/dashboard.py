import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set_style("whitegrid")


# Helper Functions
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule="ME", on="order_purchase_timestamp").agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return monthly_orders_df


def create_state_performance_df(df):
    state_performance_df = df.groupby(by="customer_state").agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()

    state_performance_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "total_revenue"
    }, inplace=True)

    state_performance_df = state_performance_df.sort_values(
        by="total_revenue", ascending=False
    )

    return state_performance_df


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"])
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
    )
    rfm_df["RFM_score"] = (rfm_df["RFM_score"] * 0.05).round(2)

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

    customer_segment_df = rfm_df.groupby(
        by="customer_segment", as_index=False
    )["customer_id"].nunique()

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


# Load Data
main_df = pd.read_csv("main_data.csv")
product_performance_df = pd.read_csv("product_performance.csv")

main_df["order_purchase_timestamp"] = pd.to_datetime(main_df["order_purchase_timestamp"])

main_df.sort_values(by="order_purchase_timestamp", inplace=True)
main_df.reset_index(drop=True, inplace=True)

# Pastikan kolom kategori tidak kosong bila file agregat membawanya
if "product_category_name" in product_performance_df.columns:
    product_performance_df["product_category_name"] = product_performance_df["product_category_name"].fillna("unknown")

# Sidebar Filter
min_date = main_df["order_purchase_timestamp"].min().date()
max_date = main_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.header("📊 Filter Dashboard")
    st.write("Pilih rentang waktu untuk melihat performa transaksi.")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_main_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) &
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Data turunan
monthly_orders_df = create_monthly_orders_df(filtered_main_df)
state_performance_df = create_state_performance_df(filtered_main_df)
customer_segment_df, rfm_df = create_customer_segment_df(filtered_main_df)

# Header
st.title("E-Commerce Public Dataset Dashboard :sparkles:")
st.markdown("Sales Performance Overview")

# KPI Cards
st.subheader("Ringkasan Utama")

col1, col2, col3 = st.columns(3)

with col1:
    total_orders = filtered_main_df["order_id"].nunique()
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    total_revenue = filtered_main_df["payment_value"].sum()
    st.metric("Total Revenue", format_currency(total_revenue, "BRL", locale="pt_BR"))

with col3:
    total_customers = filtered_main_df["customer_id"].nunique()
    st.metric("Total Customers", f"{total_customers:,}")

# Sales Trend
st.subheader("📈 Sales Trend")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["order_count"],
        marker="o",
        linewidth=2,
        color="#72BCD4"
    )
    ax.set_title("Number of Orders per Month", loc="center", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        monthly_orders_df["order_purchase_timestamp"],
        monthly_orders_df["revenue"],
        marker="o",
        linewidth=2,
        color="#72BCD4"
    )
    ax.set_title("Total Revenue per Month", loc="center", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

# Product Performance
st.subheader("🏆 Best & Worst Performing Product Categories")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="total_revenue",
    y="product_category_name",
    data=product_performance_df.sort_values(by="total_revenue", ascending=False).head(5),
    palette=colors,
    ax=ax[0]
)
ax[0].set_title("Top 5 Best Performing Product Categories", loc="center", fontsize=16)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].tick_params(axis="y", labelsize=11)

sns.barplot(
    x="total_revenue",
    y="product_category_name",
    data=product_performance_df.sort_values(by="total_revenue", ascending=True).head(5),
    palette=colors,
    ax=ax[1]
)
ax[1].set_title("Top 5 Worst Performing Product Categories", loc="center", fontsize=16)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis="y", labelsize=11)

st.pyplot(fig)

# State Contribution
st.subheader("🌍 Top States by Revenue Contribution")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        x="total_revenue",
        y="customer_state",
        data=state_performance_df.head(10),
        palette=["#72BCD4"] + ["#D3D3D3"] * 9,
        ax=ax
    )
    ax.set_title("Top 10 States by Revenue", loc="center", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        x="order_count",
        y="customer_state",
        data=state_performance_df.sort_values(by="order_count", ascending=False).head(10),
        palette=["#72BCD4"] + ["#D3D3D3"] * 9,
        ax=ax
    )
    ax.set_title("Top 10 States by Number of Orders", loc="center", fontsize=16)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    st.pyplot(fig)

# RFM Analysis
st.subheader("👥 Best Customers Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df["recency"].mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df["frequency"].mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df["monetary"].mean(), "BRL", locale="pt_BR")
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 8))

sns.barplot(
    y="recency",
    x="customer_id",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=["#72BCD4"] * 5,
    ax=ax[0]
)
ax[0].set_title("Top Customers by Recency (days)", loc="center", fontsize=16)
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].tick_params(axis="x", rotation=45, labelsize=9)

sns.barplot(
    y="frequency",
    x="customer_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=["#72BCD4"] * 5,
    ax=ax[1]
)
ax[1].set_title("Top Customers by Frequency", loc="center", fontsize=16)
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].tick_params(axis="x", rotation=45, labelsize=9)

sns.barplot(
    y="monetary",
    x="customer_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=["#72BCD4"] * 5,
    ax=ax[2]
)
ax[2].set_title("Top Customers by Monetary", loc="center", fontsize=16)
ax[2].set_xlabel(None)
ax[2].set_ylabel(None)
ax[2].tick_params(axis="x", rotation=45, labelsize=9)

st.pyplot(fig)

# Customer Segmentation
st.subheader("📊 Customer Segmentation Based on RFM Score")

fig, ax = plt.subplots(figsize=(12, 6))

colors_segment = ["#72BCD4", "#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="customer_id",
    y="customer_segment",
    data=customer_segment_df.sort_values(by="customer_segment", ascending=False),
    palette=colors_segment,
    ax=ax
)

ax.set_title("Number of Customers for Each Segment", loc="center", fontsize=16)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis="y", labelsize=11)

st.pyplot(fig)

st.caption("Dashboard Analisis E-Commerce | Dicoding Submission by Almas Ikramina")