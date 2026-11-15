# Big Data Analytics Report Outline: Brazilian E-Commerce

1. **Dataset Overview** — Kaggle Brazilian E-Commerce Public Dataset by Olist; describe the relational schemas (`orders`, `order_items`, `sellers`, `products`), transaction count (98,000+ valid orders, 112,000+ items), 3,000+ merchants, and 2016–2018 scope.
2. **Ingestion & Data Preparation** — Explain order lifecycle filtering (excluding canceled/unavailable), timestamp date extraction, item price validation, and daily grain aggregation per merchant.
3. **Data Semantics & Business Metrics** — Define core commercial metrics: Total Revenue (R$), Order Counts, Mean Daily Revenue (R$/day), Max Daily Revenue, and Peak Single Item Price.
4. **Architecture & Pipeline Design** — Illustrate the multi-system flow: Python streaming ETL, Hadoop MapReduce (mapper/reducer), Apache Pig schema validation, Apache Hive external Text and compressed RCFile tables, and MongoDB indexing.
5. **Analytical Findings** — Highlight commercial insights: annual marketplace growth from 2016 to 2018, seller concentration, revenue distributions, and top merchants.
6. **Cross-System Validation** — Compare annual aggregates computed independently across Python reference analytics, local MapReduce, MongoDB aggregation pipeline, and Hive queries; demonstrate zero discrepancies.
7. **Storage & Performance Optimization** — Evaluate storage footprint and query performance between uncompressed Text, compressed RCFile in Hive, and compound B-tree indexing in MongoDB (`seller_year`).
8. **Interactive Dashboard** — Document the Flask analytics web application: Page 1 seller lookup with dynamic SVG pie metric shares and revenue progression bars; Page 2 annual leaderboards with rank badges and top/bottom comparison cards.
9. **Coursework Evidence** — Include command outputs, test execution logs, dashboard screenshots, and schema manifests.
