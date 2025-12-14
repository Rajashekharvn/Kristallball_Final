# simulator.py
import pandas as pd
import numpy as np
from data_loader import load_and_process_data
from forecast_model import calculate_par_levels

def run_simulation(daily_df, par_levels_df, lead_time_days=3, reorder_fraction=0.5):

    # lookup dict for speed
    par_map = par_levels_df.set_index(['Bar Name', 'Brand Name'])['recommended_par_level_ml'].to_dict()
    results = []

    grouped = daily_df.groupby(['Bar Name', 'Brand Name'])
    for (bar, brand), group in grouped:
        key = (bar, brand)
        if key not in par_map:
            continue

        par = int(par_map[key])
        reorder_point = int(np.floor(par * reorder_fraction))

        group = group.sort_values('Date').copy()
        group['Date'] = pd.to_datetime(group['Date']).dt.normalize()

        # initial inventory setup
        first_open = group.iloc[0].get('Opening Balance (ml)', np.nan)
        if pd.isna(first_open) or first_open <= 0:
            current_inventory = par
        else:
            current_inventory = int(max(first_open, 0))

        pending_orders = []
        stockout_days = 0
        total_demand = 0
        total_lost = 0
        days_count = 0

        for _, row in group.iterrows():
            date = pd.to_datetime(row['Date']).normalize()
            demand = float(row['Consumed (ml)'])
            days_count += 1
            total_demand += demand

            # process arrivals
            arrivals = [p for p in pending_orders if p[0] <= date]
            if arrivals:
                arrived_qty = sum(q for _, q in arrivals)
                current_inventory += int(arrived_qty)
                pending_orders = [p for p in pending_orders if p[0] > date]

            # process demand
            if current_inventory >= demand:
                current_inventory -= int(np.round(demand))
            else:
                lost = demand - current_inventory
                total_lost += lost
                current_inventory = 0
                stockout_days += 1

            # reorder logic (continuous review)
            incoming_qty = sum(q for _, q in pending_orders)
            virtual_inventory = current_inventory + incoming_qty

            if virtual_inventory <= reorder_point:
                order_qty = par - virtual_inventory
                if order_qty > 0:
                    arrival_date = date + pd.Timedelta(days=lead_time_days)
                    pending_orders.append((arrival_date.normalize(), int(np.ceil(order_qty))))

        service_level = 1 - (stockout_days / days_count) if days_count > 0 else np.nan

        results.append({
            'Bar Name': bar,
            'Brand Name': brand,
            'Par Level (ml)': par,
            'Total Demand (ml)': total_demand,
            'Lost Sales (ml)': total_lost,
            'Stockout Days': stockout_days,
            'Days Simulated': days_count,
            'Service Level': service_level
        })

    return pd.DataFrame(results)

if __name__ == "__main__":
    FILE_PATH = "Copy of Consumption Dataset - Dataset.csv"
    try:
        print("Loading Data...")
        df = load_and_process_data(FILE_PATH)

        print("Calculating Pars...")
        pars = calculate_par_levels(df)

        print("Running Simulation...")
        sim_results = run_simulation(df, pars)

        print("\n--- Simulation Results (Lowest Service Levels) ---")
        display = sim_results.sort_values('Service Level').head(10)
        print(display.to_string(index=False))

        avg_sl = sim_results['Service Level'].mean()
        print(f"\nAverage Service Level across all items: {avg_sl:.2%}")

        sim_results.to_csv("simulation_results_summary.csv", index=False)
        print("Simulation summary saved to 'simulation_results_summary.csv'")

    except Exception as e:
        print(f"Error: {e}")
