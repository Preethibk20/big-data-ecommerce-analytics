"""Reference annual seller summaries and local streaming MapReduce execution."""

import csv
import json
import math
import subprocess
import sys
from pathlib import Path


METRICS = {
    "revenue_brl": {"label": "Total Revenue", "unit": "R$"},
    "orders": {"label": "Total Orders", "unit": "orders"},
    "mean_daily_revenue": {"label": "Mean Revenue/Day", "unit": "R$/day"},
    "max_daily_revenue": {"label": "Max Daily Revenue", "unit": "R$"},
    "peak_order_brl": {"label": "Peak Order Value", "unit": "R$"},
}


def reference(daily_path):
    groups = {}
    with Path(daily_path).open(encoding="utf-8", newline="") as stream:
        for row_number, fields in enumerate(csv.reader(stream, delimiter="\t"), start=1):
            if len(fields) != 6:
                raise ValueError(f"Expected six fields in daily row {row_number}")
            day, seller_id, orders_str, revenue_str, mean_str, peak_str = fields
            try:
                orders = int(orders_str)
                revenue = float(revenue_str)
                peak = float(peak_str)
            except ValueError as error:
                raise ValueError(f"Invalid numeric value in daily row {row_number}") from error

            if orders < 1 or any(not math.isfinite(value) or value < 0 for value in (revenue, peak)):
                raise ValueError(f"Invalid numeric range in daily row {row_number}")

            year = int(day[:4])
            key = (seller_id, year)
            item = groups.setdefault(key, {
                "days": 0,
                "orders": 0,
                "revenue_brl": 0.0,
                "max_daily_revenue": 0.0,
                "peak_order_brl": 0.0,
            })
            item["days"] += 1
            item["orders"] += orders
            item["revenue_brl"] += revenue
            if revenue > item["max_daily_revenue"]:
                item["max_daily_revenue"] = revenue
            if peak > item["peak_order_brl"]:
                item["peak_order_brl"] = peak

    for item in groups.values():
        item["mean_daily_revenue"] = item["revenue_brl"] / item["days"] if item["days"] else 0.0

    return groups


def local_mapreduce(daily_path, output_path):
    """Run the same mapper and reducer entry points used by Hadoop Streaming."""
    root = Path(__file__).resolve().parent.parent
    with Path(daily_path).open("rb") as source:
        mapped = subprocess.run([sys.executable, str(root / "mapreduce/mapper.py")],
                                stdin=source, stdout=subprocess.PIPE, check=True)
    shuffled = b"".join(sorted(mapped.stdout.splitlines(keepends=True)))
    reduced = subprocess.run([sys.executable, str(root / "mapreduce/reducer.py")],
                             input=shuffled, stdout=subprocess.PIPE, check=True)
    Path(output_path).write_bytes(reduced.stdout)
    return reduced.stdout.decode("utf-8")


def read_mapreduce(text):
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != 8:
            raise ValueError(f"MapReduce output must contain eight tab-separated fields, got {len(fields)}")
        seller_id, year, days, total_rev, mean_rev, max_rev, orders, peak = fields
        key = (seller_id, int(year))
        if key in result:
            raise ValueError(f"Duplicate MapReduce summary for {key}")
        result[key] = {
            "days": int(days),
            "orders": int(orders),
            "revenue_brl": float(total_rev),
            "mean_daily_revenue": float(mean_rev),
            "max_daily_revenue": float(max_rev),
            "peak_order_brl": float(peak),
        }
    return result


def check(expected, actual):
    if expected.keys() != actual.keys():
        raise ValueError(f"MapReduce ({len(actual)}) and reference ({len(expected)}) summaries contain different seller/year groups")
    for key, left in expected.items():
        right = actual[key]
        for field in ("days", "orders"):
            if left[field] != right[field]:
                raise ValueError(f"Summary mismatch for {key}: {field} (expected {left[field]}, got {right[field]})")
        for field in ("revenue_brl", "mean_daily_revenue", "max_daily_revenue", "peak_order_brl"):
            if not math.isclose(left[field], right[field], rel_tol=1e-7, abs_tol=1e-7):
                raise ValueError(f"Summary mismatch for {key}: {field} (expected {left[field]}, got {right[field]})")


