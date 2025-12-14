# forecast_model.py
import pandas as pd
import numpy as np
from data_loader import load_and_process_data

def calculate_par_levels(daily_df, lead_time_days=3, service_level_z=1.65, bottle_ml=750):
    """
    Calculates Par Levels for each item at each bar.
    Returns a DataFrame with par in ml and in bottles (rounded up).
    """

    stats = daily_df.groupby(['Bar Name', 'Brand Name'])['Consumed (ml)'].agg(
        mean_daily_usage='mean', # mean daily usage
        std_daily_usage='std', # standard deviation of daily usage
        total_days='count' # total number of days
    ).reset_index() # reset index

    # If std is NaN (single observation), use a conservative estimate:
    # here we use 50% of mean (heuristic). Document this choice.
    stats['std_daily_usage'] = stats['std_daily_usage'].fillna(stats['mean_daily_usage'] * 0.5) # fill NaN with 50% of mean

    # Compute lead-time demand and safety stock
    stats['lead_time_demand'] = stats['mean_daily_usage'] * lead_time_days  # lead-time demand
    stats['safety_stock'] = service_level_z * stats['std_daily_usage'] * np.sqrt(lead_time_days) # safety stock
    stats['recommended_par_level_ml'] = np.ceil(stats['lead_time_demand'] + stats['safety_stock']) # recommended par level in ml

    # Also provide bottles (rounded up)
    stats['par_bottles_750ml'] = np.ceil(stats['recommended_par_level_ml'] / bottle_ml).astype(int) # recommended par level in bottles

    return stats

# run as script
def run_analysis(input_file):
    df = load_and_process_data(input_file) # load and process data
    print("--- Data Summary (aggregated) ---")
    print(df[['Date','Bar Name','Brand Name','Consumed (ml)']].head()) # print first 5 rows

    par_levels = calculate_par_levels(df) # calculate par levels
    print("\n--- Recommended Par Levels (example) ---")
    print(par_levels[['Bar Name','Brand Name','mean_daily_usage','recommended_par_level_ml','par_bottles_750ml']].sort_values('mean_daily_usage', ascending=False).head(10).to_string(index=False)) # print first 10 rows
    return par_levels

if __name__ == "__main__":
    FILE_PATH = "Copy of Consumption Dataset - Dataset.csv"
    try:
        pars = run_analysis(FILE_PATH) # run analysis
        pars.to_csv("recommended_par_levels.csv", index=False) # save to CSV
        print("\nRecommendations saved to 'recommended_par_levels.csv'")
    except Exception as e: # catch any errors
        print(f"Error: {e}") # print error
