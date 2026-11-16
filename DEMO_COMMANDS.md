# Live Demo & Evaluation Cheatsheet (VS Code)

This document contains every command in execution order for your live demonstration to faculty.  
Open this file in VS Code (`Ctrl+Shift+V` to preview) and copy-paste each command into your VS Code Terminal.

---

## 0. Prerequisite Setup (Before Calling Faculty)

Make sure **Docker Desktop** is running, open your VS Code terminal, and run:

```powershell
cd "c:\Users\Preethi\OneDrive\Downloads\engineering\7th sem\4 big data analytics\bda-master\bda-master"

# Ensure all containers are running
docker start campushub_mongo ecommerce-sales-analytics-master-1 ecommerce-sales-analytics-worker1-1 ecommerce-sales-analytics-worker2-1
```

---

## Step 1: Run the Test Suite (Proof of System Integrity)

### Command to Copy:
```powershell
python -m unittest discover -s tests -v
```

### Expected Output:
```text
test_bad_price_raises_error ... ok
test_dashboard_validation_and_errors ... ok
test_preparation_analysis_and_dashboard ... ok
test_compare_index_performance_computes_reduction_and_speedup ... ok
test_execution_summaries_include_nested_aggregation_stats ... ok
test_faceted_and_order_pipelines_cover_required_stages ... ok
test_import_and_profile_end_to_end_with_mock_client ... ok
test_profile_validates_arguments_before_connecting ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.640s

OK
```

### What to Say to Faculty:
> *"Here we run our automated unit test suite. All 8 tests pass, confirming that input validation, MongoDB multi-stage aggregation pipelines, and query index profiling calculations match the assignment specifications."*

---

## Step 2: Theme 1 — MongoDB Big Data Processing & Query Profiling

### Part A: Show Ingested Collections & Document Counts
### Command to Copy:
```powershell
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); db = client['ecommerce_olist']; print('Collections:', db.list_collection_names()); print('daily_sales docs:', db.daily_sales.count_documents({})); print('orders_enriched docs:', db.orders_enriched.count_documents({}))"
```

### Expected Output:
```text
Collections: ['daily_sales', 'orders_enriched']
daily_sales docs: 69065
orders_enriched docs: 99441
```

### What to Say to Faculty:
> *"We ingested the Olist dataset into MongoDB. `daily_sales` has 69,065 transaction documents, and `orders_enriched` has 99,441 documents containing nested arrays of order items and customer review scores."*

---

### Part B: Execute Multi-Stage Pipeline (`$match`, `$unwind`, `$facet`, `$group`)
### Command to Copy:
```powershell
python -c "from pymongo import MongoClient; from ecommerce.mongo import build_order_items_pipeline; client = MongoClient('mongodb://localhost:27017'); db = client['ecommerce_olist']; res = list(db.orders_enriched.aggregate(build_order_items_pipeline(), allowDiskUse=True)); print('Top Sellers:', res[0]['seller_item_totals'][:2]); print('Review Summary:', res[0]['review_score_summary'])"
```

### Expected Output:
```text
Top Sellers: [{'items_sold': 1155, 'total_price_brl': 229237.63, 'total_freight_brl': 20155.81, 'seller_id': '4869f7a5dfa277a7dca6462dcf3b52b2'}, {'items_sold': 410, 'total_price_brl': 222776.05, 'total_freight_brl': 13080.63, 'seller_id': '53243585a1d6dc2643021fd1853d8905'}]
Review Summary: [{'item_count': 63107, 'avg_item_price_brl': 121.38860633527185, 'review_score': 5}, {'item_count': 21188, 'avg_item_price_brl': 118.71550783462338, 'review_score': 4}, {'item_count': 9336, 'avg_item_price_brl': 109.92101542416452, 'review_score': 3}, {'item_count': 3810, 'avg_item_price_brl': 115.49803937007874, 'review_score': 2}, {'item_count': 13735, 'avg_item_price_brl': 125.95596214051692, 'review_score': 1}]
```

