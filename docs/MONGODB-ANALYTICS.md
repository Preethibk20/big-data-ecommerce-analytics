# MongoDB Analytics & Query Profiling

The MongoDB workflow demonstrates document database ingestion, compound indexing, query planning, and aggregation pipelines on the prepared Brazilian E-Commerce dataset.

## 1. Data Ingestion & Pipeline Aggregation

The importer reads `daily.tsv`, validates types, and inserts records into the `daily_sales` collection in batches. It builds two indexes:
- `seller_year`: Compound index on `{"seller_id": 1, "year": 1}`
- `date`: Single index on `{"date": 1}`

When `--raw` is supplied, it also ingests structured orders/items and unstructured review comments into `orders_enriched` with indexes on `order_id`, `items.seller_id + order_status`, and `review.score`.

From the repository root:

```powershell
python -m ecommerce mongo --daily "data/prepared/ecommerce/daily.tsv" --database ecommerce_olist --raw "brazilian-ecommerce"
```

The aggregation pipelines cover `$match`, `$group`, `$project`, `$unwind`, and `$facet`:
- Per-seller annual summary (`$group` by `(seller_id, year)` -> `$project` `mean_daily_revenue` -> `$sort`)
- Multi-branch faceted analytics (`build_faceted_pipeline`): `$match` years -> `$facet` (`annual_totals`, `top_sellers`, `revenue_tiers` using `$group` and `$project`) -> `$unwind: "$annual_totals"` -> `$project`
- Order-item & review analytics (`build_order_items_pipeline` on `orders_enriched`): `$match` fulfilled orders -> `$unwind: "$items"` -> `$facet` (`seller_item_totals`, `review_score_summary`)

## 2. Query & Aggregation Profiling

The profiling command performs read-only explain calls with `executionStats` to compare unindexed (`COLLSCAN` via `$natural` hint) vs indexed (`IXSCAN` on `seller_year`) query performance:

```powershell
python -m ecommerce.mongo_profile --database ecommerce_olist --seller-id "53243585b1d7d780a402320474a15dac" --output "results/mongodb-analytics.json"
```

The generated `results/mongodb-analytics.json` records:
- Total collection document count (approx. 69,000+ daily documents)
- Active indexes on the collection
- Query Execution Stats (`IXSCAN` vs `COLLSCAN`):
  - `executionSuccess`, `nReturned`, `executionTimeMillis`, `totalKeysExamined`, `totalDocsExamined`
  - `docs_examined_reduction_ratio` and `speedup_ratio`
- Aggregation Pipeline Stats and `$facet`/`$unwind` results
