"""
RFM-style Customer Segmentation
--------------------------------
Extends the Customer_Behavior_Analysis project with a Recency-Frequency-Monetary
(RFM) segmentation.

NOTE on Recency: this dataset (Kaggle "Customer Shopping Trends") does not
include a transaction date/timestamp, so a true "days since last purchase"
Recency cannot be computed. Instead we use `Frequency of Purchases`
(e.g. "Weekly", "Annually") as a documented RECENCY PROXY — mapping each
category to an estimated typical gap (in days) between purchases for that
customer. This is a reasonable, explainable substitute and should be
described as such in the write-up / interview (don't call it literal
recency).

  R (Recency proxy) <- estimated days between purchases (lower = more active)
  F (Frequency)      <- Previous Purchases (actual count, higher = more frequent)
  M (Monetary)       <- Purchase Amount (USD) (higher = more valuable)
"""

import pandas as pd
import numpy as np

pd.set_option("display.width", 120)

df = pd.read_csv("customer_shopping_behavior.csv")
df.columns = [c.strip().lower().replace(" ", "_").replace("(usd)", "").strip("_") for c in df.columns]

# ---- 1. Recency proxy: map purchase-frequency category -> estimated days ----
freq_to_days = {
    "Weekly": 7,
    "Fortnightly": 14,
    "Bi-Weekly": 14,
    "Monthly": 30,
    "Every 3 Months": 90,
    "Quarterly": 90,
    "Annually": 365,
}
df["recency_proxy_days"] = df["frequency_of_purchases"].map(freq_to_days)
print("Unmapped frequency categories (check spelling):",
      df.loc[df["recency_proxy_days"].isna(), "frequency_of_purchases"].unique())

# ---- 2. Build RFM table (one row per customer already, but keep it explicit) ----
rfm = df[["customer_id", "recency_proxy_days", "previous_purchases", "purchase_amount"]].copy()
rfm.columns = ["customer_id", "R_days", "F_count", "M_amount"]

# ---- 3. Score each dimension 1-5 using quintiles ----
# Lower R_days = better (more frequent shopper) -> reverse the labels.
# R_days only has ~7 distinct category values, so rank-based qcut (not raw
# value qcut) is used to still get 5 balanced bins without duplicate-edge errors.
rfm["R_score"] = pd.qcut(rfm["R_days"].rank(method="first", ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["F_score"] = pd.qcut(rfm["F_count"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["M_amount"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

# ---- 4. Segment customers based on combined score ----
def segment(row):
    s = row["RFM_score"]
    if s >= 13:
        return "Champions"
    elif s >= 10:
        return "Loyal Customers"
    elif s >= 7:
        return "Potential Loyalists"
    elif s >= 5:
        return "At Risk"
    else:
        return "Low Value / Churn Risk"

rfm["segment"] = rfm.apply(segment, axis=1)

# ---- 5. Summary stats for the write-up ----
print("\n=== Segment counts ===")
print(rfm["segment"].value_counts())

print("\n=== Avg monetary value & count by segment ===")
summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"),
    avg_purchase_amount=("M_amount", "mean"),
    avg_previous_purchases=("F_count", "mean"),
    total_revenue_proxy=("M_amount", "sum"),
).sort_values("total_revenue_proxy", ascending=False)
summary["pct_of_customers"] = (summary["customers"] / len(rfm) * 100).round(1)
summary["pct_of_revenue_proxy"] = (summary["total_revenue_proxy"] / summary["total_revenue_proxy"].sum() * 100).round(1)

# Round for a clean CSV/README display (GitHub's CSV viewer doesn't wrap long
# decimals, so unrounded floats make the table look congested/overlapping)
summary["avg_purchase_amount"] = summary["avg_purchase_amount"].round(2)
summary["avg_previous_purchases"] = summary["avg_previous_purchases"].round(2)
summary["total_revenue_proxy"] = summary["total_revenue_proxy"].round(0).astype(int)

print(summary.round(2))

rfm.to_csv("rfm_segments.csv", index=False)
summary.to_csv("rfm_segment_summary.csv")
print("\nSaved rfm_segments.csv and rfm_segment_summary.csv")
