# Distributed Multi-Node Hadoop Cluster Setup & Presentation Guide
**Course:** BCS714D — Big Data Analytics  
**Academic Year:** 2026–2027 | **Faculty:** Sandhiya B  
**Dataset:** Brazilian E-Commerce Public Dataset by Olist  

---

## Part 1: Multi-Node Hadoop Cluster Setup (Lab Systems)

The assignment requires running across **at least 3 separate physical systems** connected via LAN/Wi-Fi:
* **System 1 (Master):** NameNode, ResourceManager, JobHistoryServer (+ Mongo/HiveServer2)
* **System 2 (Worker 1):** DataNode, NodeManager
* **System 3 (Worker 2):** DataNode, NodeManager

### 1. Network & Hosts Configuration (On ALL 3 Systems)

1. Find the static/assigned IP address of each system (`ipconfig` on Windows or `ip a` on Linux):
   * Example:
     * Master IP: `192.168.1.10`
     * Worker1 IP: `192.168.1.11`
     * Worker2 IP: `192.168.1.12`

2. Edit the hosts file:
   * **Windows:** `C:\Windows\System32\drivers\etc\hosts` (run Notepad as Administrator)
   * **Linux:** `/etc/hosts`
   Add the following lines to all 3 machines:
   ```text
   192.168.1.10   master
   192.168.1.11   worker1
   192.168.1.12   worker2
   ```

3. Ensure passwordless SSH from Master to all nodes:
   ```bash
   ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
   ssh-copy-id -i ~/.ssh/id_rsa.pub master
   ssh-copy-id -i ~/.ssh/id_rsa.pub worker1
   ssh-copy-id -i ~/.ssh/id_rsa.pub worker2
   ```

---

### 2. Hadoop Core Configuration Files (under `$HADOOP_HOME/etc/hadoop/`)

These match the configuration already prepared in your repository under `infra/hadoop/`:

#### `core-site.xml` (All Nodes)
```xml
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://master:9000</value>
  </property>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>/home/hadoop/hdata/tmp</value>
  </property>
</configuration>
```

#### `hdfs-site.xml` (All Nodes)
```xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>2</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/hadoop/hdata/dfs/name</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/hadoop/hdata/dfs/data</value>
  </property>
</configuration>
```

#### `yarn-site.xml` (All Nodes)
```xml
<configuration>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>master</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
</configuration>
```

#### `mapred-site.xml` (All Nodes)
```xml
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
```

#### `workers` (or `slaves` depending on Hadoop version) — on Master Node:
```text
worker1
worker2
```

---

### 3. Initialize & Start the Cluster (From Master Node)

1. Format the NameNode (only once on first setup):
   ```bash
   hdfs namenode -format
   ```
2. Start HDFS daemons:
   ```bash
   start-dfs.sh
   ```
3. Start YARN daemons:
   ```bash
   start-yarn.sh
   ```
4. Verify cluster health:
   ```bash
   hdfs dfsadmin -report
   yarn node -list
   ```
   *Expected: `Live datanodes (2): worker1, worker2` and `Total Nodes: 2` in RUNNING state.*

---

## Part 2: Executing the 3 Themes on the Multi-Node Cluster

### Theme 1: MongoDB Processing & Query Profiling
* Run on Master (or designated database host):
  ```bash
  # Ingestion
  python3 -m ecommerce mongo --daily data/prepared/ecommerce/daily.tsv --database ecommerce_olist --raw brazilian-ecommerce
  # Profiling (COLLSCAN vs IXSCAN)
  python3 -m ecommerce.mongo_profile --database ecommerce_olist --seller-id "4869f7a5dfa277a7dca6462dcf3b52b2" --output results/mongodb-analytics.json
  ```

### Theme 2: Distributed MapReduce on YARN
* Submit the MapReduce streaming job across Worker 1 and Worker 2:
  ```bash
  hdfs dfs -mkdir -p /user/root/ecommerce/live_eval_run/prepared
  hdfs dfs -put -f data/prepared/ecommerce/daily.tsv /user/root/ecommerce/live_eval_run/prepared/
  scripts/run_mapreduce.sh /user/root/ecommerce/live_eval_run/prepared/daily.tsv /user/root/ecommerce/mr_eval_out 2
  ```

### Theme 3: Pig Cleaning & Hive RCFile Benchmark
* Execute Pig validation on YARN:
  ```bash
  pig -x mapreduce -param INPUT=/user/root/ecommerce/live_eval_run/prepared/daily.tsv -param OUTPUT=/user/root/ecommerce/pig_eval_out pig/clean_daily.pig
  ```