def analyze(daily_path, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    groups = reference(daily_path)
    mr_text = local_mapreduce(daily_path, output_dir / "mapreduce.tsv")
    check(groups, read_mapreduce(mr_text))

    records = [{"seller_id": seller, "year": year, **value}
               for (seller, year), value in sorted(groups.items())]

    unique_sellers = sorted({row["seller_id"] for row in records})
    # Pre-compute top sellers overall for quick navigation in dashboard
    totals_by_seller = {}
    for r in records:
        sid = r["seller_id"]
        totals_by_seller[sid] = totals_by_seller.get(sid, 0.0) + r["revenue_brl"]
    top_sellers = sorted(totals_by_seller.items(), key=lambda x: -x[1])[:20]

    result = {
        "dataset": "Kaggle Brazilian E-Commerce (Olist)",
        "summary": "Annual revenue, orders, and peak value summaries by seller",
        "groups": len(records),
        "total_revenue_brl": sum(row["revenue_brl"] for row in records),
        "total_orders": sum(row["orders"] for row in records),
        "sellers": len(unique_sellers),
        "years": sorted({row["year"] for row in records}),
        "mapreduce_crosscheck": "passed",
        "top_seller_ids": [sid for sid, _ in top_sellers],
        "records": records,
    }
    (output_dir / "analytics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def seller_year_view(data, query, pie_metric="revenue_brl"):
    """Return one seller's available yearly records in chronological order."""
    if pie_metric not in METRICS:
        raise ValueError("Unsupported seller pie-chart metric")
    query_clean = query.strip().lower()
    if not query_clean:
        return None

    # Exact match first, then prefix match
    matched_seller_id = None
    all_sellers = {row["seller_id"] for row in data["records"]}
    for sid in all_sellers:
        if sid.lower() == query_clean:
            matched_seller_id = sid
            break
    if not matched_seller_id:
        for sid in sorted(all_sellers):
            if sid.lower().startswith(query_clean):
                matched_seller_id = sid
                break

    if not matched_seller_id:
        return None

    existing_by_year = {
        row["year"]: row
        for row in data["records"]
        if row["seller_id"] == matched_seller_id
    }
    if not existing_by_year:
        return None

    dataset_years = sorted(data.get("years") or existing_by_year.keys())
    records = []
    for yr in dataset_years:
        if yr in existing_by_year:
            records.append(existing_by_year[yr])
        else:
            records.append({
                "seller_id": matched_seller_id,
                "year": yr,
                "days": 0,
                "orders": 0,
                "revenue_brl": 0.0,
                "mean_daily_revenue": 0.0,
                "max_daily_revenue": 0.0,
                "peak_order_brl": 0.0,
            })

    active = [r for r in records if r["orders"] > 0]
    eval_recs = active if active else records
    highest = max(eval_recs, key=lambda row: (row["revenue_brl"], -row["year"]))
    lowest = min(eval_recs, key=lambda row: (row["revenue_brl"], row["year"]))

    return {
        "seller_id": matched_seller_id,
        "records": records,
        "highest_year": highest["year"],
        "lowest_year": lowest["year"],
        "pie_metric": pie_metric,
        "pie_total": sum(row[pie_metric] for row in records),
    }


def year_seller_ranking(data, year, metric="revenue_brl", top_k=10):
    """Rank sellers by a selected annual metric and return the requested top K."""
    if metric not in METRICS:
        raise ValueError("Unsupported seller ranking metric")
    max_k = data["sellers"]
    if type(top_k) is not int or not 1 <= top_k <= max_k:
        raise ValueError(f"Top K must be between 1 and {max_k}")

    records = sorted(
        (row for row in data["records"] if row["year"] == year),
        key=lambda row: (-row[metric], row["seller_id"]),
    )
    return {
        "year": year,
        "metric": metric,
        "top_k": top_k,
        "sellers": records[:top_k],
        "seller_count": len(records),
        "most": records[0] if records else None,
        "least": records[-1] if records else None,
    }
