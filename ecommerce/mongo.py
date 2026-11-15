"""MongoDB persistence and aggregation for prepared daily e-commerce sales."""

import csv
import math
import os
import re
from pathlib import Path

from pymongo import MongoClient


def build_faceted_pipeline(min_year=2016, max_year=2018):
    """Build an aggregation pipeline using $match, $facet, $group, $unwind, and $project."""
    return [
        {"$match": {"year": {"$gte": min_year, "$lte": max_year}}},
        {
            "$facet": {
                "annual_totals": [
                    {
                        "$group": {
                            "_id": "$year",
                            "active_seller_days": {"$sum": 1},
                            "orders": {"$sum": "$orders"},
                            "revenue_brl": {"$sum": "$revenue_brl"},
                            "peak_order_brl": {"$max": "$peak_order_brl"},
                            "sellers": {"$addToSet": "$seller_id"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "year": "$_id",
                            "active_seller_days": 1,
                            "orders": 1,
                            "revenue_brl": 1,
                            "peak_order_brl": 1,
                            "unique_sellers": {"$size": "$sellers"},
                        }
                    },
                    {"$sort": {"year": 1}},
                ],
                "top_sellers": [
                    {
                        "$group": {
                            "_id": "$seller_id",
                            "total_revenue_brl": {"$sum": "$revenue_brl"},
                            "total_orders": {"$sum": "$orders"},
                            "active_days": {"$sum": 1},
                        }
                    },
                    {"$sort": {"total_revenue_brl": -1, "_id": 1}},
                    {"$limit": 10},
                    {
                        "$project": {
                            "_id": 0,
                            "seller_id": "$_id",
                            "total_revenue_brl": 1,
                            "total_orders": 1,
                            "active_days": 1,
                        }
                    },
                ],
                "revenue_tiers": [
                    {
                        "$group": {
                            "_id": "$seller_id",
                            "total_revenue_brl": {"$sum": "$revenue_brl"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "seller_id": "$_id",
                            "total_revenue_brl": 1,
                            "tier": {
                                "$cond": [
                                    {"$gte": ["$total_revenue_brl", 10000]},
                                    "high",
                                    {
                                        "$cond": [
                                            {"$gte": ["$total_revenue_brl", 1000]},
                                            "medium",
                                            "low",
                                        ]
                                    },
                                ]
                            },
                        }
                    },
                    {
                        "$group": {
                            "_id": "$tier",
                            "seller_count": {"$sum": 1},
                            "tier_revenue_brl": {"$sum": "$total_revenue_brl"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "tier": "$_id",
                            "seller_count": 1,
                            "tier_revenue_brl": 1,
                        }
                    },
                    {"$sort": {"tier_revenue_brl": -1}},
                ],
            }
        },
        {"$unwind": "$annual_totals"},
        {
            "$project": {
                "year": "$annual_totals.year",
                "active_seller_days": "$annual_totals.active_seller_days",
                "unique_sellers": "$annual_totals.unique_sellers",
                "orders": "$annual_totals.orders",
                "revenue_brl": "$annual_totals.revenue_brl",
                "peak_order_brl": "$annual_totals.peak_order_brl",
                "top_sellers": 1,
                "revenue_tiers": 1,
            }
        },
    ]


def build_order_items_pipeline():
    """Build an aggregation pipeline over embedded order items and unstructured reviews."""
    return [
        {"$match": {"order_status": {"$nin": ["canceled", "unavailable"]}}},
        {"$unwind": "$items"},
        {
            "$facet": {
                "seller_item_totals": [
                    {
                        "$group": {
                            "_id": "$items.seller_id",
                            "items_sold": {"$sum": 1},
                            "total_price_brl": {"$sum": "$items.price"},
                            "total_freight_brl": {"$sum": "$items.freight_value"},
                        }
                    },
                    {"$sort": {"total_price_brl": -1, "_id": 1}},
                    {"$limit": 10},
                    {
                        "$project": {
                            "_id": 0,
                            "seller_id": "$_id",
                            "items_sold": 1,
                            "total_price_brl": 1,
                            "total_freight_brl": 1,
                        }
                    },
                ],
                "review_score_summary": [
                    {"$match": {"review.score": {"$ne": None}}},
                    {
                        "$group": {
                            "_id": "$review.score",
                            "item_count": {"$sum": 1},
                            "avg_item_price_brl": {"$avg": "$items.price"},
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "review_score": "$_id",
                            "item_count": 1,
                            "avg_item_price_brl": 1,
                        }
                    },
                    {"$sort": {"review_score": -1}},
                ],
            }
        },
    ]


def _ingest_orders_enriched(db, raw_dir, batch_size):
    """Ingest structured orders/items and unstructured reviews into orders_enriched."""
    raw_path = Path(raw_dir)
    orders_file = raw_path / "olist_orders_dataset.csv"
    items_file = raw_path / "olist_order_items_dataset.csv"
    reviews_file = raw_path / "olist_order_reviews_dataset.csv"
    if not orders_file.is_file() or not items_file.is_file():
        raise FileNotFoundError(f"Expected Olist CSV files under {raw_path}")

    items_by_order = {}
    with items_file.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            oid = row["order_id"].strip()
            items_by_order.setdefault(oid, []).append({
                "order_item_id": int(row["order_item_id"]),
                "product_id": row["product_id"].strip(),
                "seller_id": row["seller_id"].strip(),
                "price": float(row["price"]),
                "freight_value": float(row["freight_value"]),
            })

    reviews_by_order = {}
    if reviews_file.is_file():
        with reviews_file.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                oid = row["order_id"].strip()
                score_raw = row.get("review_score", "").strip()
                reviews_by_order[oid] = {
                    "score": int(score_raw) if score_raw.isdigit() else None,
                    "comment_title": row.get("review_comment_title", "").strip(),
                    "comment_message": row.get("review_comment_message", "").strip(),
                }

    orders_col = db.orders_enriched
    batch = []
    count = 0
    with orders_file.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            oid = row["order_id"].strip()
            doc = {
                "order_id": oid,
                "customer_id": row.get("customer_id", "").strip(),
                "order_status": row.get("order_status", "").strip().lower(),
                "order_purchase_timestamp": row.get("order_purchase_timestamp", "").strip(),
                "items": items_by_order.get(oid, []),
            }
            if oid in reviews_by_order:
                doc["review"] = reviews_by_order[oid]
            batch.append(doc)
            if len(batch) >= batch_size:
                orders_col.insert_many(batch, ordered=True)
                count += len(batch)
                batch.clear()
        if batch:
            orders_col.insert_many(batch, ordered=True)
            count += len(batch)

    orders_col.create_index([("order_id", 1)], unique=True, name="order_id")
    orders_col.create_index([("items.seller_id", 1), ("order_status", 1)], name="item_seller_status")
    orders_col.create_index([("review.score", 1)], name="review_score")
    return count


def import_and_analyze(daily_path, database="ecommerce_olist", batch_size=2000, raw_dir=None):
    if not re.fullmatch(r"ecommerce_[A-Za-z0-9_]+", database):
        raise ValueError("Use a dedicated database named ecommerce_<name>")
    if not 1 <= batch_size <= 10000:
        raise ValueError("batch-size must be between 1 and 10000")
    client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017"),
                         serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
        db = client[database]
        if db.list_collection_names():
            raise ValueError("Destination database is not empty; choose a new database")
        daily_col = db.daily_sales
        batch = []
        count = 0
        with Path(daily_path).open(encoding="utf-8", newline="") as stream:
            for fields in csv.reader(stream, delimiter="\t"):
                if len(fields) != 6:
                    raise ValueError(f"Malformed daily row {count + 1}")
                day, seller_id, orders_str, revenue_str, mean_str, peak_str = fields
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
                    raise ValueError(f"Invalid date in daily row {count + len(batch) + 1}: {day}")
                try:
                    orders = int(orders_str)
                    revenue = float(revenue_str)
                    mean_val = float(mean_str)
                    peak = float(peak_str)
                except ValueError as error:
                    raise ValueError(f"Invalid numeric value in daily row {count + len(batch) + 1}") from error
                if orders < 1 or any(not math.isfinite(val) or val < 0 for val in (revenue, mean_val, peak)):
                    raise ValueError(f"Invalid numeric values in row {count + len(batch) + 1}")

                batch.append({
                    "date": day,
                    "seller_id": seller_id,
                    "year": int(day[:4]),
                    "orders": orders,
                    "revenue_brl": revenue,
                    "mean_order_brl": mean_val,
                    "peak_order_brl": peak,
                })
                if len(batch) >= batch_size:
                    daily_col.insert_many(batch, ordered=True)
                    count += len(batch)
                    batch.clear()
            if batch:
                daily_col.insert_many(batch, ordered=True)
                count += len(batch)

        daily_col.create_index([("seller_id", 1), ("year", 1)], name="seller_year")
        daily_col.create_index([("date", 1)], name="date")

        pipeline = [
            {
                "$group": {
                    "_id": {"seller_id": "$seller_id", "year": "$year"},
                    "days": {"$sum": 1},
                    "orders": {"$sum": "$orders"},
                    "revenue_brl": {"$sum": "$revenue_brl"},
                    "max_daily_revenue": {"$max": "$revenue_brl"},
                    "peak_order_brl": {"$max": "$peak_order_brl"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "seller_id": "$_id.seller_id",
                    "year": "$_id.year",
                    "days": 1,
                    "orders": 1,
                    "revenue_brl": 1,
                    "max_daily_revenue": 1,
                    "peak_order_brl": 1,
                    "mean_daily_revenue": {"$divide": ["$revenue_brl", "$days"]},
                }
            },
            {"$sort": {"seller_id": 1, "year": 1}},
        ]
        summaries = list(daily_col.aggregate(pipeline, allowDiskUse=True))
        faceted = list(daily_col.aggregate(build_faceted_pipeline(), allowDiskUse=True))

        result = {
            "database": database,
            "daily_rows": count,
            "summaries": summaries,
            "faceted_analytics": faceted,
        }
        if raw_dir:
            result["orders_enriched_docs"] = _ingest_orders_enriched(db, raw_dir, batch_size)
            result["order_items_analytics"] = list(
                db.orders_enriched.aggregate(build_order_items_pipeline(), allowDiskUse=True)
            )
        return result
    finally:
        client.close()
