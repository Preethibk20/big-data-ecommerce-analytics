"""Profile MongoDB queries against an imported e-commerce dataset."""

import argparse
import json
import os
import re
from pathlib import Path

from pymongo import MongoClient

from .mongo import build_faceted_pipeline, build_order_items_pipeline


def _execution_summaries(explain):
    summaries = []

    def visit(value):
        if isinstance(value, dict):
            stats = value.get("executionStats")
            if isinstance(stats, dict):
                summaries.append({
                    key: stats[key]
                    for key in (
                        "executionSuccess",
                        "nReturned",
                        "executionTimeMillis",
                        "totalKeysExamined",
                        "totalDocsExamined",
                    )
                    if key in stats
                })
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(explain)
    return summaries


def _winning_stages(explain):
    """Extract query plan stage names (e.g., IXSCAN, COLLSCAN) from an explain document."""
    stages = []

    def visit(node):
        if isinstance(node, dict):
            if "stage" in node and isinstance(node["stage"], str):
                stages.append(node["stage"])
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    planner = explain.get("queryPlanner", {}).get("winningPlan")
    if planner:
        visit(planner)
    else:
        for stage in explain.get("stages", []):
            cursor_plan = stage.get("$cursor", {}).get("queryPlanner", {}).get("winningPlan")
            if cursor_plan:
                visit(cursor_plan)
    return stages


def _compare_index_performance(unindexed_stats, indexed_stats):
    """Compare COLLSCAN vs IXSCAN executionStats."""
    if not unindexed_stats or not indexed_stats:
        return {}
    unindexed = unindexed_stats[0]
    indexed = indexed_stats[0]
    unindexed_docs = unindexed.get("totalDocsExamined", 0)
    indexed_docs = indexed.get("totalDocsExamined", 0)
    unindexed_ms = unindexed.get("executionTimeMillis", 0)
    indexed_ms = indexed.get("executionTimeMillis", 0)
    return {
        "unindexed_docs_examined": unindexed_docs,
        "indexed_docs_examined": indexed_docs,
        "docs_examined_reduction_ratio": (
            round(unindexed_docs / indexed_docs, 2) if indexed_docs else None
        ),
        "unindexed_time_ms": unindexed_ms,
        "indexed_time_ms": indexed_ms,
        "speedup_ratio": (
            round(unindexed_ms / indexed_ms, 2) if indexed_ms else None
        ),
    }


def profile_database(database, seller_id, output_path):
    if not re.fullmatch(r"ecommerce_[A-Za-z0-9_]+", database):
        raise ValueError("Use the imported database named ecommerce_<name>")
    if not seller_id or len(seller_id.strip()) < 3:
        raise ValueError("seller-id must be at least 3 characters")

    client = MongoClient(
        os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017"),
        serverSelectionTimeoutMS=10000,
    )
    try:
        client.admin.command("ping")
        db = client[database]
        daily = db.daily_sales
        document_count = daily.estimated_document_count()
        if document_count == 0:
            raise ValueError(
                f"No imported daily_sales documents found in database {database}"
            )

        query = {"seller_id": seller_id, "year": {"$gte": 2016, "$lte": 2018}}
        find_cmd = {
            "find": "daily_sales",
            "filter": query,
            "projection": {"_id": 0, "date": 1, "revenue_brl": 1, "orders": 1},
            "limit": 100,
        }
        find_explain = db.command("explain", find_cmd, verbosity="executionStats")
        find_unindexed_explain = db.command(
            "explain",
            {**find_cmd, "hint": {"$natural": 1}},
            verbosity="executionStats",
        )

        aggregation = [
            {"$match": {"seller_id": seller_id}},
            {
                "$group": {
                    "_id": "$year",
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
                    "year": "$_id",
                    "days": 1,
                    "orders": 1,
                    "revenue_brl": 1,
                    "mean_daily_revenue": {"$divide": ["$revenue_brl", "$days"]},
                    "max_daily_revenue": 1,
                    "peak_order_brl": 1,
                }
            },
            {"$sort": {"year": 1}},
        ]
        aggregate_explain = db.command(
            "explain",
            {
                "aggregate": "daily_sales",
                "pipeline": aggregation,
                "cursor": {},
            },
            verbosity="executionStats",
        )
        faceted_pipeline = build_faceted_pipeline()
        faceted_explain = db.command(
            "explain",
            {
                "aggregate": "daily_sales",
                "pipeline": faceted_pipeline,
                "cursor": {},
            },
            verbosity="executionStats",
        )

        indexes = daily.index_information()
        annual_results = list(daily.aggregate(aggregation, allowDiskUse=True))
        faceted_results = list(daily.aggregate(faceted_pipeline, allowDiskUse=True))

        indexed_stats = _execution_summaries(find_explain)
        unindexed_stats = _execution_summaries(find_unindexed_explain)

        report = {
            "database": database,
            "collection": "daily_sales",
            "seller_id": seller_id,
            "document_count": document_count,
            "indexes": {
                name: {"keys": details["key"], "unique": details.get("unique", False)}
                for name, details in indexes.items()
            },
            "query_profile": {
                "description": "Find daily records for one seller across 2016-2018 (IXSCAN vs COLLSCAN)",
                "indexed_stages": _winning_stages(find_explain),
                "explain_execution_stats": indexed_stats,
                "unindexed_stages": _winning_stages(find_unindexed_explain),
                "unindexed_execution_stats": unindexed_stats,
                "index_comparison": _compare_index_performance(unindexed_stats, indexed_stats),
            },
            "aggregation_profile": {
                "description": "Group the selected seller's daily records by year",
                "stages": _winning_stages(aggregate_explain),
                "explain_execution_stats": _execution_summaries(aggregate_explain),
                "annual_results": annual_results,
            },
            "faceted_pipeline_profile": {
                "description": "Multi-stage $match, $facet ($group, $project), $unwind analytics",
                "explain_execution_stats": _execution_summaries(faceted_explain),
                "results": faceted_results,
            },
        }

        if "orders_enriched" in db.list_collection_names() and db.orders_enriched.estimated_document_count() > 0:
            order_pipeline = build_order_items_pipeline()
            order_explain = db.command(
                "explain",
                {"aggregate": "orders_enriched", "pipeline": order_pipeline, "cursor": {}},
                verbosity="executionStats",
            )
            report["orders_enriched_profile"] = {
                "document_count": db.orders_enriched.estimated_document_count(),
                "explain_execution_stats": _execution_summaries(order_explain),
                "results": list(db.orders_enriched.aggregate(order_pipeline, allowDiskUse=True)),
            }

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
        return report
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="ecommerce_olist")
    parser.add_argument("--seller-id", required=True)
    parser.add_argument("--output", default="results/mongodb-analytics.json")
    args = parser.parse_args()
    report = profile_database(args.database, args.seller_id, args.output)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
