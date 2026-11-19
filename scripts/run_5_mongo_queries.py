"""Run 5 distinct MongoDB analytical queries on the Brazilian E-Commerce dataset."""
import json
from pymongo import MongoClient

def main():
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client["ecommerce_olist"]
    
    print("=" * 70)
    print("DEMONSTRATING 5 DISTINCT MONGODB ANALYTICAL QUERIES")
    print("=" * 70)
    
    # ---------------------------------------------------------
    # QUERY 1: Annual Marketplace Performance ($match, $group, $project, $sort)
    # ---------------------------------------------------------
    print("\n[Query 1] Annual Marketplace Totals (2016-2018):")
    q1 = [
        {"$match": {"year": {"$gte": 2016, "$lte": 2018}}},
        {"$group": {
            "_id": "$year",
            "active_seller_days": {"$sum": 1},
            "total_orders": {"$sum": "$orders"},
            "total_revenue_brl": {"$sum": "$revenue_brl"},
            "peak_single_day_brl": {"$max": "$max_order_brl"},
            "unique_sellers": {"$addToSet": "$seller_id"}
        }},
        {"$project": {
            "_id": 0,
            "year": "$_id",
            "active_seller_days": 1,
            "total_orders": 1,
            "total_revenue_brl": {"$round": ["$total_revenue_brl", 2]},
            "peak_single_day_brl": {"$round": ["$peak_single_day_brl", 2]},
            "unique_sellers_count": {"$size": "$unique_sellers"}
        }},
        {"$sort": {"year": 1}}
    ]
    for row in db.daily_sales.aggregate(q1):
        print(f"  Year {row['year']}: {row['total_orders']:,} orders | R$ {row['total_revenue_brl']:,.2f} revenue | {row['unique_sellers_count']:,} unique sellers")

    # ---------------------------------------------------------
    # QUERY 2: Top 5 Highest-Grossing Merchants ($group, $sort, $limit)
    # ---------------------------------------------------------
    print("\n[Query 2] Top 5 Merchants by Cumulative GMV:")
    q2 = [
        {"$group": {
            "_id": "$seller_id",
            "cumulative_revenue": {"$sum": "$revenue_brl"},
            "total_orders": {"$sum": "$orders"},
            "active_days": {"$sum": 1}
        }},
        {"$sort": {"cumulative_revenue": -1}},
        {"$limit": 5},
        {"$project": {
            "_id": 0,
            "seller_id": "$_id",
            "cumulative_revenue": {"$round": ["$cumulative_revenue", 2]},
            "total_orders": 1,
            "active_days": 1
        }}
    ]
    for i, row in enumerate(db.daily_sales.aggregate(q2), 1):
        print(f"  #{i} Seller: {row['seller_id']} -> R$ {row['cumulative_revenue']:,.2f} ({row['total_orders']} orders across {row['active_days']} days)")

    # ---------------------------------------------------------
    # QUERY 3: Seller Revenue Tier Segmentation ($group, $cond, $group)
    # ---------------------------------------------------------
    print("\n[Query 3] Merchant Pareto Segmentation (High / Medium / Low Tiers):")
    q3 = [
        {"$group": {"_id": "$seller_id", "rev": {"$sum": "$revenue_brl"}}},
        {"$project": {
            "_id": 0,
            "tier": {
                "$cond": [
                    {"$gte": ["$rev", 10000]}, "High Tier (>= R$ 10k)",
                    {"$cond": [{"$gte": ["$rev", 1000]}, "Medium Tier (R$ 1k - 10k)", "Low Tier (< R$ 1k)"]}
                ]
            },
            "rev": 1
        }},
        {"$group": {
            "_id": "$tier",
            "merchant_count": {"$sum": 1},
            "tier_revenue": {"$sum": "$rev"}
        }},
        {"$project": {
            "_id": 0,
            "tier": "$_id",
            "merchant_count": 1,
            "tier_revenue": {"$round": ["$tier_revenue", 2]}
        }},
        {"$sort": {"tier_revenue": -1}}
    ]
    for row in db.daily_sales.aggregate(q3):
        print(f"  Tier: {row['tier']} -> {row['merchant_count']:,} merchants | R$ {row['tier_revenue']:,.2f}")

    # ---------------------------------------------------------
    # QUERY 4: Order Line Items Unwinding & Freight Ratios ($match, $unwind, $group)
    # ---------------------------------------------------------
    print("\n[Query 4] Order Line Items Unwinding & Freight Share (Top 3 Sellers):")
    q4 = [
        {"$match": {"order_status": {"$nin": ["canceled", "unavailable"]}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.seller_id",
            "items_sold": {"$sum": 1},
            "total_item_sales": {"$sum": "$items.price"},
            "total_freight": {"$sum": "$items.freight_value"}
        }},
        {"$sort": {"total_item_sales": -1}},
        {"$limit": 3},
        {"$project": {
            "_id": 0,
            "seller_id": "$_id",
            "items_sold": 1,
            "total_item_sales": {"$round": ["$total_item_sales", 2]},
            "total_freight": {"$round": ["$total_freight", 2]},
            "freight_percentage": {"$round": [{"$multiply": [{"$divide": ["$total_freight", "$total_item_sales"]}, 100]}, 2]}
        }}
    ]
    for row in db.orders_enriched.aggregate(q4, allowDiskUse=True):
        print(f"  Seller {row['seller_id']}: {row['items_sold']:,} items | Sales: R$ {row['total_item_sales']:,.2f} | Freight: R$ {row['total_freight']:,.2f} ({row['freight_percentage']}%)")

    # ---------------------------------------------------------
    # QUERY 5: Customer Review Scores vs. Average Item Price ($match, $unwind, $group)
    # ---------------------------------------------------------
    print("\n[Query 5] Customer Satisfaction (Review Ratings 1 to 5 Stars vs Price):")
    q5 = [
        {"$match": {"order_status": {"$nin": ["canceled", "unavailable"]}, "review.score": {"$ne": None}}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$review.score",
            "rated_items_count": {"$sum": 1},
            "avg_item_price": {"$avg": "$items.price"}
        }},
        {"$project": {
            "_id": 0,
            "star_rating": "$_id",
            "rated_items_count": 1,
            "avg_item_price": {"$round": ["$avg_item_price", 2]}
        }},
        {"$sort": {"star_rating": -1}}
    ]
    for row in db.orders_enriched.aggregate(q5, allowDiskUse=True):
        print(f"  {row['star_rating']} Stars: {row['rated_items_count']:,} items | Avg Item Price: R$ {row['avg_item_price']:,.2f}")

    print("\n" + "=" * 70)
    print("ALL 5 QUERIES EXECUTED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    main()
