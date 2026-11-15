import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ecommerce.mongo import (
    build_faceted_pipeline,
    build_order_items_pipeline,
    import_and_analyze,
)
from ecommerce.mongo_profile import (
    _compare_index_performance,
    _execution_summaries,
    _winning_stages,
    profile_database,
)


class _FakeCollection:
    def __init__(self):
        self.docs = []
        self.indexes = {"_id_": {"key": [("_id", 1)], "unique": True}}

    def insert_many(self, batch, ordered=True):
        self.docs.extend(batch)

    def create_index(self, keys, name=None, unique=False):
        self.indexes[name or str(keys)] = {"key": keys, "unique": unique}

    def estimated_document_count(self):
        return len(self.docs)

    def index_information(self):
        return self.indexes

    def aggregate(self, pipeline, allowDiskUse=False):
        return [{"stage_count": len(pipeline), "doc_count": len(self.docs)}]


class _FakeDB:
    def __init__(self):
        self.daily_sales = _FakeCollection()
        self.orders_enriched = _FakeCollection()
        self.commands = []

    def __getitem__(self, name):
        return getattr(self, name)

    def list_collection_names(self):
        names = []
        if self.daily_sales.docs:
            names.append("daily_sales")
        if self.orders_enriched.docs:
            names.append("orders_enriched")
        return names

    def command(self, name, payload=None, verbosity=None):
        self.commands.append((name, payload, verbosity))
        if name == "ping":
            return {"ok": 1}
        if name == "explain":
            is_natural = isinstance(payload, dict) and payload.get("hint") == {"$natural": 1}
            stage = "COLLSCAN" if is_natural else "IXSCAN"
            return {
                "queryPlanner": {"winningPlan": {"stage": stage}},
                "executionStats": {
                    "executionSuccess": True,
                    "nReturned": 2,
                    "executionTimeMillis": 25 if is_natural else 1,
                    "totalKeysExamined": 0 if is_natural else 2,
                    "totalDocsExamined": len(self.daily_sales.docs) if is_natural else 2,
                },
            }
        return {}


class _FakeClient:
    def __init__(self, *args, **kwargs):
        self.admin = _FakeDB()
        self.dbs = {}

    def __getitem__(self, name):
        return self.dbs.setdefault(name, _FakeDB())

    def close(self):
        pass


class MongoProfileTests(unittest.TestCase):
    def test_execution_summaries_include_nested_aggregation_stats(self):
        explain = {
            "queryPlanner": {"winningPlan": {"stage": "IXSCAN"}},
            "stages": [
                {"$cursor": {"executionStats": {
                    "nReturned": 50,
                    "executionTimeMillis": 3,
                    "totalKeysExamined": 50,
                    "totalDocsExamined": 50,
                    "executionStages": {"stage": "IXSCAN"},
                }}},
            ],
        }
        self.assertEqual(_execution_summaries(explain), [{
            "nReturned": 50,
            "executionTimeMillis": 3,
            "totalKeysExamined": 50,
            "totalDocsExamined": 50,
        }])
        self.assertEqual(_winning_stages(explain), ["IXSCAN"])

    def test_faceted_and_order_pipelines_cover_required_stages(self):
        faceted = build_faceted_pipeline()
        faceted_stages = {next(iter(stage)) for stage in faceted}
        self.assertEqual(faceted_stages, {"$match", "$facet", "$unwind", "$project"})
        inner_stages = {
            next(iter(step))
            for branch in faceted[1]["$facet"].values()
            for step in branch
        }
        self.assertIn("$group", inner_stages)
        self.assertIn("$project", inner_stages)

        order_pipeline = build_order_items_pipeline()
        order_stages = {next(iter(stage)) for stage in order_pipeline}
        self.assertEqual(order_stages, {"$match", "$unwind", "$facet"})

    def test_compare_index_performance_computes_reduction_and_speedup(self):
        comparison = _compare_index_performance(
            [{"totalDocsExamined": 69065, "executionTimeMillis": 42}],
            [{"totalDocsExamined": 120, "executionTimeMillis": 2}],
        )
        self.assertEqual(comparison["unindexed_docs_examined"], 69065)
        self.assertEqual(comparison["indexed_docs_examined"], 120)
        self.assertEqual(comparison["docs_examined_reduction_ratio"], 575.54)
        self.assertEqual(comparison["speedup_ratio"], 21.0)

    def test_profile_validates_arguments_before_connecting(self):
        with self.assertRaisesRegex(ValueError, "ecommerce_"):
            profile_database("other_database", "seller_123", "report.json")
        with self.assertRaisesRegex(ValueError, "at least 3 characters"):
            profile_database("ecommerce_demo", "ab", "report.json")

    def test_import_and_profile_end_to_end_with_mock_client(self):
        fake_client = _FakeClient()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            daily_tsv = root / "daily.tsv"
            daily_tsv.write_text(
                "2017-05-01\tseller_aaa111\t2\t150.0\t75.0\t100.0\n"
                "2018-05-02\tseller_aaa111\t1\t200.0\t200.0\t200.0\n"
                "2018-05-02\tseller_bbb222\t1\t50.0\t50.0\t50.0\n",
                encoding="utf-8",
            )
            raw_dir = root / "raw"
            raw_dir.mkdir()
            (raw_dir / "olist_orders_dataset.csv").write_text(
                "order_id,customer_id,order_status,order_purchase_timestamp\n"
                "ord_1,cust_1,delivered,2017-05-01 10:00:00\n",
                encoding="utf-8",
            )
            (raw_dir / "olist_order_items_dataset.csv").write_text(
                "order_id,order_item_id,product_id,seller_id,price,freight_value\n"
                "ord_1,1,prod_1,seller_aaa111,150.0,10.0\n",
                encoding="utf-8",
            )
            (raw_dir / "olist_order_reviews_dataset.csv").write_text(
                "order_id,review_score,review_comment_title,review_comment_message\n"
                "ord_1,5,Great,Fast delivery\n",
                encoding="utf-8",
            )

            with patch("ecommerce.mongo.MongoClient", return_value=fake_client), \
                 patch("ecommerce.mongo_profile.MongoClient", return_value=fake_client):
                imported = import_and_analyze(daily_tsv, database="ecommerce_mock", batch_size=2, raw_dir=raw_dir)
                self.assertEqual(imported["daily_rows"], 3)
                self.assertEqual(imported["orders_enriched_docs"], 1)
                self.assertIn("faceted_analytics", imported)
                self.assertIn("order_items_analytics", imported)

                out_json = root / "mongodb-analytics.json"
                report = profile_database("ecommerce_mock", "seller_aaa111", out_json)
                saved = json.loads(out_json.read_text(encoding="utf-8"))
                self.assertEqual(saved["document_count"], 3)
                self.assertEqual(report["query_profile"]["indexed_stages"], ["IXSCAN"])
                self.assertEqual(report["query_profile"]["unindexed_stages"], ["COLLSCAN"])
                self.assertEqual(report["query_profile"]["index_comparison"]["unindexed_docs_examined"], 3)
                self.assertEqual(report["query_profile"]["index_comparison"]["indexed_docs_examined"], 2)
                self.assertIn("faceted_pipeline_profile", saved)
                self.assertIn("orders_enriched_profile", saved)


if __name__ == "__main__":
    unittest.main()
