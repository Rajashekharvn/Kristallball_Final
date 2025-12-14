# Project Overview & Interview Prep Guide

## 1. Technologies Used
This project utilizes a focused set of powerful Python libraries standard in data science and analytics:

*   **Python 3**: The core programming language.
*   **Pandas**: The primary tool for data manipulation. Used for reading CSVs (`read_csv`), cleaning data, handling dates (`to_datetime`), and performing aggregations (`groupby`).
*   **NumPy**: Used for numerical operations, specifically calculating square roots (`np.sqrt`) for safety stock formulas and handling rounding (`np.ceil`).
*   **CSV**: Standard file format for input data and output reports.

---

## 2. Key Python & Data Science Concepts
Be prepared to explain these concepts during an interview, as they are central to your code:

### A. Data Cleaning & Preprocessing (Pandas)
*   **ETL (Extract, Transform, Load)**: You built a `data_loader.py` script that acts as an ETL pipeline.
*   **Data Type Conversion**: converting strings to numbers (`pd.to_numeric`) and handling errors (`errors='coerce'`).
*   **Handling Missing Values**: Using `.fillna(0)` to replace missing numeric data with zeros (essential for sales data).
*   **Datetime Parsing**: Converting string dates to actual datetime objects allows for chronological sorting and operations.
*   **Aggregation**: Using `.groupby().agg()` to summarize transactional data into daily totals. This turns "row-per-sale" data into "row-per-day" data.

### B. Statistical Forecasting
*   **Descriptive Statistics**: You calculated the **Mean** (Average Daily Usage) and **Standard Deviation** (Volatility of demand).
*   **Normal Distribution**: The safety stock calculation assumes demand follows a normal curve.
*   **Z-Score**: You used a Z-score of **1.65** (corresponding to a 95% confidence interval/Service Level) to determine how much buffer stock is needed to cover demand spikes.

### C. Simulation Logic (Python Control Flow)
*   **Time-Series Simulation**: You wrote a loop that iterates through interactions day-by-day to mimic real-time passage.
*   **Dictionaries for Lookup**: You used a dictionary (`par_map`) for O(1) constant-time lookups of Par Levels during the simulation, which is much faster than filtering a DataFrame inside a loop.
*   **State Management**: Within the loop, you tracked variables that change over time (`current_inventory`, `pending_orders`). This demonstrates an understanding of how to manage state in an algorithm.

### D. Inventory Management Domain Knowledge
*   **Lead Time**: The delay between ordering and receiving (3 days).
*   **Safety Stock**: Extra stock held to mitigate risk of stockouts during Lead Time.
*   **Reorder Point**: The inventory level that triggers a new order (set to 50% of Par Level).

---

## 3. End-to-End Project Explanation
Here is the narrative of how the solution works, which you can use to walk an interviewer through the project:

### Step 1: Data Ingestion (`data_loader.py`)
The process begins by reading the raw transaction data (`csv`). The data contains messy artifacts like commas in numbers or inconsistent column names.
*   **Action**: The script cleans these headers and values.
*   **Transformation**: It aggregates the raw "per-drink" transactions into a daily summary. For example, instead of 50 rows saying "sold 1 Budweiser", we get 1 row saying "Date: Jan 1, Item: Budweiser, Total Consumed: 50".

### Step 2: Forecasting Par Levels (`forecast_model.py`)
Using the cleaned daily data, the system calculates the optimal inventory targets.
*   **Math**: It calculates the **Average Daily Usage (ADU)** and the **Standard Deviation** for every bar and brand combo.
*   **Formula**: It applies the standard inventory formula:
    > `Par Level = (ADU * Lead Time) + Safety Stock`
*   **Safety Stock**: Calculated as `1.65 * StdDev * sqrt(Lead Time)`. This statistically ensures we have enough stock to survive 95% of random demand spikes during the 3 days it takes for new stock to arrive.
*   **Output**: The results are saved to `recommended_par_levels.csv`.

### Step 3: Validation via Simulation (`simulator.py`)
To prove these numbers actually work before deploying them, we run a simulation.
*   **Setup**: The simulator starts with the recommended Par Level as the initial inventory.
*   **Loop**: It walks through history day-by-day.
    1.  **Deduct Sales**: It subtracts that day's actual sales from inventory.
    2.  **Check Stockout**: If inventory < 0, it records a "Stockout Day" and "Lost Sales".
    3.  **Reorder**: If inventory drops below 50% of the target, it places a virtual order.
    4.  **Restock**: 3 days later, that order is added to the inventory.
*   **Result**: It calculates a **Service Level** (percentage of days with no stockouts). If the Service Level is >95%, the model is validated.
