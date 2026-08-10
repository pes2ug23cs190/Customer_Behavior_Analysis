-- =========================================================
-- RFM-style Customer Segmentation (PostgreSQL)
-- =========================================================
-- NOTE: this dataset has no transaction date, so true "Recency"
-- (days since last purchase) is not available. `recency_proxy_days`
-- instead estimates typical days-between-purchases from the
-- categorical `frequency_of_purchases` column. It is a documented
-- proxy, not a literal recency value.

WITH base AS (
    SELECT
        customer_id,
        previous_purchases                                   AS f_count,
        purchase_amount                                       AS m_amount,
        CASE frequency_of_purchases
            WHEN 'Weekly'          THEN 7
            WHEN 'Fortnightly'     THEN 14
            WHEN 'Bi-Weekly'       THEN 14
            WHEN 'Monthly'         THEN 30
            WHEN 'Every 3 Months'  THEN 90
            WHEN 'Quarterly'       THEN 90
            WHEN 'Annually'        THEN 365
        END                                                    AS r_days
    FROM customer
),
scored AS (
    SELECT
        customer_id,
        r_days,
        f_count,
        m_amount,
        NTILE(5) OVER (ORDER BY r_days DESC)  AS r_score,   -- lower r_days => higher score
        NTILE(5) OVER (ORDER BY f_count ASC)  AS f_score,
        NTILE(5) OVER (ORDER BY m_amount ASC) AS m_score
    FROM base
),
final AS (
    SELECT
        *,
        (r_score + f_score + m_score) AS rfm_score,
        CASE
            WHEN (r_score + f_score + m_score) >= 13 THEN 'Champions'
            WHEN (r_score + f_score + m_score) >= 10 THEN 'Loyal Customers'
            WHEN (r_score + f_score + m_score) >= 7  THEN 'Potential Loyalists'
            WHEN (r_score + f_score + m_score) >= 5  THEN 'At Risk'
            ELSE 'Low Value / Churn Risk'
        END AS segment
    FROM scored
)
SELECT
    segment,
    COUNT(*)                                   AS customers,
    ROUND(AVG(m_amount)::numeric, 2)           AS avg_purchase_amount,
    ROUND(AVG(f_count)::numeric, 2)            AS avg_previous_purchases,
    SUM(m_amount)                               AS total_revenue_proxy,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct_of_customers,
    ROUND(100.0 * SUM(m_amount) / SUM(SUM(m_amount)) OVER (), 1) AS pct_of_revenue_proxy
FROM final
GROUP BY segment
ORDER BY total_revenue_proxy DESC;
