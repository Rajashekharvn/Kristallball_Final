# data_loader.py
import pandas as pd #import pandas as pd
import os #import os
import numpy as np #import numpy as np

def load_and_process_data(filepath, zero_threshold=1e-6):

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)

    # clean up column names
    df.columns = [c.strip() for c in df.columns]

    # parse dates and drop invalid rows
    df['Date Time Served'] = pd.to_datetime(df['Date Time Served'], errors='coerce')
    df = df.dropna(subset=['Date Time Served'])
    df['Date'] = df['Date Time Served'].dt.normalize()

    # clean numeric columns usually containing commas
    numeric_cols = ['Opening Balance (ml)', 'Purchase (ml)', 'Consumed (ml)', 'Closing Balance (ml)']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0.0

    df[numeric_cols] = df[numeric_cols].fillna(0.0)

    # fix scientific notation artifacts
    for col in numeric_cols:
        df.loc[df[col].abs() < zero_threshold, col] = 0.0

    # clip negative consumption
    df['Consumed (ml)'] = df['Consumed (ml)'].clip(lower=0)

    # Aggregate to Daily level
    daily_df = df.groupby(['Date', 'Bar Name', 'Alcohol Type', 'Brand Name'], as_index=False).agg({
        'Consumed (ml)': 'sum',
        'Opening Balance (ml)': 'first',
        'Purchase (ml)': 'sum',
        'Closing Balance (ml)': 'last'
    })

    daily_df.sort_values(by=['Bar Name', 'Brand Name', 'Date'], inplace=True)
    daily_df.reset_index(drop=True, inplace=True)

    print(f"Data loaded. Raw rows: {len(df)} -> Aggregated daily rows: {len(daily_df)}")
    return daily_df

# run as script
if __name__ == "__main__":
    FILE_PATH = "Copy of Consumption Dataset - Dataset.csv" # file path
    try:
        df = load_and_process_data(FILE_PATH) # load and process data
        print(df.head()) # print first 5 rows
        print(df.info()) # print info
    except Exception as e: # catch any errors
        print(f"Error: {e}")
