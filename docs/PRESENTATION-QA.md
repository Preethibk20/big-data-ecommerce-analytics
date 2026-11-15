# Presentation Q&A: Brazilian E-Commerce (Olist) Analytics

## What does the dataset contain?

It is the Kaggle Brazilian E-Commerce Public Dataset by Olist: 100,000 real orders placed between 2016 and 2018 across Brazilian marketplaces, linking customers, orders, item-level prices, and over 3,000 merchants.

## How is revenue calculated?

Each order contains one or more line items with price and freight in Brazilian Reais (R$). Daily revenue per seller is the sum of item prices sold by that merchant on that day. Annual revenue is the annual sum across all active selling days.

## How are order statuses and missing values treated?

Orders marked as `canceled` or `unavailable` are filtered out during preparation so metrics reflect actual fulfilled commercial transactions. Blank prices, non-finite values, or negative figures are strictly rejected.

## Why use more than one big data tool?

- **Python**: Performs streaming ETL to normalize relational orders and line items into a daily TSV.
- **Hadoop MapReduce**: Distributes annual aggregations across worker nodes using standard key-value streaming (`mapper.py` and `reducer.py`).
- **Apache Pig**: Provides concise schema filtering and validation (`clean_daily.pig`).
- **Apache Hive**: Enables SQL queries on uncompressed Text and compressed RCFile tables (`tables.hql`, `annual_seller_summary.hql`).
- **MongoDB**: Offers document persistence with compound indexing (`seller_year`) and an aggregation pipeline for low-latency operational lookups.
- **Flask**: Serves clean, read-only visualization dashboards without mixing heavy compute with serving.

## How are merchants ranked?

On Page 2 of the dashboard, merchants are ranked within any active year (2016, 2017, or 2018) by Total Revenue, Total Orders, Mean Daily Revenue, Max Daily Revenue, or Peak Order Value, with ties broken consistently by Seller ID.
