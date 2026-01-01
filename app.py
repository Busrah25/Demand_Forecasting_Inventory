import streamlit as st
import pandas as pd
import numpy as np
import math
from scipy.stats import norm
import os

# Page Configuration
st.set_page_config(
    page_title="Inventory Optimization Dashboard",
    layout="wide"
)

# Title
st.title("📦 Inventory Optimization & Reorder Planning")
st.caption("Executive Decision Support Tool | Demand Forecasting + Inventory Analytics")

# Load Data
@st.cache_data
def load_data():
    path = os.path.join("data", "demand_history.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# Sidebar Controls
st.sidebar.header("⚙️ Planning Parameters")

service_level = st.sidebar.selectbox(
    "Service Level",
    options=[0.90, 0.95, 0.99],
    index=1
)

lead_time_days = st.sidebar.slider(
    "Lead Time (days)",
    min_value=1,
    max_value=21,
    value=7
)

# Aggregate Daily Demand
daily_demand = (
    df.groupby("date", as_index=False)
      .agg(units_sold=("units_sold", "sum"))
)

avg_daily_demand = daily_demand["units_sold"].mean()
std_daily_demand = daily_demand["units_sold"].std()

z = norm.ppf(service_level)

safety_stock = z * std_daily_demand * math.sqrt(lead_time_days)
reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Daily Demand", f"{avg_daily_demand:.1f}")
col2.metric("Demand Volatility", f"{std_daily_demand:.1f}")
col3.metric("Safety Stock", f"{round(safety_stock):,}")
col4.metric("Reorder Point", f"{round(reorder_point):,}")

# SKU Level Analysis
daily_sku = (
    df.groupby(["sku", "date"], as_index=False)
      .agg(units_sold=("units_sold", "sum"))
)

sku_stats = (
    daily_sku.groupby("sku", as_index=False)
    .agg(
        avg_daily_demand=("units_sold", "mean"),
        std_daily_demand=("units_sold", "std")
    )
)

sku_stats["std_daily_demand"] = sku_stats["std_daily_demand"].fillna(0)

sku_stats["mean_demand_lt"] = sku_stats["avg_daily_demand"] * lead_time_days
sku_stats["std_demand_lt"] = sku_stats["std_daily_demand"] * math.sqrt(lead_time_days)

sku_stats["safety_stock"] = z * sku_stats["std_demand_lt"]
sku_stats["reorder_point"] = (
    sku_stats["mean_demand_lt"] + sku_stats["safety_stock"]
).round().astype(int)

# Simulated Inventory Position
rng = np.random.default_rng(2025)

sku_stats["on_hand"] = rng.integers(
    low=0,
    high=sku_stats["reorder_point"] * 2
)

sku_stats["inventory_position"] = sku_stats["on_hand"]

sku_stats["reorder_now"] = (
    sku_stats["inventory_position"] <= sku_stats["reorder_point"]
)

sku_stats["recommended_order_qty"] = np.where(
    sku_stats["reorder_now"],
    sku_stats["reorder_point"] * 2 - sku_stats["inventory_position"],
    0
).astype(int)

# Reorder Table
st.subheader("📋 SKU Reorder Recommendations")

reorder_table = (
    sku_stats
    .sort_values("recommended_order_qty", ascending=False)
    .reset_index(drop=True)
)

st.dataframe(reorder_table, width="stretch")

# Download Button
csv = reorder_table.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Reorder Plan",
    data=csv,
    file_name="inventory_reorder_plan.csv",
    mime="text/csv"
)
