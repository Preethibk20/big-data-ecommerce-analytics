# Laptop Demo Guide

The Python preparation, MapReduce verification, and dashboard run natively on Windows, macOS, or Linux with Python 3.11+.

Place the extracted Olist dataset CSV files under `brazilian-ecommerce/`.

```powershell
python -m pip install -r requirements.txt
python -m ecommerce prepare --input "brazilian-ecommerce" --output "data/prepared/ecommerce"
python -m ecommerce analyze --daily "data/prepared/ecommerce/daily.tsv" --output "results/ecommerce"
python -m ecommerce dashboard --results "results/ecommerce"
```

### What Happens During Each Step

1. **Preparation (`prepare`)**:
   - Streams raw `olist_orders_dataset.csv` and `olist_order_items_dataset.csv`.
   - Filters out non-fulfilled orders (e.g. canceled).
   - Generates normalized `daily.tsv` containing 69,000+ daily seller transaction records.
   - Writes `manifest.json` with SHA-256 digests and row counts.

2. **Analysis (`analyze`)**:
   - Executes `mapreduce/mapper.py` and `mapreduce/reducer.py` locally through standard I/O streaming.
   - Computes an independent Python reference aggregation.
   - Cross-checks all seller/year groups, asserting identical row counts, revenues, and peak order metrics.
   - Emits `analytics.json` and `mapreduce.tsv`.

3. **Dashboard (`dashboard`)**:
   - Launches Flask at `http://127.0.0.1:5000`.
   - **Page 1**: Look up any seller ID (e.g., `53243585b1d7d780a402320474a15dac` or quick select chips). Compare annual shares using dynamic SVG pie slices and review annual revenue bars.
   - **Page 2**: Choose a year (2016, 2017, or 2018), ranking metric (Total Revenue, Orders, Mean Daily Revenue, Max Daily Revenue, Peak Order Value), and Top K (e.g., 10 or 25). Review highest vs lowest merchants and the complete leaderboard.

### Optional MongoDB Execution

With MongoDB running locally or via Docker (`.\scripts\start_mongo.ps1` on Windows or `scripts/start_mongo.sh` on Linux/macOS):

```powershell
# Import daily sales + enriched orders/reviews and run aggregation pipelines
python -m ecommerce mongo --daily "data/prepared/ecommerce/daily.tsv" --database ecommerce_olist --raw "brazilian-ecommerce"

# Profile indexed (IXSCAN) vs unindexed (COLLSCAN) queries and faceted pipelines
python -m ecommerce.mongo_profile --database ecommerce_olist --seller-id 4869f7a5dfa277a7dca6462dcf3b52b2 --output "results/mongodb-analytics.json"
```
