# 🍸 Hotel Bar Inventory Optimization System

> **Data-driven inventory planning to eliminate stockouts and reduce overstocking across multi-location hotel bars.**

---

## 📌 Problem Statement

Hotel bars face two costly problems:

- ❌ **Stockouts** → Lost sales of popular drinks.
- ❌ **Overstocking** → Locked capital, spoilage, and wasted storage.

Manual estimation of inventory levels doesn’t scale across multiple bars and brands.

This project introduces a **statistical, automated inventory optimization system** that calculates scientifically-derived **Par Levels** and validates them using historical backtesting.

---

## 🎯 Solution Overview

The system uses **historical consumption data** to:

- Forecast **Average Daily Usage (ADU)**
- Account for **demand variability**
- Maintain a **95% service level**
- Validate recommendations through **simulation**

### Key Outcomes
✔ Fewer stockout days  
✔ Lower excess inventory  
✔ Data-backed reorder decisions  
✔ Scalable across multiple bar locations  

---

## 🧩 System Architecture

The project is divided into **three modular components**:

### 1️⃣ Data Loader  
Prepares raw data for analysis.

**Responsibilities**
- Load raw CSV consumption data
- Normalize column names
- Handle missing / invalid values
- Aggregate usage at `(Date, Bar, Brand)` level

📄 **File**: `data_loader.py`

---

### 2️⃣ Forecasting Model (Core Engine)

Calculates optimal **Par Levels** using statistical inventory control theory.

**Calculations**
- Average Daily Usage (ADU)
- Demand standard deviation
- Safety stock
- Final Par Level (in ml)

📄 **File**: `forecast_model.py`  
📤 **Output**: `recommended_par_levels.csv`

---

### 3️⃣ Inventory Simulator (Backtesting)

Validates the effectiveness of the recommended Par Levels by replaying historical demand.

**Simulation Features**
- Daily inventory consumption
- Reorder trigger at **50% of Par Level**
- 3-day supplier lead time
- Tracks stockout days
- Calculates achieved **Service Level**

📄 **File**: `simulator.py`

---

## 📁 Project Structure

```
├── data_loader.py
├── forecast_model.py
├── simulator.py
├── recommended_par_levels.csv
├── Copy of Consumption Dataset - Dataset.csv
└── README.md
```

---

## 🧠 Inventory Optimization Logic

### 📐 Par Level Formula

```
Par Level = (Average Daily Demand × Lead Time) + Safety Stock
```

#### Parameters Used
| Parameter | Value | Reason |
|--------|------|-------|
| Lead Time | 3 Days | Typical supplier turnaround |
| Z-Score | 1.65 | Targets ~95% service level |
| Safety Stock | Z × σ × √LeadTime | Covers demand variability |

---

### 🛡 Safety Stock Formula

```
Safety Stock = Z_score × StdDev(Demand) × sqrt(Lead Time)
```

This ensures inventory can handle **unexpected spikes in demand** without frequent stockouts.

---

## 🔄 Simulation & Validation

The simulator runs a **day-by-day replay** of historical consumption:

1. Deduct daily consumption
2. Trigger reorder when inventory < 50% of Par
3. Restock after 3-day lead time
4. Track unmet demand
5. Compute final **Service Level**

✅ A service level above **95%** confirms model reliability.

---

## ⚙️ How to Run the Project

### ✅ Prerequisites

- Python 3.x
- pandas
- numpy

```bash
python3 -m pip install pandas numpy
```

---

### ▶️ Step 1: Generate Par Level Recommendations

```bash
python3 forecast_model.py
```

📄 Output file:
```
recommended_par_levels.csv
```

---

### ▶️ Step 2: Validate with Simulation

```bash
python3 simulator.py
```

📊 Terminal Output Example:
```
Service Level Achieved: 97.10%
```

---

## 📊 Output Interpretation

Example from `recommended_par_levels.csv`:

| Bar Name | Brand Name | Par Level (ml) | Operational Meaning |
|--------|-----------|---------------|---------------------|
| Taylor's Bar | Budweiser | 1696 | Keep ~1.7L (~5–6 bottles) |
| Ocean Lounge | Jack Daniels | 2450 | Maintain higher buffer due to demand variability |

📌 **Note**  
Par levels are expressed in **milliliters** for precision.  
For operations, consider rounding to standard bottle sizes (e.g., 750 ml).

---

## 🚀 Future Enhancements

- 📈 Time-series forecasting (ARIMA / Prophet)
- 🏨 Seasonal & event-based demand modeling
- 🧮 Dynamic reorder points instead of fixed 50%
- 📊 Dashboard visualization (Power BI / Tableau / Streamlit)
- ☁️ Cloud deployment & automated data ingestion

---

## 💼 Ideal Use Cases

- Hotel chains with multiple bars
- Restaurants & lounges
- Liquor distribution planning
- Inventory analytics portfolios
- Supply chain optimization case studies

---

## 🏁 Final Note

This project demonstrates **real-world inventory optimization**, combining:
- Statistics
- Data engineering
- Simulation
- Business impact analysis

Perfect for **data science**, **analytics**, and **supply-chain engineering** portfolios.
