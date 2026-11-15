USE ${hivevar:DATABASE};
SELECT seller_id, substr(order_date, 1, 4) AS year, COUNT(*) AS days,
       SUM(orders) AS orders, SUM(revenue_brl) AS total_revenue_brl,
       AVG(revenue_brl) AS mean_daily_revenue, MAX(revenue_brl) AS max_daily_revenue,
       MAX(peak_order_brl) AS peak_order_brl
FROM ${hivevar:TABLE}
GROUP BY seller_id, substr(order_date, 1, 4)
ORDER BY seller_id, year;
