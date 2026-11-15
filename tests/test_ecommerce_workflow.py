import csv
import tempfile
import unittest
from pathlib import Path

from ecommerce.analytics import analyze, year_seller_ranking
from ecommerce.dashboard import create_app
from ecommerce.prepare import prepare


class EcommerceWorkflowTests(unittest.TestCase):
    def make_source(self, directory, bad_price=None):
        orders_path = directory / "olist_orders_dataset.csv"
        items_path = directory / "olist_order_items_dataset.csv"

        with orders_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow([
                "order_id", "customer_id", "order_status",
                "order_purchase_timestamp", "order_approved_at",
                "order_delivered_carrier_date", "order_delivered_customer_date",
                "order_estimated_delivery_date"
            ])
            # Order 1: Seller A, 2017-05-01
            writer.writerow(["ord_1", "cust_1", "delivered", "2017-05-01 10:00:00", "", "", "", ""])
            # Order 2: Seller A, 2017-05-02
            writer.writerow(["ord_2", "cust_2", "delivered", "2017-05-02 11:00:00", "", "", "", ""])
            # Order 3: Seller B, 2017-05-02
            writer.writerow(["ord_3", "cust_3", "delivered", "2017-05-02 12:00:00", "", "", "", ""])
            # Order 4: Canceled order (should be skipped)
            writer.writerow(["ord_4", "cust_4", "canceled", "2017-05-03 12:00:00", "", "", "", ""])

        with items_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow([
                "order_id", "order_item_id", "product_id",
                "seller_id", "shipping_limit_date", "price", "freight_value"
            ])
            p1 = bad_price if bad_price is not None else "100.00"
            writer.writerow(["ord_1", "1", "prod_1", "seller_aaa111", "2017-05-05", p1, "10.00"])
            writer.writerow(["ord_2", "1", "prod_2", "seller_aaa111", "2017-05-06", "50.00", "5.00"])
            writer.writerow(["ord_3", "1", "prod_3", "seller_bbb222", "2017-05-06", "200.00", "15.00"])
            # canceled order item
            writer.writerow(["ord_4", "1", "prod_4", "seller_aaa111", "2017-05-07", "500.00", "20.00"])

    def test_preparation_analysis_and_dashboard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw"
            raw.mkdir()
            self.make_source(raw)

            manifest = prepare(raw, root / "prepared")
            self.assertEqual(manifest["valid_orders"], 3)
            self.assertEqual(manifest["matched_items"], 3)
            self.assertEqual(manifest["daily_seller_rows"], 3)
            self.assertEqual(manifest["unique_sellers"], 2)
            self.assertEqual(manifest["first_day"], "2017-05-01")
            self.assertEqual(manifest["last_day"], "2017-05-02")

            output = root / "results"
            result = analyze(root / "prepared/daily.tsv", output)
            self.assertEqual(result["mapreduce_crosscheck"], "passed")
            self.assertEqual(result["total_revenue_brl"], 350.0)
            self.assertEqual(result["total_orders"], 3)
            self.assertEqual(result["sellers"], 2)
            self.assertEqual(result["years"], [2017])

            seller_a = next(r for r in result["records"] if r["seller_id"] == "seller_aaa111")
            self.assertEqual(seller_a["days"], 2)
            self.assertEqual(seller_a["orders"], 2)
            self.assertEqual(seller_a["revenue_brl"], 150.0)
            self.assertEqual(seller_a["mean_daily_revenue"], 75.0)
            self.assertEqual(seller_a["max_daily_revenue"], 100.0)
            self.assertEqual(seller_a["peak_order_brl"], 100.0)

            seller_b = next(r for r in result["records"] if r["seller_id"] == "seller_bbb222")
            self.assertEqual(seller_b["days"], 1)
            self.assertEqual(seller_b["orders"], 1)
            self.assertEqual(seller_b["revenue_brl"], 200.0)

            # Test ranking
            ranking = year_seller_ranking(result, 2017, "revenue_brl", 1)
            self.assertEqual(ranking["most"]["seller_id"], "seller_bbb222")
            self.assertEqual(ranking["least"]["seller_id"], "seller_aaa111")
            self.assertEqual(len(ranking["sellers"]), 1)

            with self.assertRaisesRegex(ValueError, "Top K"):
                year_seller_ranking(result, 2017, "revenue_brl", 3)

            # Test Flask dashboard
            app = create_app(output)
            client = app.test_client()

            # Home page (default seller view)
            res = client.get("/")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Seller Analytics Engine", res.data)

            # Seller lookup
            res_seller = client.get("/?seller_id=seller_aaa111")
            self.assertEqual(res_seller.status_code, 200)
            self.assertIn(b"seller_aaa111", res_seller.data)
            self.assertIn(b"Annual Share", res_seller.data)

            # Prefix lookup
            res_prefix = client.get("/?seller_id=seller_bbb")
            self.assertEqual(res_prefix.status_code, 200)
            self.assertIn(b"seller_bbb222", res_prefix.data)

            # Metric selector
            for metric, label in [
                ("revenue_brl", "Total Revenue"),
                ("orders", "Total Orders"),
                ("mean_daily_revenue", "Mean Revenue/Day"),
                ("max_daily_revenue", "Max Daily Revenue"),
                ("peak_order_brl", "Peak Order Value"),
            ]:
                resp = client.get(f"/?seller_id=seller_aaa111&pie_metric={metric}")
                self.assertEqual(resp.status_code, 200)
                self.assertIn(label.encode(), resp.data)

            # Leaderboard view
            res_year = client.get("/?page=year&year=2017&top_k=2")
            self.assertEqual(res_year.status_code, 200)
            self.assertIn(b"Annual Seller Leaderboard", res_year.data)
            self.assertIn(b"seller_bbb222", res_year.data)
            self.assertIn(b"seller_aaa111", res_year.data)

    def test_dashboard_validation_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw"
            raw.mkdir()
            self.make_source(raw)
            prepare(raw, root / "prepared")
            analyze(root / "prepared/daily.tsv", root / "results")

            client = create_app(root / "results").test_client()
            missing = client.get("/?seller_id=non_existent_seller_id")
            self.assertEqual(missing.status_code, 200)
            self.assertIn(b"No records found", missing.data)

            self.assertEqual(client.get("/?page=unknown").status_code, 400)
            self.assertEqual(client.get("/?page=year&year=1999").status_code, 400)
            self.assertEqual(client.get("/?page=year&year=2017&metric=unknown").status_code, 400)
            self.assertEqual(client.get("/?page=year&year=2017&top_k=0").status_code, 400)
            self.assertEqual(client.get("/?page=year&year=2017&top_k=abc").status_code, 400)

    def test_bad_price_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw"
            raw.mkdir()
            self.make_source(raw, bad_price="-25.00")
            with self.assertRaisesRegex(ValueError, "Invalid non-finite or negative price"):
                prepare(raw, root / "prepared")


if __name__ == "__main__":
    unittest.main()