### What to Say to Faculty:
> *"This pipeline uses `$unwind` on the embedded items array to flatten product records, then `$facet` concurrently computes two analytics streams: top sellers by total revenue, and review distribution from 1 to 5 stars."*

---

### Part C: Query Profiling (`COLLSCAN` vs `IXSCAN` Indexing)
### Command to Copy:
```powershell
python -m ecommerce.mongo_profile --seller-id "4869f7a5dfa277a7dca6462dcf3b52b2" --output "results/mongodb-analytics.json"
```

### Expected Output (look for `index_comparison` at top/middle):
```json
"index_comparison": {
  "unindexed_docs_examined": 22973,
  "indexed_docs_examined": 100,
  "docs_examined_reduction_ratio": 229.73,
  "unindexed_time_ms": 10,
  "indexed_time_ms": 5,
  "speedup_ratio": 2.0
}
```

### What to Say to Faculty:
> *"Here we profile query performance with `.explain('executionStats')`. Without an index (`COLLSCAN`), MongoDB scanned 22,973 documents. With our compound index on `(seller_id, year)` (`IXSCAN`), it examined only 100 documents — a 229.7x reduction in scanned documents."*

---

## Step 3: Theme 2 — Hadoop File Management & MapReduce Analytics

### Part A: Cluster Health Check (Active DataNodes)
### Command to Copy:
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfsadmin -report | grep 'Live datanodes'"
```

### Expected Output:
```text
Live datanodes (2):
```

### What to Say to Faculty:
> *"This proves our distributed 3-node Hadoop cluster is healthy, running 1 master and 2 live worker DataNodes with safe mode OFF."*

---

### Part B: HDFS Lifecycle Operations (`-mkdir`, `-put`, `-cat`, `-get`, `-rm -r`)
### Command to Copy:
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -rm -r -skipTrash /user/root/ecommerce/live_eval_run 2>/dev/null || true; /project/scripts/hdfs_demo.sh /project/data/prepared/ecommerce/daily.tsv /project/data/prepared/ecommerce /user/root/ecommerce/live_eval_run"
```

### Expected Output:
```text
Ecommerce HDFS round-trip verification
Deleted /user/root/ecommerce/live_eval_run/demo
drwxr-xr-x   - root supergroup          0 /user/root/ecommerce/live_eval_run/prepared
-rw-r--r--   2 root supergroup    4285661 /user/root/ecommerce/live_eval_run/prepared/daily.tsv
-rw-r--r--   2 root supergroup       1117 /user/root/ecommerce/live_eval_run/prepared/manifest.json
drwxr-xr-x   - root supergroup          0 /user/root/ecommerce/live_eval_run/raw
-rw-r--r--   2 root supergroup    4285661 /user/root/ecommerce/live_eval_run/raw/daily.tsv
```

### What to Say to Faculty:
> *"This script demonstrates the complete HDFS lifecycle: directory creation with `-mkdir -p`, uploading data blocks with `-put`, inspecting streams with `-cat`, round-trip file verification with `-get` and `cmp`, and directory cleanup with `-rm -r`."*

---

### Part C: Run Distributed MapReduce on YARN
### Command to Copy:
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -rm -r -skipTrash /user/root/ecommerce/mr_eval_out 2>/dev/null || true; /project/scripts/run_mapreduce.sh /user/root/ecommerce/live_eval_run/prepared/daily.tsv /user/root/ecommerce/mr_eval_out 2"
```

### Expected Output:
```text
INFO mapreduce.Job: Running job: job_XXXXXXXXXX
...
	Map input records=69065
	Map output records=69065
	Reduce input groups=4254
	Reduce output records=4254
	Bytes Written=316212
