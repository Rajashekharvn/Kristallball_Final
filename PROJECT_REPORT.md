# Hotel Bar Inventory Optimization - Project Report

## 1. Core Business Problem
**Problem**: Hotel bars face a constant optimization challenge:
*   **Stockouts**: Running out of high-demand items (e.g., a specific vodka or gin) leads to lost revenue and poor guest experience.
*   **Overstocking**: Holding too much inventory ties up working capital, clutters limited storage space, and increases the risk of wastage/shrinkage (theft or breakage).

**Why it matters**: In the hospitality industry, margins are thin. Optimizing inventory directly impacts profitability by freeing up cash flow and ensuring every potential sale can be fulfilled. A data-driven approach replaces "gut feeling" orders with statistically backed targets.

## 2. Assumptions Made
*   **Stationary Demand**: We assumed that historical daily consumption patterns are a reasonable predictor of future demand. *Why?* For established bars, consumption of core spirits is relatively stable over time.
*   **Fixed Lead Time (3 Days)**: We assumed a constant 3-day window between placing an order and receiving goods. *Why?* This simplifies the simulation. In reality, this could vary, but 3 days is a conservative average for local distributors.
*   **Target Service Level (95%)**: We aimed to be in-stock 95% of the time. *Why?* This is an industry standard balance—100% is too expensive (requires massive safety stock), and <90% risks frequent guest disappointment.
*   **Continuous Review / Daily granularity**: We assumed consumption is tracked daily. *Why?* POS systems provide this granularity, allowing for precise checking.

## 3. Model Selection
**Model Used**: **Par Level System** (also known as Min-Max or Periodic Review System).

**Formula**:
$$ \text{Par Level} = (\text{Avg Daily Usage} \times \text{Lead Time}) + \text{Safety Stock} $$

**Why this model?**
1.  **Industry Standard**: "Par Levels" are universally understood by bar staff and managers. Adoption requires zero training on complex algorithms.
2.  **Operational Simplicity**: It translates directly to a physical workflow: "Count what we have, order up to Par."
3.  **Robustness**: For items with stable demand (like standard spirits), this statistical approach matches or outperforms complex ML models which might overfit to noise in sparse data.

**Why not others (e.g., LSTM, Prophet)?**
*   Deep learning models require massive datasets and are "black boxes" to operations staff.
*   Time-series forecasting (ARIMA) handles seasonality better but adds complexity that may not yield ROI for low-volume items.

## 4. System Performance & Improvements
**Performance**:
*   The retrospective simulation demonstrated that the calculated Par Levels achieved a **Service Level of >95%** for the majority of items.
*   The system successfully handled peak demand days without stockouts due to the buffer provided by the Safety Stock.

**Improvements**:
*   **Seasonality**: The current model uses a global average. Implementing seasonal factors (e.g., higher Pars for December/Summer) would reduce stockouts during peak seasons and reduce holding costs in low seasons.
*   **Event Integration**: Ingesting hotel occupancy data or event calendars (weddings, conferences) to dynamically adjust Pars for specific weekends.

## 5. Real-World Implementation
**In a real hotel, this solution would fit into the weekly workflow:**

1.  **Automated Analysis**: Every Monday morning, the Python script runs on the latest POS data export.
2.  **Report Generation**: The system generates a "Recommended Par Level" sheet for the week.
3.  **Physical Count**: Bar staff perform their regular stock count.
4.  **Ordering**: The Purchasing Manager compares the physical count to the recommended Par.
    *   *Order Quantity = Recommended Par - Current Stock*
5.  **Feedback Loop**: Actual stockouts are logged to refine the Safety Stock settings for future weeks.
