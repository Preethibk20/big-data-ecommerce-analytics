# Distributed Hadoop, Pig, and Hive Run

This guide describes the distributed big data workflow for the Brazilian E-Commerce dataset across an HDFS cluster.

## 1. Prepare Tools and Data

Ensure the Olist CSV files are placed in `brazilian-ecommerce/`. Prepare the daily normalized TSV:

```bash
python3 -m ecommerce prepare \
  --input brazilian-ecommerce \
  --output data/prepared/ecommerce
```

## 2. Upload Daily Rows and Run Hadoop Streaming

Upload the prepared daily records to HDFS:

```bash
RUN=ecommerce_demo_001
ROOT=/user/$USER/ecommerce/$RUN
hdfs dfs -mkdir -p "$ROOT/input"
hdfs dfs -put data/prepared/ecommerce/daily.tsv "$ROOT/input/"
```

Execute Hadoop Streaming MapReduce with 2 reducers:

```bash
scripts/run_mapreduce.sh "$ROOT/input" "$ROOT/mapreduce" 2
hdfs dfs -get "$ROOT/mapreduce" "results/$RUN-mapreduce"
```

The mapper emits `seller_id|year \t daily_revenue \t daily_orders \t daily_peak`. The reducer aggregates grouped keys and emits:
`seller_id \t year \t days \t total_revenue \t mean_daily_revenue \t max_daily_revenue \t total_orders \t peak_order_brl`.

The local `python -m ecommerce analyze` command performs this exact MapReduce job and asserts equivalence against pure Python reference summaries.

## 3. Apache Pig Data Cleaning

Run the Pig cleaning script in MapReduce mode to validate types and schemas:

```bash
pig -x mapreduce -param INPUT="$ROOT/input" -param OUTPUT="$ROOT/clean" \
  -f pig/clean_daily.pig
```

## 4. Apache Hive Text and RCFile Analytics

Create external Text and compressed RCFile tables (via Beeline against HiveServer2):

```bash
beeline -u jdbc:hive2://localhost:10000 -n root \
     --hivevar DATABASE=ecommerce_analytics \
     --hivevar INPUT="$ROOT/clean" \
     --hivevar RC_OUTPUT="$ROOT/rcfile" \
     -f hive/tables.hql
```

Execute the annual seller summary query on both tables, verify identical outputs, and report execution-time and HDFS storage-compression metrics:

```bash
scripts/benchmark_hive_rcfile.sh ecommerce_analytics "$ROOT/clean" "$ROOT/rcfile" results
```

Or run the individual queries manually:

```bash
beeline -u jdbc:hive2://localhost:10000 -n root --silent=true --showHeader=false --outputformat=tsv2 \
  --hivevar DATABASE=ecommerce_analytics --hivevar TABLE=daily_text -f hive/annual_seller_summary.hql > results/hive_text_summary.tsv
beeline -u jdbc:hive2://localhost:10000 -n root --silent=true --showHeader=false --outputformat=tsv2 \
  --hivevar DATABASE=ecommerce_analytics --hivevar TABLE=daily_rcfile -f hive/annual_seller_summary.hql > results/hive_rcfile_summary.tsv
diff results/hive_text_summary.tsv results/hive_rcfile_summary.tsv
```