* Execute Hive Text vs RCFile query comparison:
  ```bash
  beeline -u jdbc:hive2://master:10000 -n root --hivevar DATABASE=ecommerce_analytics --hivevar INPUT=/user/root/ecommerce/pig_eval_out --hivevar RC_OUTPUT=/user/root/ecommerce/rcfile -f hive/tables.hql
  
  beeline -u jdbc:hive2://master:10000/ecommerce_analytics -n root -e "SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev FROM daily_text GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5; SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev FROM daily_rcfile GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5;"
  ```

---

## Part 3: Presentation Structure (Slide-by-Slide)

Here is the exact slide deck structure addressing all required points for your evaluation presentation:

### Slide 1: Title & Group Details
- **Title:** Distributed Big Data Analytics on Brazilian E-Commerce (Olist)
- **Subtitle:** Multi-Node Hadoop, YARN MapReduce, Pig, Hive RCFile Benchmarking & MongoDB Profiling
- **Details:** Course Code (BCS714D), Section (7A/7B), Student Names & USNs, Faculty: Sandhiya B

### Slide 2: Dataset Overview
- **Name:** Brazilian E-Commerce Public Dataset by Olist (Kaggle).
- **Scale:** 98,207 valid orders, 112,101 line items, 3,053 active merchants, 69,065 daily seller summaries.
- **Timespan:** Sept 2016 to Sept 2018; Total sales: R$ 13,494,400.74.
- **Key Tables:** Orders, Order Items, Customer Reviews, Products, Sellers.

### Slide 3: Architecture & Multi-Node Cluster Setup
- **Master Node:** NameNode + YARN ResourceManager + HiveServer2 + MongoDB.
- **Worker Nodes (Worker 1 & Worker 2):** DataNodes + NodeManagers.
- **Network Configuration:** Hostname mapping, SSH keys, replication factor = 2, HDFS block distribution.

### Slide 4: 5 Distinct Business Analytics Questions
1. **Q1 (Marketplace Growth):** How did total transaction volume and GMV (Gross Merchandise Value) scale across 2016, 2017, and 2018?
2. **Q2 (Merchant Pareto Distribution):** Who are the top 5 revenue-generating sellers, and what fraction of total sales do they command?
3. **Q3 (Customer Satisfaction vs Revenue):** Does higher seller GMV correlate with positive review scores (1 to 5 stars)?
4. **Q4 (Merchant Volatility & Peak Days):** What are the peak daily transaction spikes per seller vs their mean daily revenue?
5. **Q5 (Storage & Query Speedup):** How does columnar compression (RCFile + Gzip) compare against standard row-based Text for multi-year analytical scans?

### Slide 5: Theme 1 Implementation — MongoDB Aggregation & Profiling
- **Ingestion:** `daily_sales` (69,065 docs) and `orders_enriched` (99,441 docs with nested review text and items array).
- **Pipelines:** `$match`, `$unwind` (flattening order items), `$facet` (concurrent revenue and review score aggregation).
- **Profiling (`.explain('executionStats')`):**
  - Unindexed (`COLLSCAN`): 22,973 docs examined, 17 ms.
  - Indexed (`IXSCAN` on `(seller_id, year)`): 100 docs examined, 3 ms.
  - **Result:** 229.7x document scan reduction, 5.67x speedup.

### Slide 6: Theme 2 Implementation — HDFS Operations & YARN MapReduce
- **HDFS Lifecycle:** `-mkdir`, `-put`, `-cat`, `-get`, `-rm -r`.
- **Hadoop Streaming MapReduce on YARN:**
  - `mapper.py`: Emits `(seller_id|year) -> (revenue, orders, peak)`.
  - `reducer.py`: Aggregates grouped keys into annual summaries across 2 reducers.
  - Processed 69,065 input records into 4,254 aggregated merchant records.

### Slide 7: Theme 3 Implementation — Pig Transformation & Hive RCFile Benchmark
- **Pig Latin Cleaning:** Regex date validation (`\d{4}-\d{2}-\d{2}`), non-empty seller IDs, non-negative checks (`69,065` valid rows output).
- **Hive Table Benchmark:**
  - Standard Text (`TEXTFILE`): 4.40 MB, Query time: 56.78 s.
  - Columnar Compressed (`RCFILE + GzipCodec`): 937 KB, Query time: 50.89 s.
  - **Result:** **78.71% disk space savings** and **1.11x–1.45x query speedup**.

### Slide 8: Track B Practical Extension — Interactive Flask Dashboard
- **Page 1 (Seller Deep-Dive):** Merchant ID search, multi-year trend analysis, dynamic SVG revenue share.
- **Page 2 (Annual Leaderboard):** Filter by year (2016/2017/2018), rank by revenue/orders/peak, top vs bottom merchant comparisons.

### Slide 9: Conclusion & Key Learnings
- Distributed processing advantages over single-node bottlenecks.
- Trade-offs between document databases (MongoDB) for real-time querying vs data lakes (HDFS + Hive RCFile) for batch reporting.
- Q&A session.
