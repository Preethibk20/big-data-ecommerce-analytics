# Validation Record

The test suite validates data ingestion, schema filtering, MapReduce cross-checking, dashboard endpoints, error boundaries, and MongoDB aggregation logic.

## 1. Automated Unit Test Verification

Execute the test suite with:

```powershell
python -m unittest discover tests
```

Tests verify:
- Accurate filtering of canceled / unavailable orders.
- Correct streaming aggregation into daily per-seller records (`daily.tsv`).
- Equivalence between pure Python reference aggregation and MapReduce (`mapper.py` + `reducer.py`).
- Tie-breaking and sorting semantics in seller ranking (`-metric, seller_id`).
- Input validation: rejection of non-finite or negative prices.
- Dashboard HTTP responses: 200 OK for valid pages, 400 Bad Request for invalid years/metrics/top_k, 200 with notice for non-existent seller IDs.
- MongoDB explain execution statistics and index parsing.

## 2. Real Dataset Validation Record

For full-dataset verification, retain the generated `manifest.json` and `analytics.json`:
- Source: Kaggle Brazilian E-Commerce (Olist)
- Valid Orders Processed: 98,207
- Matched Items: 112,101
- Daily Seller Rows: 69,065
- Unique Sellers: 3,053
- Date Span: September 4, 2016 through September 3, 2018
- MapReduce Cross-Check: PASSED (Exact match on all (seller, year) groups)
