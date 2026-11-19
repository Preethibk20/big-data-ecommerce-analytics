"""Execute the 8 MongoDB queries shown in MongoDB Compass / Atlas."""
import os
from pathlib import Path
from pymongo import MongoClient

def get_mongodb_uri():
    if os.environ.get("MONGODB_URI"):
        return os.environ["MONGODB_URI"]
    for path in [Path(".env"), Path("../atlas-credentials.env"), Path("atlas-credentials.env")]:
        if path.is_file():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.startswith("MONGODB_URI="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return "mongodb://127.0.0.1:27017"

def main():
    uri = get_mongodb_uri()
    client = MongoClient(uri)
    db = client["OlistDB"]

    print("=" * 80)
    print("DEMONSTRATING THE 8 MONGODB COMPASS AGGREGATION QUERIES (OlistDB)")
    print("=" * 80)

    # 1. Delivered Orders Analysis (Collection: orders)
    print("\n[Query 1] Delivered Orders Analysis (Collection: orders):")
    q1 = [
        {"$match": {"order_status": "delivered"}},
        {"$group": {
            "_id": {"$substr": ["$order_purchase_timestamp", 0, 4]},
            "delivered_orders_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "year": "$_id", "delivered_orders_count": 1}}
    ]
    for row in db.orders.aggregate(q1):
        print(f"  Year {row['year']}: {row['delivered_orders_count']:,} delivered orders")

    # 2. Orders Facet Analysis (Collection: orders)
    print("\n[Query 2] Orders Facet Analysis (Collection: orders):")
    q2 = [
        {"$facet": {
            "status_distribution": [
                {"$group": {"_id": "$order_status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ],
            "yearly_distribution": [
                {"$group": {"_id": {"$substr": ["$order_purchase_timestamp", 0, 4]}, "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
        }}
    ]
    res2 = list(db.orders.aggregate(q2))[0]
    print("  Status Breakdown:", res2["status_distribution"])
    print("  Yearly Breakdown:", res2["yearly_distribution"])

    # 3. Payment Type Analysis (Collection: order_payments)
    print("\n[Query 3] Payment Type Analysis (Collection: order_payments):")
    q3 = [
        {"$group": {
            "_id": "$payment_type",
            "total_transactions": {"$sum": 1},
            "total_payment_value": {"$sum": "$payment_value"},
            "avg_payment_value": {"$avg": "$payment_value"},
            "avg_installments": {"$avg": "$payment_installments"}
        }},
        {"$sort": {"total_payment_value": -1}},
        {"$project": {
            "_id": 0,
            "payment_type": "$_id",
            "total_transactions": 1,
            "total_payment_value": {"$round": ["$total_payment_value", 2]},
            "avg_payment_value": {"$round": ["$avg_payment_value", 2]},
            "avg_installments": {"$round": ["$avg_installments", 2]}
        }}
    ]
    for row in db.order_payments.aggregate(q3):
        print(f"  Type: {row['payment_type']:<12} | {row['total_transactions']:,} txns | Total: R$ {row['total_payment_value']:,.2f} | Avg: R$ {row['avg_payment_value']:.2f} | Avg Installments: {row['avg_installments']}")

    # 4. Top 10 Brazilian states with highest number of sellers (Collection: sellers)
    print("\n[Query 4] Top 10 Brazilian states with the highest number of sellers (Collection: sellers):")
    q4 = [
        {"$group": {"_id": "$seller_state", "seller_count": {"$sum": 1}}},
        {"$sort": {"seller_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "state": "$_id", "seller_count": 1}}
    ]
    for idx, row in enumerate(db.sellers.aggregate(q4), 1):
        print(f"  #{idx:<2} State: {row['state']} -> {row['seller_count']:,} sellers")

    # 5. Top 10 Customer States (Collection: customers)
    print("\n[Query 5] Top 10 Customer States (Collection: customers):")
    q5 = [
        {"$group": {"_id": "$customer_state", "customer_count": {"$sum": 1}}},
        {"$sort": {"customer_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "state": "$_id", "customer_count": 1}}
    ]
    for idx, row in enumerate(db.customers.aggregate(q5), 1):
        print(f"  #{idx:<2} State: {row['state']} -> {row['customer_count']:,} customers")

    # 6. Top 10 Orders by Item Value (Collection: order_items)
    print("\n[Query 6] Top 10 Orders by Item Value (Collection: order_items):")
    q6 = [
        {"$group": {
            "_id": "$order_id",
            "total_item_value": {"$sum": "$price"},
            "items_count": {"$sum": 1}
        }},
        {"$sort": {"total_item_value": -1}},
        {"$limit": 10},
        {"$project": {
            "_id": 0,
            "order_id": "$_id",
            "total_item_value": {"$round": ["$total_item_value", 2]},
            "items_count": 1
        }}
    ]
    for idx, row in enumerate(db.order_items.aggregate(q6), 1):
        print(f"  #{idx:<2} Order: {row['order_id']} -> R$ {row['total_item_value']:,.2f} ({row['items_count']} items)")

    # 7. Top 10 Product Categories (Collection: products)
    print("\n[Query 7] Top 10 Product Categories (Collection: products):")
    q7 = [
        {"$match": {"product_category_name": {"$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$product_category_name", "product_count": {"$sum": 1}}},
        {"$sort": {"product_count": -1}},
        {"$limit": 10},
        {"$project": {"_id": 0, "category": "$_id", "product_count": 1}}
    ]
    for idx, row in enumerate(db.products.aggregate(q7), 1):
        print(f"  #{idx:<2} Category: {row['category']:<30} -> {row['product_count']:,} products")

    # 8. Top 5 Orders by Total Item Value Using Unwind (Collection: order_items)
    print("\n[Query 8] Top 5 Orders by Total Item Value Using Unwind (Collection: order_items):")
    q8 = [
        {"$group": {
            "_id": "$order_id",
            "items": {"$push": {"price": "$price", "product_id": "$product_id"}}
        }},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$_id",
            "total_item_value": {"$sum": "$items.price"},
            "items_count": {"$sum": 1}
        }},
        {"$sort": {"total_item_value": -1}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "order_id": "$_id",
            "total_item_value": {"$round": ["$total_item_value", 2]},
            "items_count": 1
        }}
    ]
    for idx, row in enumerate(db.order_items.aggregate(q8, allowDiskUse=True), 1):
        print(f"  #{idx:<2} Order: {row['order_id']} -> R$ {row['total_item_value']:,.2f} ({row['items_count']} items unwound)")

    print("\n" + "=" * 80)
    print("ALL 8 COMPASS / ATLAS QUERIES EXECUTED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    main()
