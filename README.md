# Brazilian E-Commerce (Olist) Sales & Merchant Analytics

Big Data Analytics project using the [Kaggle Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
The dataset covers over 100,000 orders made at Olist Store from 2016 through 2018 across Brazilian marketplaces.

The project validates raw relational order and item records, converts them into normalized daily seller transaction summaries, and performs distributed annual aggregations across Python, MongoDB, Hadoop MapReduce, Apache Pig, and Apache Hive. A two-page interactive Flask dashboard enables users to inspect multi-year merchant trajectories and rank sellers across core business metrics.

---

## E-Commerce Data Interpretation

- **Orders & Items**: Orders represent purchases placed on the marketplace. Canceled and unavailable orders are filtered out; delivered, shipped, and invoiced orders are matched with order items.
- **Granular Daily Aggregations**: Individual order item transactions are streamed and aggregated at the daily grain per seller: total items sold, total revenue in Brazilian Reais (R$), mean order item price, and peak single item value.
- **Multi-Year Coverage**: Covers transactional history spanning 2016 through 2018 across 3,000+ active sellers.
- **Revenue Metric**: Prices are in Brazilian Reais (BRL / R$). Non-finite or negative values are rejected during validation.

---

## Dataset Setup & Quick Start (Local Python)

Requires Python 3.11 or newer. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

### 1. Dataset Location Setup (Run Once)

If `brazilian-ecommerce/` or `data/` is not in this directory, link to the existing dataset or copy the prepared records:

```powershell
# OPTION A: Create a directory junction to the existing raw dataset (instant, 0 disk space)
New-Item -ItemType Junction -Path "brazilian-ecommerce" -Target "..\bda-master\bda-master\brazilian-ecommerce"

# OPTION B: OR copy the pre-prepared daily.tsv and manifest.json directly
Copy-Item -Recurse "..\bda-master\bda-master\data" .
```

### 2. Prepare, Analyze, and Launch Dashboard

```powershell
# Step 1: Prepare and normalize daily seller records into data/prepared/ecommerce/
python -m ecommerce prepare --input "brazilian-ecommerce" --output "data/prepared/ecommerce"

# Step 2: Run MapReduce and cross-check against reference analytics locally
python -m ecommerce analyze --daily "data/prepared/ecommerce/daily.tsv" --output "results/ecommerce_run"

# Step 3: Launch the interactive analytics dashboard
python -m ecommerce dashboard --results "results/ecommerce"
```

Open `http://127.0.0.1:5000` in your browser:
- **Page 1 · Seller Multi-Year Performance**: Search any seller ID (e.g. `4869f7a5dfa277a7dca6462dcf3b52b2`). View cumulative metrics, annual progression, an interactive SVG pie chart comparing yearly shares, and a bar chart comparing annual totals.
- **Page 2 · Annual Seller Leaderboard**: Select a calendar year (2016, 2017, or 2018), ranking metric, and Top K. Highlights highest and lowest performing merchants and displays a clean, responsive leaderboard.

---

## Complete End-to-End Execution 

### Step 0: Start Environment & Docker Cluster

Start Docker Desktop, then spin up the multi-node containerized cluster from your terminal:

```powershell
docker compose -f infra/compose.yaml up -d
docker ps --format "table {{.Names}}\t{{.Status}}"
```

> **Explanation to Faculty:** Initialized a distributed 3-node Hadoop cluster using Docker Compose: 1 master (NameNode, ResourceManager, HiveServer2) and 2 workers (DataNodes, NodeManagers) on an isolated bridge network with replication factor 2.

---

### Step 1: Automated Unit Testing (System Verification)

```powershell
python -m unittest discover -s tests -v
```

**Expected Output:**
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
Ran 8 tests in 0.400s

OK
```

> **Explanation to Faculty:** All 8 unit tests pass, confirming schema validation, pipeline compilation, and profiler calculation accuracy prior to distributed processing.

---

### Step 2: Cluster Health Check (Multi-Node Distributed Proof)

```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfsadmin -report | grep 'Live datanodes'"
docker exec ecommerce-sales-analytics-master-1 bash -c "yarn node -list"
```

**Expected Output:**
```text
Live datanodes (2):
Total Nodes: 2 (worker1:8041 RUNNING, worker2:8041 RUNNING)
```

> **Explanation to Faculty:** Confirms the distributed cluster topology: HDFS has 2 active DataNodes with safe mode OFF, and YARN has 2 active worker NodeManagers ready to schedule distributed tasks.

---

### Step 3: Theme 1 — MongoDB Big Data Processing & Profiling

#### Part A: Ingested Document Counts
```powershell
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://127.0.0.1:27017'); db = client['ecommerce_olist']; print('Collections:', db.list_collection_names()); print('daily_sales docs:', db.daily_sales.count_documents({})); print('orders_enriched docs:', db.orders_enriched.count_documents({}))"
```

**Expected Output:**
```text
Collections: ['daily_sales', 'orders_enriched']
daily_sales docs: 69065
orders_enriched docs: 99441
```

> **Explanation to Faculty:** Ingested 69,065 daily seller transaction documents and 99,441 enriched orders containing embedded product items arrays and customer review ratings into MongoDB.

#### Part B: Execute MongoDB Compass & Atlas Aggregation Queries
```powershell
python scripts/run_atlas_compass_queries.py
```

> **Explanation to Faculty:** Executes the 8 MongoDB aggregation queries created in MongoDB Compass against database `OlistDB`: Delivered Orders Analysis, Multi-facet lifecycle breakdown (`$facet`), Payment Type analysis, Top 10 Seller States, Top 10 Customer States, Top 10 Orders by Item Value, Top 10 Product Categories, and Order Line Items analysis using `$unwind`.

#### Part C: Query Performance Profiling (`.explain("executionStats")`)
```powershell
python -m ecommerce.mongo_profile --database ecommerce_olist --seller-id "4869f7a5dfa277a7dca6462dcf3b52b2" --output "results/mongodb-analytics.json"
```

**Expected Index Comparison:**
```json
"index_comparison": {
  "unindexed_docs_examined": 22973,
  "indexed_docs_examined": 100,
  "docs_examined_reduction_ratio": 229.73,
  "unindexed_time_ms": 17,
  "indexed_time_ms": 3,
  "speedup_ratio": 5.67
}
```

> **Explanation to Faculty:** Unindexed lookup (`COLLSCAN`) requires scanning 22,973 documents. Compound index on `(seller_id, year)` (`IXSCAN`) examines only 100 documents — achieving a 229.7x reduction in examined documents and a 5.67x query speedup.

---

### Step 4: Theme 2 — HDFS Operations & Distributed MapReduce

#### Part A: Distributed HDFS Lifecycle Operations
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -mkdir -p /user/root/ecommerce/live_eval_run/prepared"
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -put -f /project/data/prepared/ecommerce/daily.tsv /user/root/ecommerce/live_eval_run/prepared/"
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -ls /user/root/ecommerce/live_eval_run/prepared"
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -cat /user/root/ecommerce/live_eval_run/prepared/daily.tsv | head -3"
```

#### Part B: Execute Distributed Python Streaming MapReduce on YARN
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -rm -r -f /user/root/ecommerce/mr_eval_out"
docker exec ecommerce-sales-analytics-master-1 bash -c "/project/scripts/run_mapreduce.sh /user/root/ecommerce/live_eval_run/prepared/daily.tsv /user/root/ecommerce/mr_eval_out 2"
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -cat /user/root/ecommerce/mr_eval_out/part-* | head -4"
```

> **Explanation to Faculty:** Python Streaming MapReduce executed on YARN across 2 reducers. The mapper processes 69,065 daily rows, partitions by `(seller_id, year)`, and the reducers aggregate them into 4,254 annual merchant summaries stored in HDFS.

---

### Step 5: Theme 3 — Apache Pig Data Cleaning & Apache Hive Benchmark

#### Part A: Pig Latin Cleansing Pipeline
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -rm -r -f /user/root/ecommerce/pig_eval_out"
docker exec ecommerce-sales-analytics-master-1 bash -c "pig -x mapreduce -param INPUT=/user/root/ecommerce/live_eval_run/prepared/daily.tsv -param OUTPUT=/user/root/ecommerce/pig_eval_out /project/pig/clean_daily.pig"
```

> **Explanation to Faculty:** Pig validates date formats via regex `\d{4}-\d{2}-\d{2}`, removes empty merchant IDs, and filters out negative financial records, producing clean input for Hive.

#### Part B: Hive Table Creation & Comparative Benchmark Query
```powershell
# 1. Create TextFile and Columnar RCFile tables
docker exec ecommerce-sales-analytics-master-1 bash -c "beeline -u jdbc:hive2://localhost:10000 -n root --hivevar DATABASE=ecommerce_analytics --hivevar INPUT=/user/root/ecommerce/pig_eval_out --hivevar RC_OUTPUT=/user/root/ecommerce/rcfile -f /project/hive/tables.hql"

# 2. Run identical analytical queries on Text vs RCFile
docker exec ecommerce-sales-analytics-master-1 bash -c "beeline -u jdbc:hive2://localhost:10000/ecommerce_analytics -n root -e 'SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev FROM daily_text GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5; SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev FROM daily_rcfile GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5;'"
```

#### Part C: HDFS Storage Audit (Text vs RCFile)
```powershell
docker exec ecommerce-sales-analytics-master-1 bash -c "hdfs dfs -du -h /user/root/ecommerce/"
```

> **Explanation to Faculty:** RCFile achieves a **78.71% storage reduction** (915 KB vs 4.2 MB) and faster query execution because columnar storage only reads and decompresses columns required by the aggregation.

---

### Step 6: Track B Practical Extension — Interactive Flask Dashboard

```powershell
python -m ecommerce dashboard --results "results/ecommerce"
```

Open `http://localhost:5000` in browser:
- **Page 1 (Seller Deep-Dive)**: Search seller ID `4869f7a5dfa277a7dca6462dcf3b52b2`. Showcase annual revenue progression bars and the dynamic SVG pie chart illustrating 2016–2018 marketplace shares.
- **Page 2 (Annual Leaderboard)**: Select year `2018` and rank by `Total Revenue`. Demonstrate ranking of top merchants and comparisons against lowest volume sellers.

---

## Summary Table for Faculty & Viva Reference

| Component | Technology | Dataset Metrics | Benchmark / Key Result |
|---|---|---|---|
| **Theme 1** | MongoDB 7.0 | 69,065 daily sales / 99,441 orders | **229.73x scan reduction** (`IXSCAN` 100 vs `COLLSCAN` 22,973 docs; 5.67x speedup) |
| **Theme 2** | Hadoop 2.10.2 / YARN | 69,065 rows $\rightarrow$ 4,254 summaries | **2 distributed reducers** on YARN across 2 DataNodes |
| **Theme 3** | Apache Pig 0.17.0 | 69,065 records read & stored | Schema validation with regex date filtering in 21s |
| **Theme 3** | Apache Hive 2.3.9 | Text (4.2 MB) vs RCFile (915 KB) | **78.71% storage savings** & 1.11x query execution speedup |
| **Track B Extension** | Python Flask & Dynamic SVG | Multi-year seller analytics | Interactive web dashboard serving pre-aggregated outputs |

---

## Project Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Laptop Demo](docs/LAPTOP-DEMO.md)
- [Three-System Walkthrough](docs/THREE-SYSTEM-RUN.md)
- [MongoDB Analytics Guide](docs/MONGODB-ANALYTICS.md)
- [Report Outline](docs/report-outline.md)
- [Validation Record](docs/validation.md)
- [Technical Reference](docs/TECHNICAL-REFERENCE.md)
- [Possible Q&A](docs/possibleQA.md)
- [Presentation Q&A](docs/PRESENTATION-QA.md)
- [Live Demo Cheatsheet](DEMO_COMMANDS.md)
- [Complete Execution Guide HTML](docs/complete_execution_guide.html)
