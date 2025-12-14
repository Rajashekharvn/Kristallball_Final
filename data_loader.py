# data_loader.py
import pandas as pd #import pandas as pd
import os #import os
import numpy as np #import numpy as np

def load_and_process_data(filepath, zero_threshold=1e-6):
    """
    Loads the consumption dataset, parses dates, and cleans column names.
    Returns a DataFrame aggregated to daily consumption per (Date, Bar Name, Brand Name).
    - Keeps Date as pd.Timestamp (datetime64[ns]) normalized to midnight.
    - Converts very small scientific-notation numbers (e.g., 1.71E-13) to 0.
    """

    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Load data
    print(f"Loading data from {filepath}...")

    # Read the CSV file
    df = pd.read_csv(filepath)

    # 1. Standardize column names & remove extra spaces
    df.columns = [c.strip() for c in df.columns]

    # 2. Parse DateTime -> keep full datetime then normalize to midnight & drop rows with invalid dates
    df['Date Time Served'] = pd.to_datetime(df['Date Time Served'], errors='coerce')
    if df['Date Time Served'].isna().any():
        print("Warning: some Date Time Served values could not be parsed and will be dropped.")
    df = df.dropna(subset=['Date Time Served']) # drop rows with invalid dates
    df['Date'] = df['Date Time Served'].dt.normalize()  # midnight timestamps & drop rows with invalid dates & examples: 2022-01-01 00:00:00 -> 2022-01-01 00:00:00

    # 3. Clean numeric columns & examples: 1,234,567.89 -> 1234567.89
    numeric_cols = ['Opening Balance (ml)', 'Purchase (ml)', 'Consumed (ml)', 'Closing Balance (ml)']
    for col in numeric_cols: # iterate over numeric columns
        if col in df.columns: # check if column exists
            # Remove commas and whitespace, coerce to numeric (handles scientific notation)
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce') # convert to numeric & examples: 1,234,567.89 -> 1234567.89
        else: # if column doesn't exist, create it with 0s
            df[col] = 0.0

    # 4. Replace NaN with 0 & examples: NaN -> 0
    df[numeric_cols] = df[numeric_cols].fillna(0.0)

    # 5. Convert very small floats to 0 (these are CSV artifacts like 1.71E-13) & examples: 1.71E-13 -> 0
    for col in numeric_cols:
        df.loc[df[col].abs() < zero_threshold, col] = 0.0 # convert very small floats to 0

    # 6. Clip negative consumptions to 0 (data error) & examples: -1 -> 0
    df['Consumed (ml)'] = df['Consumed (ml)'].clip(lower=0)

    # 7. Aggregate to Daily level: sum of consumed, purchases; opening first, closing last & examples:
    daily_df = df.groupby(['Date', 'Bar Name', 'Alcohol Type', 'Brand Name'], as_index=False).agg({
        'Consumed (ml)': 'sum', # sum of consumed
        'Opening Balance (ml)': 'first',  # approximation
        'Purchase (ml)': 'sum', # sum of purchases
        'Closing Balance (ml)': 'last' # last closing balance
    })

    # Sort for reproducibility
    daily_df.sort_values(by=['Bar Name', 'Brand Name', 'Date'], inplace=True) # sort for reproducibility
    daily_df.reset_index(drop=True, inplace=True) # reset index

    print(f"Data loaded. Raw rows: {len(df)} -> Aggregated daily rows: {len(daily_df)}") # print summary
    return daily_df   # return processed data

# run as script
if __name__ == "__main__":
    FILE_PATH = "Copy of Consumption Dataset - Dataset.csv" # file path
    try:
        df = load_and_process_data(FILE_PATH) # load and process data
        print(df.head()) # print first 5 rows
        print(df.info()) # print info
    except Exception as e: # catch any errors
        print(f"Error: {e}") 
