# 🛍️ Customer Shopping Behavior Analysis

An end-to-end data analytics project analyzing retail customer shopping behavior using **Python, PostgreSQL, SQL, and Power BI** — from data cleaning and feature engineering to SQL-based business analysis and an interactive dashboard.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Dataset](#-dataset)
- [Tech Stack](#️-tech-stack)
- [Project Workflow](#-project-workflow)
- [Project Steps](#-project-steps)
- [Key Business Questions & Results](#-key-business-questions--results)
- [Dashboard](#-dashboard)
- [Key Insights](#-key-insights)
- [Business Recommendations](#-business-recommendations)
- [Project Deliverables & Structure](#-project-deliverables--structure)
- [How to Run](#-how-to-run)
- [Author](#-author)

---

## 📖 Overview

Retail businesses generate large volumes of transaction data, but raw data alone doesn't drive decisions — it needs to be cleaned, analyzed, and visualized. This project takes a **Customer Shopping Behavior dataset** through a full analytics pipeline: preprocessing and EDA in Python, structured business analysis in PostgreSQL via SQL, and an interactive Power BI dashboard for stakeholders to explore.

---

## 📂 Dataset

| Attribute | Details |
|---|---|
| Dataset Name | Customer Shopping Behavior Dataset |
| Domain | Retail Analytics |
| Records | 3,900 |
| Columns | 18 |
| Format | CSV |

**Features:** Customer demographics (age, gender, location), purchase history (item, category, amount), product attributes (size, color, season), review ratings, subscription status, payment & shipping method, discount/promo usage, purchase frequency, and previous purchase count.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python / Pandas | Data loading, cleaning, EDA, feature engineering |
| PostgreSQL | Storage and management of processed data |
| SQL (pgAdmin) | Business analysis and querying |
| SQLAlchemy | Python ↔ PostgreSQL connection |
| Power BI | Interactive dashboard and visualization |
| Jupyter Notebook | Development and documentation |

---

## 🔄 Project Workflow

```
Raw Dataset → Data Loading → Cleaning & Preprocessing → EDA
     → Feature Engineering → PostgreSQL → SQL Business Analysis
     → Power BI Dashboard → Business Insights & Recommendations
```

---

## 📌 Project Steps

### 1. Data Preprocessing
- Loaded data with Pandas; inspected structure with `df.info()` and `df.describe()`.
- Checked for missing values and duplicates.
- Only `Review Rating` had nulls (37 of 3,900 rows).

### 2. Feature Engineering
- Filled missing `Review Rating` values using the **median rating per product category**.
- Standardized all column names to `snake_case`.
- Created an `age_group` column (Young Adult / Adult / Middle-aged / Senior) via quartile binning.
- Converted `frequency_of_purchases` (e.g. "Weekly", "Annually") into a numeric `purchase_frequency_days` column.
- Dropped `promo_code_used` after confirming it was 100% identical to `discount_applied`.

### 3. Database Integration
- Connected Python to PostgreSQL with SQLAlchemy (`psycopg2` driver).
- Loaded the cleaned DataFrame into a `customer` table using `to_sql()`.
- Verified the import in pgAdmin before running analysis.

### 4. SQL Business Analysis
Ten structured queries answering real business questions — see results below.

### 5. Dashboard Development
Built an interactive Power BI dashboard with KPI cards, category/age breakdowns, and slicers.

---

## 📊 Key Business Questions & Results

| # | Question | Result |
|---|---|---|
| 1 | Revenue by gender | Male: **$157,890** · Female: **$75,191** |
| 2 | High-spending discount users | Multiple customers spent above the $59.76 average purchase amount while using a discount |
| 3 | Top 5 products by review rating | Gloves (3.86), Sandals (3.84), Boots (3.82), Hat (3.80), Skirt (3.78) |
| 4 | Standard vs Express shipping spend | Standard: $58.46 avg · Express: $60.48 avg |
| 5 | Subscribers vs non-subscribers | Non-subscribers: 2,847 customers, $170,436 total revenue · Subscribers: 1,053 customers, $62,645 total revenue |
| 6 | Products most dependent on discounts | Hat (50%), Sneakers (49%), Coat (49%), Sweater (48%), Pants (47%) |
| 7 | Customer segmentation (New/Returning/Loyal) | Loyal: 3,116 · Returning: 701 · New: 83 |
| 8 | Top 3 products per category | e.g. Clothing → Blouse, Pants, Shirt; Footwear → Sandals, Shoes, Sneakers |
| 9 | Do repeat buyers (>5 purchases) subscribe more? | No — 2,518 non-subscribers vs 958 subscribers among repeat buyers |
| 10 | Revenue by age group | Young Adult: $62,143 · Middle-aged: $59,197 · Adult: $55,978 · Senior: $55,763 |

Full query text is available in [`sql/business_queries.sql`](sql/business_queries.sql).

---

## 📈 Dashboard

The Power BI dashboard includes:
- KPI cards — total customers, average purchase amount, average review rating
- Revenue & sales breakdown by category and by age group
- Subscription status donut chart
- Interactive slicers: subscription status, gender, category, shipping type

*(Full dashboard walkthrough and screenshots are included in the [Project Report](report/Project_Report.pdf).)*

---

## 📊 Key Insights

- **Clothing** generated the highest revenue among all product categories.
- **Young Adult** customers contributed the highest overall revenue ($62,143).
- The majority (73%) of customers were **non-subscribers** — a clear growth opportunity.
- **Express shipping** customers spent slightly more on average than Standard shipping customers.
- **Loyal customers** (3,116) made up the largest segment by far, ahead of Returning (701) and New (83).

## 💡 Business Recommendations

- Introduce targeted subscription offers to convert non-subscribers.
- Focus marketing spend on top-performing categories (Clothing, Accessories).
- Reward loyal customers with exclusive discounts/loyalty programs.
- Promote highly-rated products (Gloves, Sandals, Boots) to drive engagement.
- Use the New/Returning/Loyal segmentation for personalized campaigns.

---

## 📄 Project Deliverables & Structure

```
Customer-Shopping-Behavior-Analysis/
│
├── data/
│   └── customer_shopping_behavior.csv
├── notebooks/
│   └── customer_shopping_behavior.ipynb
├── sql/
│   └── business_queries.sql
├── powerbi/
│   └── customer_dashboard.pbix
├── report/
│   └── Project_Report.pdf
├── presentation/
│   └── Project_Presentation.pdf
├── README.md
└── requirements.txt
```

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/customer-shopping-behavior-analysis.git
   cd customer-shopping-behavior-analysis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or individually:
   pip install pandas sqlalchemy psycopg2-binary
   ```

3. **Set up PostgreSQL**
   - Create a database (e.g. `customer_behavior`).
   - Update the connection details (`username`, `password`, `host`, `port`, `database`) in the notebook.

4. **Run the notebook**
   - Open `notebooks/customer_shopping_behavior.ipynb` in Jupyter.
   - Run all cells to clean the data and load it into PostgreSQL (`to_sql()`).

5. **Run the SQL analysis**
   - Open `sql/business_queries.sql` in pgAdmin (or your SQL client of choice) and execute against the `customer` table.

6. **Explore the dashboard**
   - Open `powerbi/customer_dashboard.pbix` in Power BI Desktop.

---

## 👨‍💻 Author

**Favaz Ahmed**
B.Tech Computer Science & Engineering, PES University, Bengaluru

📫 Connect: *[add your LinkedIn / portfolio / email here]*

---

## 📜 License

This project is open-sourced for learning and portfolio purposes. Feel free to fork and adapt — attribution appreciated.

If you found this project helpful, consider giving it a ⭐.
