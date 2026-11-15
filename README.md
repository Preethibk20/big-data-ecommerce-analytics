# Brazilian E-Commerce (Olist) Sales & Merchant Analytics

Big Data Analytics project using the [Kaggle Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
The dataset covers over 100,000 orders made at Olist Store from 2016 through 2018 across Brazilian marketplaces.

The project validates raw relational order and item records, converts them into normalized daily seller transaction summaries, and performs distributed annual aggregations across Python, MongoDB, Hadoop MapReduce, Apache Pig, and Apache Hive. A two-page interactive Flask dashboard enables users to inspect multi-year merchant trajectories and rank sellers across core business metrics.

## E-Commerce Data Interpretation

- **Orders & Items**: Orders represent purchases placed on the marketplace. Canceled and unavailable orders are filtered out; delivered, shipped, and invoiced orders are matched with order items.
- **Granular Daily Aggregations**: Individual order item transactions are streamed and aggregated at the daily grain per seller: total items sold, total revenue in Brazilian Reais (R$), mean order item price, and peak single item value.
- **Multi-Year Coverage**: Covers transactional history spanning 2016 through 2018 across 3,000+ active sellers.
- **Revenue Metric**: Prices are in Brazilian Reais (BRL / R$). Non-finite or negative values are rejected during validation.

## Quick Start (Python, Windows or Linux)

Requires Python 3.11 or newer. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Download the dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) or place the extracted CSV files under `brazilian-ecommerce/`. Then produce annual summaries:

```powershell
# 1. Prepare and normalize daily seller records
python -m ecommerce prepare --input "brazilian-ecommerce" --output "data/prepared/ecommerce"

# 2. Run MapReduce and cross-check against reference analytics locally
python -m ecommerce analyze --daily "data/prepared/ecommerce/daily.tsv" --output "results/ecommerce"

# 3. Launch the interactive analytics dashboard
python -m ecommerce dashboard --results "results/ecommerce"
```

Open `http://127.0.0.1:5000` in your browser:
- **Page 1 · Seller Multi-Year Performance**: Search any seller ID (full 32-character hex or initial prefix) or pick from top sellers. View cumulative metrics, annual progression, an interactive SVG pie chart comparing yearly shares for any selected metric (Revenue, Orders, Mean Daily Revenue, Max Daily Revenue, Peak Order Value), and a bar chart comparing annual totals.
- **Page 2 · Annual Seller Leaderboard**: Select a calendar year (2016, 2017, or 2018), ranking metric, and Top K (1 to total sellers). Highlights highest and lowest performing merchants and displays a clean, responsive leaderboard.

## Optional MongoDB Aggregation & Profiling

Start a local MongoDB service (e.g., `.\scripts\start_mongo.ps1` on Windows or `scripts/start_mongo.sh` on Linux/macOS), then import and aggregate:

```powershell
python -m ecommerce mongo --daily "data/prepared/ecommerce/daily.tsv" --database ecommerce_olist --raw "brazilian-ecommerce"
```

To profile `IXSCAN` vs `COLLSCAN` execution plans, query indexes, and `$facet`/`$unwind` pipelines:

```powershell
python -m ecommerce.mongo_profile --database ecommerce_olist --seller-id "4869f7a5dfa277a7dca6462dcf3b52b2" --output "results/mongodb-analytics.json"
```

The MongoDB pipelines aggregate annual revenue, order volumes, daily averages, and peak transaction values using `$match`, `$group`, `$project`, `$unwind`, `$facet`, and indexed lookups.

## Distributed Hadoop, Pig, and Hive

The distributed toolchain is set up in Docker or a cluster; see [docs/THREE-SYSTEM-RUN.md](docs/THREE-SYSTEM-RUN.md).
- **Hadoop Streaming**: `mapreduce/mapper.py` and `mapreduce/reducer.py` compute annual seller metrics on HDFS clusters.
- **Apache Pig**: `pig/clean_daily.pig` performs schema validation and data filtering.
- **Apache Hive**: `hive/tables.hql` and `hive/annual_seller_summary.hql` create Text and compressed RCFile tables and execute SQL analytical aggregations.

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

Generated `data/` and `results/` are local and excluded from version control. Output directories must be unique per run to ensure clean separation of artifacts.
