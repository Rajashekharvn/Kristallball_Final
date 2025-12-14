# %% [markdown]
# # Hotel Bar Inventory Optimization: End-to-End Solution
#
# **Objective**: Design a forecasting and inventory recommendation system to optimize stock levels,
# minimizing stockouts and waste.
#
# **Methodology**:
# 1. **Data Loading**: Ingest and clean historical consumption data.
# 2. **EDA**: Analyze consumption patterns.
# 3. **Forecasting**: Calculate Average Daily Usage (ADU) and Safety Stock to determine Par Levels.
# 4. **Simulation**: Backtest the recommended Par Levels against historical demand to verify Service Levels.
#
# ---

# %% [markdown]
# ## 1. Setup & Dependencies
# Import necessary libraries. Ensure `pandas` and `numpy` are installed.

# %%
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Configuration
FILE_PATH = "Copy of Consumption Dataset - Dataset.csv"
LEAD_TIME_DAYS = 3      # Time from order to delivery
SERVICE_LEVEL_Z = 1.65  # Z-score for 95% Service Level

print("Dependencies loaded.")

# %% [markdown]
# ## 2. Data Loading & Cleaning
# We load the raw CSV, standardize column names, and aggregate consumption to a daily level.
#
# **Key Steps**:
# - Parse Dates.
# - Clean numeric columns (remove commas).
# - Aggregate by `Date`, `Bar Name`, and `Brand Name`.

# %%
def load_and_process_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)

    # Standardize column names
    df.columns = [c.strip() for c in df.columns]

    # Parse DateTime
    df['Date'] = pd.to_datetime(df['Date Time Served']).dt.date

    # Clean numeric columns
    numeric_cols = ['Opening Balance (ml)', 'Purchase (ml)', 'Consumed (ml)', 'Closing Balance (ml)']
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Handle negative consumption (data anomalies)
    df['Consumed (ml)'] = df['Consumed (ml)'].clip(lower=0)

    # Aggregate to Daily level (Total Consumption per Bar per Brand per Day)
    daily_df = df.groupby(['Date', 'Bar Name', 'Alcohol Type', 'Brand Name'], as_index=False).agg({
        'Consumed (ml)': 'sum',
        'Opening Balance (ml)': 'first',
        'Purchase (ml)': 'sum',
        'Closing Balance (ml)': 'last'
    })

    daily_df.sort_values(by=['Bar Name', 'Brand Name', 'Date'], inplace=True)
    return daily_df

# Execute Load
try:
    daily_df = load_and_process_data(FILE_PATH)
    print(f"Data Loaded Successfully. Rows: {len(daily_df)}")
    print(daily_df.head())
except Exception as e:
    print(f"Error loading data: {e}")

# %% [markdown]
# ## 3. Exploratory Data Analysis (EDA)
# Let's look at the distribution of daily consumption to understand variability. High variability implies a need for higher safety stock.

# %%
if 'daily_df' in locals():
    print("\n--- Consumption Stats ---")
    print(daily_df['Consumed (ml)'].describe())

    # Identify top moving items
    top_items = daily_df.groupby(['Bar Name', 'Brand Name'])['Consumed (ml)'].sum().sort_values(ascending=False).head(5)
    print("\n--- Top 5 Consumed Items (Total Volume) ---")
    print(top_items)

# %% [markdown]
# ## 4. Forecasting & Par Level Calculation
# We calculate the **Par Level** using statistical Inventory Control formulas.
#
# $$ \text{Par Level} = (\text{Avg Daily Usage} \times \text{Lead Time}) + \text{Safety Stock} $$
# $$ \text{Safety Stock} = Z \times \sigma_{\text{demand}} \times \sqrt{\text{Lead Time}} $$
#
# - **Avg Daily Usage (ADU)**: Mean of daily consumption.
# - **Safety Stock**: Buffer for variability (Z=1.65 for 95% confidence).

# %%
def calculate_par_levels(daily_df, lead_time_days=3, service_level_z=1.65):
    # Calculate stats per (Bar, Brand)
    stats = daily_df.groupby(['Bar Name', 'Brand Name'])['Consumed (ml)'].agg(
        mean_daily_usage='mean',
        std_daily_usage='std',
        total_days='count'
    ).reset_index()

    # Fill NaN std (single data point) with 0.5 * mean as a conservative estimate
    stats['std_daily_usage'] = stats['std_daily_usage'].fillna(stats['mean_daily_usage'] * 0.5)

    # Compute Logic
    stats['lead_time_demand'] = stats['mean_daily_usage'] * lead_time_days
    stats['safety_stock'] = service_level_z * stats['std_daily_usage'] * np.sqrt(lead_time_days)
    stats['recommended_par_level'] = stats['lead_time_demand'] + stats['safety_stock']

    # Round up (optional, keeping as float/ml for precision)
    stats['par_level_ml'] = np.ceil(stats['recommended_par_level'])

    return stats