Output directory: /user/root/ecommerce/mr_eval_out
```

### What to Say to Faculty:
> *"Here Hadoop Streaming executes our Python mapper and reducer across 2 reducers on YARN. The mapper processes 69,065 daily records, partitions by `(seller_id, year)`, and the reducers aggregate them into 4,254 annual merchant summaries written to HDFS."*

---

## Step 4: Theme 3 — Apache Pig & Apache Hive RCFile Performance

### Part A: Pig Latin Data Cleaning Pipeline
### Command to Copy:
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -rm -r -skipTrash /user/root/ecommerce/pig_eval_out 2>/dev/null || true; pig -x mapreduce -param INPUT=/user/root/ecommerce/live_eval_run/prepared/daily.tsv -param OUTPUT=/user/root/ecommerce/pig_eval_out /project/pig/clean_daily.pig"
```

### Expected Output:
```text
Successfully read 69065 records (4286058 bytes)
Successfully stored 69065 records (4401177 bytes) in: "/user/root/ecommerce/pig_eval_out"
Pig script completed in 19 seconds
```

### What to Say to Faculty:
> *"Our Pig Latin script enforces schema integrity on MapReduce: it validates date formats using regex `\\d{4}-\\d{2}-\\d{2}`, ensures seller IDs are non-empty, and filters out negative revenues, producing clean data for Hive."*

---

### Part B: Hive Table Comparison (Text vs Columnar RCFile Benchmark)
### Command to Copy:
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "beeline -u jdbc:hive2://localhost:10000/ecommerce_analytics -n root -e 'SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev FROM daily_text GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5; SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev FROM daily_rcfile GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5;'"
```

### Expected Output:
```text
+-----------------------------------+-------+------------+
|             seller_id             | days  | total_rev  |
+-----------------------------------+-------+------------+
| 4869f7a5dfa277a7dca6462dcf3b52b2  | 358   | 229237.63  |
| 53243585a1d6dc2643021fd1853d8905  | 150   | 222776.05  |
| 4a3ca9315b744ce9f8e9374361493884  | 537   | 200326.12  |
| fa1c13f2614d7b5c4749cbc52fecda94  | 341   | 192842.13  |
| 7c67e1448b00f6e969d365cea6b010ab  | 375   | 187923.89  |
+-----------------------------------+-------+------------+
...
Query 1 (daily_text): ~130 seconds
Query 2 (daily_rcfile): ~90 seconds
```

### What to Say to Faculty:
> *"We execute the exact same analytical aggregation on both tables. Both return identical top sellers, but RCFile achieves a 78.71% disk storage reduction (937 KB vs 4.4 MB) and runs ~40 seconds faster (1.45x speedup) because RCFile is columnar and only decompresses queried columns."*

---

## Step 5: Web Visualisation Dashboard (Flask)

### Command to Copy:
```powershell
python -m ecommerce dashboard --results results/ecommerce
```

### What to Show in Browser (`http://localhost:5000`):
1. **Page 1 (Seller Deep-Dive):**
   - Click on the top seller or search `4869f7a5dfa277a7dca6462dcf3b52b2`.
   - Point out the **multi-year revenue trend**, the **SVG pie chart**, and the **annual bar chart**.
2. **Page 2 (Annual Leaderboard):**
   - Click the top navigation link for **Annual Leaderboard** (or visit `http://localhost:5000/?page=year&year=2018`).
   - Show the ranking of merchants by revenue tiers for year 2018.

---

## Quick Reference / Viva Cheat Sheet

| Question | What to answer / point to |
| :--- | :--- |
| *Where are your reports?* | Open `results/Assignment_1_Report.pdf` (9 pages) and `results/Assignment_2_Report.pdf` (7 pages). |
| *Where is your GitHub repo?* | Open [https://github.com/Preethibk20/big-data-ecommerce-analytics](https://github.com/Preethibk20/big-data-ecommerce-analytics). |
| *Why use RCFile over Text in Hive?* | RCFile stores data in column stripes with Gzip compression. It saves 78.7% disk space and speeds up queries by skipping columns not in the query. |
| *What is the benefit of MongoDB compound index?* | Scans only matching B-tree keys (`IXSCAN`) instead of doing a full collection table scan (`COLLSCAN`), examining 100 documents instead of 22,973. |
