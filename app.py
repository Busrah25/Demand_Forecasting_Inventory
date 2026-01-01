import streamlit as st
import pandas as pd
import numpy as np
import math
from scipy.stats import norm
import os

 # Page configuration
 st.set_page_config(
    page_title="Inventory Optimization Dashboard",
    layout="wide"
)

st.title("📦 Inventory Optimization and Reorder Planning")
st.caption("Executive decision support tool using demand forecasting and inventory analytics")

 # Load data safely regardless of run location
 @st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "data", "demand_history.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

 # Sidebar controls
 st.sidebar.header("Planning parameters")

service_level = st.sidebar.selectbox(
    "Service level",
    options=[0.90, 0.95, 0.99],
    index=1
)

lead_time_days = st.sidebar.slider(
    "Lead time in days",
    min_value=1,
    max_value=21,
    value=7
)

st.sidebar.info(
    "On hand inventory values are simulated for demonstration. "
    "Reorder logic and calculations reflect real world inventory planning methods."
)

 # Aggregate daily demand
 daily_demand = (
    df.groupby("date", as_index=False)
      .agg(units_sold=("units_sold", "sum"))
)

avg_daily_demand = daily_demand["units_sold"].mean()
std_daily_demand = daily_demand["units_sold"].std()

 # Inventory math
 z_score = norm.ppf(service_level)

safety_stock = z_score * std_daily_demand * math.sqrt(lead_time_days)
reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

 # KPI display
 col1, col2, col3, col4 = st.columns(4)

col1.metric("Average daily demand", f"{avg_daily_demand:.1f}")
col2.metric("Demand volatility", f"{std_daily_demand:.1f}")
col3.metric("Safety stock units", f"{round(safety_stock):,}")
col4.metric("Reorder point units", f"{round(reorder_point):,}")

 # SKU level demand statistics
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

sku_stats["safety_stock"] = z_score * sku_stats["std_demand_lt"]

sku_stats["reorder_point"] = (
    sku_stats["mean_demand_lt"] + sku_stats["safety_stock"]
).round().astype(int)

 # Simulated inventory and reorder logic
 rng = np.random.default_rng(2025)

sku_stats["on_hand"] = rng.integers(
    low=0,
    high=(sku_stats["reorder_point"] * 2).clip(lower=1)
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

 # Final reorder table
 st.subheader("SKU reorder recommendations")

reorder_table = (
    sku_stats
    .sort_values("recommended_order_qty", ascending=False)
    .reset_index(drop=True)
)

display_columns = [
    "sku",
    "avg_daily_demand",
    "reorder_point",
    "on_hand",
    "recommended_order_qty"
]

st.dataframe(
    reorder_table[display_columns],
    width="stretch"
)

 # Download button
 csv_data = reorder_table.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download reorder plan",
    data=csv_data,
    file_name="inventory_reorder_plan.csv",
    mime="text/csv"
)
