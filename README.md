# Hotel Bar Inventory Optimization System

## 1. Project Overview
This project is an automated inventory management system designed for a hotel chain with multiple bar locations. It solves the problem of **stockouts** (running out of popular items) and **overstocking** (wasting space/cash on slow movers) by using historical data to scientifically calculate "Par Levels" (target inventory levels).

The system consists of three main components:
1.  **Data Loader**: Cleans and aggregates raw transaction data.
2.  **Forecasting Model**: Calculates recommended Par Levels based on consumption variance and safety stock targets.
3.  **Simulator**: Backtests the recommended levels against history to verify their effectiveness (Service Level).

---

## 2. File Structure
- `data_loader.py`: Script to ingest the raw CSV, clean column names, handling missing values, and aggregate usage to a `(Date, Bar, Brand)` level.
- `forecast_model.py`: The core logic. Calculates Average Daily Usage (ADU), Standard Deviation, and ultimately the **Par Levels**.
    - **Output**: `recommended_par_levels.csv`
- `simulator.py`: A virtual environment that "replays" the past sales history using the new Par Levels to measure performance (Stockouts vs Inventory Held).
- `recommended_par_levels.csv`: The final actionable report containing the specific milliliter quantity to stock for each item at each bar.
- `Copy of Consumption Dataset - Dataset.csv`: The input historical data source.

---

## 3. Methodology & Logic

### A. Forecasting Approach
We use a **statistical inventory control** method suitable for items with variable demand:

> **Par Level = (Daily Demand × Lead Time) + Safety Stock**

-   **Daily Demand**: Average Daily Usage (ADU) calculated from history.
-   **Lead Time**: Assumed to be **3 Days** (time between ordering and receiving).
-   **Safety Stock**: Buffer inventory to protect against demand spikes.
    -   Formula: `Z_score × StdDev_Demand × sqrt(Lead_Time)`
    -   We use a **Z-score of 1.65**, targeting a **95% Service Level** (probability of NOT running out of stock during replenishment).

### B. Simulation Logic
To validate the numbers, the simulator runs through the historical dates day-by-day:
1.  **Sales Decrement**: Deduction of `Consumed (ml)` from inventory.
2.  **Reordering**: When inventory drops below 50% of the Par Level (Reorder Point), an order is placed.
3.  **Restocking**: Order arrives after 3 days (Lead Time).
4.  **Metric Tracking**: Counts how many days demand could not be met (Stockout Days).

---

## 4. How to Run

### Prerequisites
You need Python 3 and pandas installed.
```bash
python3 -m pip install pandas numpy
```

### Step 1: Generate Recommendations
Run the forecasting model. This reads the dataset, performs the math, and saves the results.
```bash
python3 forecast_model.py
```
**Output**: A file named `recommended_par_levels.csv` will be created in the folder.

### Step 2: Validate with Simulation
Run the simulator to see how these Par Levels perform in practice.
```bash
python3 simulator.py
```
**Output**: The script will print the **Service Level** (e.g., 97.10%) to the terminal. A high service level (>95%) indicates the system is working as intended.

---

## 5. Interpreting Results
Open `recommended_par_levels.csv` to see the targets.

| Bar Name | Brand Name | Par Level (ml) | Interpretation |
| :--- | :--- | :--- | :--- |
| Taylor's Bar | Budweiser | 1696.0 | Keep ~1.7 Liters (approx 5-6 bottles) on hand. |
| ... | ... | ... | ... |

**Note**: The system outputs Par Levels in **ml** (Milliliters) to match the input data precision. You may wish to rounded this to the nearest bottle size (e.g., / 750ml) for operational simplicity.
