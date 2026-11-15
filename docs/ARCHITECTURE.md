# Architecture

## Dataset

The source is the Kaggle Brazilian E-Commerce Public Dataset by Olist. The dataset captures real commercial operations from 2016 to 2018 across Brazilian marketplaces.

Key raw tables utilized:
1. `olist_orders_dataset.csv`: Central transaction lifecycle table with `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`.
2. `olist_order_items_dataset.csv`: Line item details with `order_id`, `order_item_id`, `product_id`, `seller_id`, `price`, `freight_value`.
3. `olist_sellers_dataset.csv`: Merchant locations (`seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state`).

Data preparation filters out canceled and unavailable orders, associates valid order timestamps with their line items, and validates that item prices are finite and non-negative numbers in Brazilian Reais (R$).

## Processing Flow

```text
Kaggle Olist CSVs (orders, items)
  -> ecommerce.prepare: stream, validate, and write daily.tsv + manifest.json
  -> Python reference aggregation + Hadoop Streaming MapReduce cross-check
  -> optional MongoDB daily collection, indexed queries, and aggregation pipeline
  -> Apache Pig validation/cleaning -> Apache Hive Text and RCFile tables
  -> saved JSON/TSV results -> Flask analytics dashboard
```

The normalized TSV has six columns:

| Column | Type | Meaning |
|---|---|---|
| `date` | String (YYYY-MM-DD) | Purchase date of the transactions |
| `seller_id` | String (32 hex chars) | Unique merchant identifier |
| `orders` | Integer | Total items / orders sold on that date (>= 1) |
| `revenue_brl` | Float | Sum of item sales prices in Brazilian Reais (R$) |
| `mean_order_brl` | Float | Average order item value on that day (`revenue_brl / orders`) |
| `peak_order_brl` | Float | Maximum single order item value recorded that day |

The primary analytics grouping aggregates by `(seller_id, year)`:
- Active days with recorded sales (`days`)
- Total annual orders (`orders`)
- Total annual revenue (`revenue_brl`)
- Mean revenue per active day (`mean_daily_revenue`)
- Maximum single-day revenue (`max_daily_revenue`)
- Peak single item transaction value (`peak_order_brl`)

## Dashboard Pages

- **Page 1 · Seller Multi-Year Performance**: Look up any merchant by full ID or prefix. Displays cumulative revenue, items sold, active days, peak item price, an interactive SVG pie chart comparing yearly share across any selected metric, an annual revenue progression bar chart highlighting best and worst operating years, and a complete historical breakdown table.
- **Page 2 · Annual Seller Leaderboard**: Select a calendar year (2016, 2017, or 2018), ranking metric, and Top K. Displays featured KPI cards for the top and bottom merchants, an interactive comparison bar, and a ranked leaderboard table with quick-links to individual seller profiles.

## Distributed Tools

- **HDFS**: Stores the normalized daily sales TSV across cluster nodes.
- **YARN and Hadoop Streaming**: Executes `mapreduce/mapper.py` and `mapreduce/reducer.py` in parallel.
- **Apache Pig**: `pig/clean_daily.pig` validates data types and filters out nulls or invalid values.
- **Apache Hive**: `hive/tables.hql` manages external Text and RCFile tables; `hive/annual_seller_summary.hql` performs analytical SQL aggregations.
- **MongoDB**: `ecommerce_olist` database with compound indexes on `(seller_id, year)` and `(date)` for sub-millisecond query retrieval and analytical pipeline aggregation.
- **Flask**: Lightweight, dependency-free web server serving saved analytics.
