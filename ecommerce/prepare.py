"""Convert the Kaggle Olist Brazilian E-Commerce dataset to daily seller summaries."""

import csv
import hashlib
import json
import math
import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


SELLER_HEX_PATTERN = re.compile(r"[0-9a-fA-F]{32}\Z")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _parse_price(raw, row_number, order_id):
    if not raw:
        raise ValueError(f"Missing price for order {order_id} at item row {row_number}")
    try:
        value = float(raw)
    except ValueError as error:
        raise ValueError(f"Invalid price for order {order_id} at item row {row_number}: {raw!r}") from error
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"Invalid non-finite or negative price at item row {row_number}: {value}")
    return value


def prepare(source, destination, min_status=None):
    """Stream and aggregate Olist orders & items into daily seller revenue summaries."""
    source_path = Path(source).resolve(strict=True)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    if source_path.is_dir():
        orders_file = source_path / "olist_orders_dataset.csv"
        items_file = source_path / "olist_order_items_dataset.csv"
        sellers_file = source_path / "olist_sellers_dataset.csv"
    else:
        orders_file = source_path
        items_file = source_path.parent / "olist_order_items_dataset.csv"
        sellers_file = source_path.parent / "olist_sellers_dataset.csv"

    if not orders_file.is_file():
        raise FileNotFoundError(f"Orders dataset not found at {orders_file}")
    if not items_file.is_file():
        raise FileNotFoundError(f"Order items dataset not found at {items_file}")

    excluded_statuses = {"canceled", "unavailable"}

    # 1. Map order_id -> purchase_date
    orders_date = {}
    valid_orders = 0
    with orders_file.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        for row_num, row in enumerate(reader, start=2):
            oid = row.get("order_id", "").strip()
            status = row.get("order_status", "").strip().lower()
            timestamp = row.get("order_purchase_timestamp", "").strip()
            if not oid:
                raise ValueError(f"Missing order_id at orders row {row_num}")
            if status in excluded_statuses:
                continue
            if not timestamp:
                continue
            date_str = timestamp[:10]
            if not DATE_PATTERN.fullmatch(date_str):
                raise ValueError(f"Invalid date format in timestamp {timestamp!r} at orders row {row_num}")
            orders_date[oid] = date_str
            valid_orders += 1

    if not orders_date:
        raise ValueError("No valid orders found in the orders file")

    # 2. Stream items and aggregate by (date, seller_id)
    # daily_stats: (date, seller_id) -> [orders_count, total_revenue, peak_item_price]
    daily_stats = defaultdict(lambda: [0, 0.0, 0.0])
    total_items = 0
    sellers_seen = set()

    with items_file.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        for row_num, row in enumerate(reader, start=2):
            oid = row.get("order_id", "").strip()
            if oid not in orders_date:
                continue
            seller_id = row.get("seller_id", "").strip()
            if not seller_id:
                raise ValueError(f"Missing seller_id at items row {row_num}")
            price = _parse_price(row.get("price", ""), row_num, oid)

            date = orders_date[oid]
            stat = daily_stats[(date, seller_id)]
            stat[0] += 1
            stat[1] += price
            if price > stat[2]:
                stat[2] = price
            total_items += 1
            sellers_seen.add(seller_id)

    if not daily_stats:
        raise ValueError("No matching order items found for valid orders")

    # 3. Write sorted daily.tsv
    daily_tsv = destination / "daily.tsv"
    sorted_keys = sorted(daily_stats.keys())
    first_day = sorted_keys[0][0]
    last_day = sorted_keys[-1][0]

    with daily_tsv.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        for date, seller_id in sorted_keys:
            count, revenue, peak = daily_stats[(date, seller_id)]
            mean_order = revenue / count if count else 0.0
            writer.writerow((
                date,
                seller_id,
                count,
                format(revenue, ".15g"),
                format(mean_order, ".15g"),
                format(peak, ".15g")
            ))

    source_hashes = {
        "orders_sha256": sha256(orders_file),
        "items_sha256": sha256(items_file),
    }
    if sellers_file.is_file():
        source_hashes["sellers_sha256"] = sha256(sellers_file)

    manifest = {
        "dataset": "Kaggle Brazilian E-Commerce (Olist)",
        "source_directory": str(source_path),
        "source_files": source_hashes,
        "valid_orders": valid_orders,
        "matched_items": total_items,
        "daily_seller_rows": len(daily_stats),
        "unique_sellers": len(sellers_seen),
        "first_day": first_day,
        "last_day": last_day,
        "daily_columns": ["date", "seller_id", "orders", "revenue_brl", "mean_order_brl", "peak_order_brl"],
        "conversion": "revenue_brl is the sum of item prices sold by the seller on that day in BRL (R$)",
        "order_status_note": "Canceled and unavailable orders are excluded; delivered and approved orders are aggregated.",
        "aggregation_grain": "Daily per-seller normalized transactional records.",
    }

    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