# Execute Calculation
par_levels_df = calculate_par_levels(daily_df, LEAD_TIME_DAYS, SERVICE_LEVEL_Z)
print("\n--- Calculated Par Levels (Sample) ---")
print(par_levels_df[['Bar Name', 'Brand Name', 'mean_daily_usage', 'par_level_ml']].head())

# Save Recommendations
par_levels_df.to_csv("recommended_par_levels.csv", index=False)
print("Recommendations saved to 'recommended_par_levels.csv'.")

# %% [markdown]
# ## 5. Inventory Simulation (Backtesting)
# To validate our recommendations, we run a retrospective simulation.
#
# **Simulation Logic**:
# 1. Start with initial stock.
# 2. Iterate through history day by day.
# 3. Deduct `Consumed (ml)`.
# 4. Trigger **Restock Order** if stock <= 50% of Par Level.
# 5. Order arrives after `Lead Time` (3 days).
# 6. Measure **Stockouts** (days where Demand > Inventory).

# %%
def run_simulation(daily_df, par_levels_df, lead_time_days=3):
    par_map = par_levels_df.set_index(['Bar Name', 'Brand Name'])['par_level_ml'].to_dict()
    results = []

    grouped = daily_df.groupby(['Bar Name', 'Brand Name'])

    for (bar, brand), group in grouped:
        if (bar, brand) not in par_map:
            continue

        par = par_map[(bar, brand)]
        reorder_point = par * 0.5

        # Sort by date
        group = group.sort_values('Date')

        # Initial State
        current_inventory = group.iloc[0]['Opening Balance (ml)']
        if pd.isna(current_inventory) or current_inventory == 0:
            current_inventory = par # Assume we start healthy if data missing

        pending_orders = [] # List of (arrival_date, quantity)
        stockout_days = 0
        total_demand = 0
        total_lost_sales = 0

        dates = group['Date'].tolist()
        demands = group['Consumed (ml)'].tolist()

        for i, date in enumerate(dates):
            # 1. Receive Orders
            arrived_qty = sum(qty for d, qty in pending_orders if d <= date)
            pending_orders = [(d, qty) for d, qty in pending_orders if d > date]
            current_inventory += arrived_qty

            # 2. Fulfill Demand
            demand = demands[i]
            total_demand += demand

            if current_inventory >= demand:
                current_inventory -= demand
            else:
                # Stockout
                total_lost_sales += (demand - current_inventory)
                current_inventory = 0
                stockout_days += 1

            # 3. Reorder Logic
            incoming_stock = sum(qty for _, qty in pending_orders)
            virtual_inventory = current_inventory + incoming_stock

            if virtual_inventory <= reorder_point:
                order_qty = par - virtual_inventory
                if order_qty > 0:
                    arrival_date = date + pd.Timedelta(days=lead_time_days)
                    pending_orders.append((arrival_date, order_qty))

        results.append({
            'Bar Name': bar,
            'Brand Name': brand,
            'Par Level': par,
            'Total Demand (ml)': total_demand,
            'Stockout Days': stockout_days,
            'Service Level': 1 - (stockout_days / len(dates)) if len(dates) > 0 else 0
        })

    return pd.DataFrame(results)

# Run Simulation
sim_results = run_simulation(daily_df, par_levels_df, LEAD_TIME_DAYS)

# %% [markdown]
# ## 6. Final Results & Validation
# We check the **Average Service Level**. A value close to 95% or higher indicates the Par Levels are effective.

# %%
avg_sl = sim_results['Service Level'].mean()
print("-" * 40)
print(f"SIMULATION VALIDATION RESULTS")
print("-" * 40)
print(f"Overall Average Service Level: {avg_sl:.2%}")

# Show Low Performers (Service Level < 90%)
low_performers = sim_results[sim_results['Service Level'] < 0.90]
if not low_performers.empty:
    print("\nWarning: The following items had low service levels:")
    print(low_performers[['Bar Name', 'Brand Name', 'Service Level']].head())
else:
    print("\nSuccess: All items achieved > 90% Service Level.")

print("\nProcess Complete.")
