"""Generate a comprehensive, professional PowerPoint presentation for the Big Data Analytics project."""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Paths
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PPTX = ROOT / "results" / "BDA_Final_Project_Presentation.pptx"
IMAGES_DIR = ROOT / "results" / "report_images"

# Color Palette (Corporate Academic Tech)
COLOR_NAVY = RGBColor(10, 37, 64)        # Deep Navy (Primary brand)
COLOR_EMERALD = RGBColor(5, 150, 105)    # Emerald Accent
COLOR_SLATE_DARK = RGBColor(30, 41, 59)  # Code box background
COLOR_TEXT_MAIN = RGBColor(15, 23, 42)   # Dark Slate Body
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)
COLOR_CODE_TEXT = RGBColor(241, 245, 249)
COLOR_LIGHT_BG = RGBColor(248, 250, 252)
COLOR_CARD_BORDER = RGBColor(226, 232, 240)
COLOR_AMBER = RGBColor(217, 119, 6)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_CARD_BG = RGBColor(241, 245, 249)
COLOR_CALLOUT_BG = RGBColor(236, 253, 245)
COLOR_CALLOUT_BORDER = RGBColor(16, 185, 129)


def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, step_tag="BIG DATA ANALYTICS · BCS714D"):
        # Header banner
        header_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15)
        )
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = COLOR_NAVY
        header_shape.line.fill.background()

        # Step tag
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.3))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = step_tag.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGBColor(110, 231, 183)  # Mint/Emerald

        # Title
        tx_box2 = slide.shapes.add_textbox(Inches(0.8), Inches(0.40), Inches(11.7), Inches(0.65))
        tf2 = tx_box2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(22)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_WHITE

    def add_card(slide, left, top, width, height, bg_color=COLOR_LIGHT_BG, border_color=COLOR_CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
        return shape

    def add_code_box(slide, left, top, width, height, header_label, code_text):
        card = add_card(slide, left, top, width, height, bg_color=COLOR_SLATE_DARK, border_color=COLOR_SLATE_DARK)
        tx_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), height - Inches(0.2))
        tf = tx_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"# {header_label}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(148, 163, 184)
        
        p2 = tf.add_paragraph()
        p2.text = code_text
        p2.font.name = "Consolas"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_CODE_TEXT

    def add_output_box(slide, left, top, width, height, header_label, output_text):
        card = add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        tx_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), height - Inches(0.2))
        tf = tx_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"OUTPUT: {header_label}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_EMERALD
        
        p2 = tf.add_paragraph()
        p2.text = output_text
        p2.font.name = "Consolas"
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MAIN

    def add_viva_callout(slide, left, top, width, height, callout_text):
        card = add_card(slide, left, top, width, height, bg_color=COLOR_CALLOUT_BG, border_color=COLOR_CALLOUT_BORDER)
        tx_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), width - Inches(0.3), height - Inches(0.2))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "EXPLANATION TO FACULTY / VIVA KEY POINT"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(4, 120, 87)
        
        p2 = tf.add_paragraph()
        p2.text = callout_text
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_TEXT_MAIN

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY
    bg1.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(4.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "BCS714D · BIG DATA ANALYTICS PROJECT PRESENTATION"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(110, 231, 183)
    
    p2 = tf1.add_paragraph()
    p2.text = "Brazilian E-Commerce (Olist)\nSales & Merchant Analytics"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE
    p2.space_before = Pt(12)
    p2.space_after = Pt(14)

    p3 = tf1.add_paragraph()
    p3.text = "Distributed Processing Across Multi-Node Hadoop 2.10.2, YARN MapReduce, MongoDB 7.0, Apache Pig, Apache Hive RCFile Benchmarking & Interactive Flask Dashboard"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    
    # Metadata card at bottom
    add_card(s1, Inches(1.0), Inches(5.4), Inches(11.333), Inches(1.4), bg_color=RGBColor(15, 23, 42), border_color=RGBColor(51, 65, 85))
    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(5.5), Inches(10.9), Inches(1.2))
    mtf = meta_box.text_frame
    mtf.word_wrap = True
    mp = mtf.paragraphs[0]
    mp.text = "Evaluation Details & Architecture Topology:"
    mp.font.bold = True
    mp.font.size = Pt(12)
    mp.font.color.rgb = RGBColor(241, 245, 249)
    
    mp2 = mtf.add_paragraph()
    mp2.text = "• Course: BCS714D (Sections 7A/7B)  |  Faculty In-Charge: Sandhiya B\n• Dataset: Kaggle Brazilian E-Commerce Public Dataset by Olist (100k+ Orders, 2016–2018)\n• Cluster Topology: 3-Node Distributed Cluster (1 Master NameNode/ResourceManager + 2 DataNode/NodeManager Workers)"
    mp2.font.size = Pt(11)
    mp2.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================================
    # SLIDE 2: End-to-End System Architecture
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "End-to-End System Architecture & Distributed Pipeline", "ARCHITECTURAL OVERVIEW")
    
    img_arch = IMAGES_DIR / "figure1_architecture.png"
    if img_arch.is_file():
        s2.shapes.add_picture(str(img_arch), Inches(0.8), Inches(1.4), width=Inches(6.2))
        
    add_card(s2, Inches(7.3), Inches(1.4), Inches(5.2), Inches(5.6))
    abox = s2.shapes.add_textbox(Inches(7.5), Inches(1.5), Inches(4.8), Inches(5.4))
    atf = abox.text_frame
    atf.word_wrap = True
    
    p = atf.paragraphs[0]
    p.text = "Distributed Toolchain & Responsibilities:"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_NAVY
    
    items = [
        ("Python Streaming ETL", "Extracts raw orders & items, filters canceled transactions, validates numeric bounds, and streams daily per-seller aggregations (daily.tsv)."),
        ("MongoDB 7.0 Ingestion", "Document persistence with compound index (seller_id, year) and review rating arrays. Exercises multi-stage pipelines ($match, $unwind, $facet, $group)."),
        ("HDFS & YARN MapReduce", "Stores daily.tsv with replication factor 2. Python streaming mapper and reducer execute across 2 worker nodes to generate annual seller aggregates."),
        ("Apache Pig 0.17.0", "Pig Latin regex schema validation and filtering of null/negative financial records prior to data warehouse storage."),
        ("Apache Hive 2.3.9", "External Text vs columnar compressed RCFile (GzipCodec) storage benchmarking and SQL analytical aggregations."),
        ("Interactive Flask UI", "Read-only web dashboard serving seller deep-dives and annual leaderboards with dynamic SVG pie charts and ranking badges.")
    ]
    for title, desc in items:
        p = atf.add_paragraph()
        p.text = f"• {title}: "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_before = Pt(6)
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_TEXT_MUTED

    # =========================================================================
    # SLIDE 3: Dataset Ingestion & 2016 Pilot Context
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Dataset Schema, Validation & 2016 Pilot Launch Context", "DATASET FOUNDATION")

    add_card(s3, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6))
    dbox = s3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.4))
    dtf = dbox.text_frame
    dtf.word_wrap = True
    
    dp = dtf.paragraphs[0]
    dp.text = "Olist Public Dataset Schema & Scale:"
    dp.font.bold = True
    dp.font.size = Pt(13)
    dp.font.color.rgb = COLOR_NAVY
    
    schema_info = [
        ("olist_orders_dataset.csv", "99,441 raw orders -> 98,207 valid orders (canceled/unavailable orders filtered)."),
        ("olist_order_items_dataset.csv", "112,650 line items -> 112,101 matched valid items with verified prices."),
        ("olist_sellers_dataset.csv", "3,053 unique active merchants across Brazilian states."),
        ("olist_order_reviews_dataset.csv", "Customer review scores (1-5 stars) and Portuguese comment messages."),
        ("Normalized daily.tsv", "69,065 daily seller grain summaries across 2016–2018."),
        ("Financial Scope", "Total GMV of R$ 13,494,400.74 across 4,254 (seller, year) groups.")
    ]
    for t, d in schema_info:
        p = dtf.add_paragraph()
        p.text = f"• {t}: "
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_before = Pt(5)
        r = p.add_run()
        r.text = d
        r.font.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT_MUTED

    # Right side: 2016 context card
    add_card(s3, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6))
    pbox = s3.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.4))
    ptf = pbox.text_frame
    ptf.word_wrap = True
    
    p = ptf.paragraphs[0]
    p.text = "Why is 2016 Volume Low (Showing 0 for Many Sellers)?"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_AMBER
    
    p_pts = [
        ("Pilot Launch Period", "Olist began recording public marketplace orders on September 4, 2016. Thus, 2016 spans only 4 months of early rollout."),
        ("Marketplace Scale Comparison", "• 2016: 348 orders | 134 sellers | R$ 44,726.06\n• 2017: 50,617 orders | 1,766 sellers | R$ 6,108,492.27\n• 2018: 61,136 orders | 2,354 sellers | R$ 7,341,182.41"),
        ("Why Sellers Show 0 in 2016", "Out of 3,053 total sellers, only 134 existed in 2016. Over 95.6% of merchants onboarded in 2017 or 2018. Top seller 4869f7a... joined in 2017, so its 2016 activity is factually 0."),
        ("Full Multi-Year Integration", "Our updated dashboard explicitly includes 2016 across all charts, tables, and pie metrics, ensuring full 2016-2018 multi-year compliance.")
    ]
    for t, d in p_pts:
        p = ptf.add_paragraph()
        p.text = f"• {t}: "
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_before = Pt(5)
        r = p.add_run()
        r.text = d
        r.font.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Step 0 & 1 — Environment Startup & System Verification
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Step 0 & Step 1: Cluster Startup & Automated Unit Testing", "THEME 2 / SYSTEM VERIFICATION")

    add_code_box(s4, Inches(0.8), Inches(1.4), Inches(6.0), Inches(1.5),
                 "Step 0: Spin Up 3-Node Containerized Cluster",
                 "docker compose -f infra/compose.yaml up -d\ndocker ps --format \"table {{.Names}}\\t{{.Status}}\"")

    add_code_box(s4, Inches(0.8), Inches(3.0), Inches(6.0), Inches(1.5),
                 "Step 1: Execute Automated Unit Testing Suite",
                 "python -m unittest discover -s tests -v")

    add_output_box(s4, Inches(0.8), Inches(4.6), Inches(6.0), Inches(2.4),
                   "All 8 Unit Tests Passing (0.35s)",
                   "test_bad_price_raises_error ... ok\ntest_dashboard_validation_and_errors ... ok\ntest_preparation_analysis_and_dashboard ... ok\ntest_compare_index_performance_computes_reduction ... ok\ntest_execution_summaries_include_nested_stats ... ok\ntest_faceted_and_order_pipelines_cover_stages ... ok\ntest_import_and_profile_end_to_end_mock ... ok\ntest_profile_validates_arguments ... ok\n\nRan 8 tests in 0.350s  -->  OK")

    img_tests = IMAGES_DIR / "screenshot_tests_and_prepare.png"
    if img_tests.is_file():
        s4.shapes.add_picture(str(img_tests), Inches(7.1), Inches(1.4), width=Inches(5.4))
        
    add_viva_callout(s4, Inches(7.1), Inches(5.1), Inches(5.4), Inches(1.9),
                     "Confirms system integrity: unit tests validate rejection of non-finite/negative prices, verify mathematical parity between pure Python and MapReduce, and test multi-stage MongoDB pipeline compilation.")

    # =========================================================================
    # SLIDE 5: Step 2 — Cluster Health Check
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Step 2: Distributed Cluster Health & Node Verification", "THEME 2 · HADOOP CLUSTER VERIFICATION")

    add_code_box(s5, Inches(0.8), Inches(1.4), Inches(6.0), Inches(1.6),
                 "Verify Live DataNodes & YARN NodeManagers",
                 "docker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"hdfs dfsadmin -report | grep 'Live datanodes'\"\ndocker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"yarn node -list\"")

    add_output_box(s5, Inches(0.8), Inches(3.1), Inches(6.0), Inches(2.1),
                   "Cluster Topology Live Report",
                   "Live datanodes (2):\n\nTotal Nodes: 2\n  Node-Id         Node-State    Node-Http-Address   Number-of-Containers\n  worker1:8041    RUNNING       worker1:8042        0\n  worker2:8041    RUNNING       worker2:8042        0")

    add_viva_callout(s5, Inches(0.8), Inches(5.3), Inches(6.0), Inches(1.7),
                     "Demonstrates that HDFS has 2 active DataNodes with Safe Mode OFF, replication factor 2 enabled, and YARN has 2 active NodeManagers ready to execute distributed MapReduce jobs.")

    img_cluster = IMAGES_DIR / "screenshot_theme2_cluster_verify.png"
    if img_cluster.is_file():
        s5.shapes.add_picture(str(img_cluster), Inches(7.1), Inches(1.4), width=Inches(5.4))

    # =========================================================================
    # SLIDE 6: Step 3 (Theme 1) — MongoDB Ingestion & Document Linkage
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Theme 1 (Part A): MongoDB Ingestion & Document Linkage", "THEME 1 · MONGODB BIG DATA PROCESSING")

    add_code_box(s6, Inches(0.8), Inches(1.4), Inches(6.0), Inches(1.8),
                 "Verify Document Counts Across Ingested Collections",
                 "python -c \"from pymongo import MongoClient; \\\nclient = MongoClient('mongodb://127.0.0.1:27017'); \\\ndb = client['ecommerce_olist']; \\\nprint('Collections:', db.list_collection_names()); \\\nprint('daily_sales docs:', db.daily_sales.count_documents({})); \\\nprint('orders_enriched docs:', db.orders_enriched.count_documents({}))\"")

    add_output_box(s6, Inches(0.8), Inches(3.3), Inches(6.0), Inches(1.8),
                   "Ingested Collection Document Counts",
                   "Collections: ['daily_sales', 'orders_enriched']\ndaily_sales docs: 69065\norders_enriched docs: 99441")

    add_viva_callout(s6, Inches(0.8), Inches(5.2), Inches(6.0), Inches(1.8),
                     "'Ingested document counts' is the sanity proof to faculty that the database is populated. daily_sales holds 69,065 daily seller summaries. orders_enriched links 99,441 orders with embedded item arrays and customer review ratings.")

    img_mongo = IMAGES_DIR / "screenshot_theme1_mongodb.png"
    if img_mongo.is_file():
        s6.shapes.add_picture(str(img_mongo), Inches(7.1), Inches(1.4), width=Inches(5.4))

    # =========================================================================
    # SLIDE 7: Step 3 (Theme 1) — 5 Distinct MongoDB Queries
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Theme 1 (Part B): MongoDB Compass & Atlas Aggregations (OlistDB)", "THEME 1 · ADVANCED AGGREGATION PIPELINES")

    add_code_box(s7, Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.9),
                 "Command to Execute Compass / Atlas Aggregations",
                 "python scripts/run_atlas_compass_queries.py")

    # Table of 5 queries
    table_shape = s7.shapes.add_table(6, 4, Inches(0.8), Inches(2.3), Inches(11.7), Inches(4.7))
    tbl = table_shape.table
    tbl.columns[0].width = Inches(1.4)
    tbl.columns[1].width = Inches(2.6)
    tbl.columns[2].width = Inches(3.2)
    tbl.columns[3].width = Inches(4.5)

    headers = ["Query #", "Business Goal", "MongoDB Operators", "Actual Executed Output / Insight"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_WHITE

    q_data = [
        ("Query 1", "Annual Marketplace Totals", "$match, $group, $project, $sort, $addToSet, $size", "2016: 348 orders | R$ 44.7k | 134 sellers\n2017: 50,617 orders | R$ 6.11M | 1,766 sellers\n2018: 61,136 orders | R$ 7.34M | 2,354 sellers"),
        ("Query 2", "Top 5 Merchants by GMV", "$group, $sort, $limit, $project", "#1 Seller 4869f7a...: R$ 229,237.63 (1,155 orders)\n#2 Seller 5324358...: R$ 222,776.05 (410 orders)\n#3 Seller 4a3ca93...: R$ 200,326.12 (1,985 orders)"),
        ("Query 3", "Merchant Pareto Segmentation", "$group, $cond, $group, $project", "High Tier (>= R$ 10k): 289 merchants | R$ 8.94M (66.3%)\nMedium Tier (R$ 1k-10k): 1,125 merchants | R$ 4.01M\nLow Tier (< R$ 1k): 1,639 merchants | R$ 539.7k"),
        ("Query 4", "Line Items Unwind & Freight", "$match, $unwind, $group, $sort, $limit", "Top seller 4869f7a...: 1,155 items | Sales: R$ 229.2k | Freight: R$ 20.1k (8.79% freight ratio)"),
        ("Query 5", "Customer Reviews vs Price", "$match, $unwind, $group, $sort, $avg", "5 Stars: 63,107 items (Avg R$ 121.39)\n1 Star: 13,735 items (Avg R$ 125.96) — higher priced items encounter stricter customer expectations")
    ]
    for row_idx, row_vals in enumerate(q_data, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = tbl.cell(row_idx, col_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(9.5)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
            elif col_idx == 2:
                p.font.name = "Consolas"
                p.font.size = Pt(8.5)
                p.font.color.rgb = COLOR_EMERALD

    # =========================================================================
    # SLIDE 8: Step 3 (Theme 1) — Query Profiling: IXSCAN vs COLLSCAN
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Theme 1 (Part C): Query Profiling (.explain('executionStats'))", "THEME 1 · QUERY OPTIMIZATION & INDEX PROFILING")

    add_code_box(s8, Inches(0.8), Inches(1.4), Inches(6.0), Inches(1.4),
                 "Profile Query Execution Plan",
                 "python -m ecommerce.mongo_profile \\\n  --database ecommerce_olist \\\n  --seller-id \"4869f7a5dfa277a7dca6462dcf3b52b2\" \\\n  --output \"results/mongodb-analytics.json\"")

    # Table of stats
    t_shape = s8.shapes.add_table(5, 3, Inches(0.8), Inches(2.9), Inches(6.0), Inches(2.2))
    tbl8 = t_shape.table
    tbl8.columns[0].width = Inches(2.4)
    tbl8.columns[1].width = Inches(1.8)
    tbl8.columns[2].width = Inches(1.8)

    h8 = ["Execution Metric", "Unindexed (COLLSCAN)", "Indexed (IXSCAN)"]
    for i, h in enumerate(h8):
        c = tbl8.cell(0, i)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_NAVY
        p = c.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_WHITE

    stats_data = [
        ("Winning Plan Stages", "COLLSCAN", "IXSCAN -> FETCH"),
        ("totalDocsExamined", "22,973 documents", "100 documents"),
        ("totalKeysExamined", "0 keys", "100 keys"),
        ("executionTimeMillis", "17 ms", "3 ms")
    ]
    for r_idx, r_vals in enumerate(stats_data, start=1):
        for c_idx, val in enumerate(r_vals):
            c = tbl8.cell(r_idx, c_idx)
            c.text = val
            p = c.text_frame.paragraphs[0]
            p.font.size = Pt(10)
            if c_idx == 2:
                p.font.bold = True
                p.font.color.rgb = COLOR_EMERALD

    add_viva_callout(s8, Inches(0.8), Inches(5.2), Inches(6.0), Inches(1.8),
                     "Core Result: Compound index (seller_id, year) delivers a 229.73x reduction in examined documents (100 vs 22,973) and a 5.67x execution speedup (3ms vs 17ms) by avoiding full collection scans.")

    img_prof = IMAGES_DIR / "theme1_mongodb_index_profiling.png"
    if img_prof.is_file():
        s8.shapes.add_picture(str(img_prof), Inches(7.1), Inches(1.4), width=Inches(5.4))

    # =========================================================================
    # SLIDE 9: Step 4 (Theme 2) — Distributed HDFS File Lifecycle
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Theme 2 (Part A): Distributed HDFS File Lifecycle Operations", "THEME 2 · HDFS STORAGE MANAGEMENT")

    add_code_box(s9, Inches(0.8), Inches(1.4), Inches(6.0), Inches(2.2),
                 "HDFS Ingestion & Verification Commands",
                 "docker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"hdfs dfs -mkdir -p /user/root/ecommerce/live_eval_run/prepared\"\n\ndocker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"hdfs dfs -put -f /project/data/prepared/ecommerce/daily.tsv \\\n   /user/root/ecommerce/live_eval_run/prepared/\"\n\ndocker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"hdfs dfs -ls /user/root/ecommerce/live_eval_run/prepared\"")

    add_output_box(s9, Inches(0.8), Inches(3.7), Inches(6.0), Inches(1.6),
                   "HDFS Directory Listing (Replication Factor = 2)",
                   "Found 2 items\n-rw-r--r--   2 root supergroup    4285661 2026-11-19 07:07 .../daily.tsv\n-rw-r--r--   2 root supergroup       1117 2026-11-16 17:04 .../manifest.json")

    add_viva_callout(s9, Inches(0.8), Inches(5.4), Inches(6.0), Inches(1.6),
                     "Replication factor of 2 proves blocks are stored across both worker DataNodes. The 'Unable to write to output stream' message during head -3 is normal Unix pipe closure (SIGPIPE), confirming successful stream termination.")

    add_card(s9, Inches(7.1), Inches(1.4), Inches(5.4), Inches(5.6))
    hbox = s9.shapes.add_textbox(Inches(7.3), Inches(1.5), Inches(5.0), Inches(5.4))
    htf = hbox.text_frame
    htf.word_wrap = True
    
    hp = htf.paragraphs[0]
    hp.text = "HDFS Lifecycle Operations Demonstrated:"
    hp.font.bold = True
    hp.font.size = Pt(13)
    hp.font.color.rgb = COLOR_NAVY
    
    h_ops = [
        ("Directory Creation (-mkdir -p)", "Created dedicated namespaces for /raw, /prepared, and /mr_eval_out under HDFS root."),
        ("Distributed Ingestion (-put -f)", "Transferred 4,285,661 bytes of daily.tsv into HDFS with block replication across DataNodes."),
        ("Metadata Inspection (-ls -R)", "Verified POSIX file permissions (-rw-r--r--), supergroup ownership, byte sizes, and timestamps."),
        ("Stream Reading (-cat | head)", "Streamed distributed HDFS blocks to stdout to inspect transactional record headers."),
        ("Local Retrieval (-get)", "Downloaded HDFS blocks back to local container filesystem and performed byte-level cmp verification."),
        ("Safe Cleanup (-rm -r -f)", "Removed temporary evaluation directories ensuring clean, idempotent analytical re-runs.")
    ]
    for o, d in h_ops:
        p = htf.add_paragraph()
        p.text = f"• {o}: "
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_before = Pt(5)
        r = p.add_run()
        r.text = d
        r.font.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT_MUTED

    # =========================================================================
    # SLIDE 10: Step 4 (Theme 2) — MapReduce on YARN
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Theme 2 (Part B): Distributed Python Streaming MapReduce on YARN", "THEME 2 · DISTRIBUTED COMPUTATION")

    add_code_box(s10, Inches(0.8), Inches(1.4), Inches(6.0), Inches(1.9),
                 "Submit YARN MapReduce Streaming Job",
                 "docker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"hdfs dfs -rm -r -f /user/root/ecommerce/mr_eval_out\"\n\ndocker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"/project/scripts/run_mapreduce.sh \\\n   /user/root/ecommerce/live_eval_run/prepared/daily.tsv \\\n   /user/root/ecommerce/mr_eval_out 2\"")

    add_output_box(s10, Inches(0.8), Inches(3.4), Inches(6.0), Inches(1.9),
                   "YARN Job Counters & Map/Reduce Execution",
                   "INFO mapreduce.Job: Running job: job_1794418089843_0002\nMap input records=69065 | Map output records=69065\nReduce input groups=4254 | Reduce output records=4254\nBytes Written=316212 (part-00000: 155 KB, part-00001: 160 KB)\n_SUCCESS marker verified.")

    add_viva_callout(s10, Inches(0.8), Inches(5.4), Inches(6.0), Inches(1.6),
                     "mapper.py streams 69,065 daily rows and emits key (seller_id|year). YARN shuffles and sorts keys, and 2 reducers compute annual orders, GMV, daily averages, and peak order values (4,254 summaries).")

    img_mr = IMAGES_DIR / "screenshot_theme2_hdfs_mapreduce.png"
    if img_mr.is_file():
        s10.shapes.add_picture(str(img_mr), Inches(7.1), Inches(1.4), width=Inches(5.4))

    # =========================================================================
    # SLIDE 11: Step 5 (Theme 3) — Apache Pig Cleansing Pipeline
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Theme 3 (Part A): Apache Pig Latin Data Cleansing Pipeline", "THEME 3 · PIG LATIN ETL TRANSFORMATION")

    add_code_box(s11, Inches(0.8), Inches(1.4), Inches(6.0), Inches(1.9),
                 "Execute Pig Latin Cleaning Job on YARN",
                 "docker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"hdfs dfs -rm -r -f /user/root/ecommerce/pig_eval_out\"\n\ndocker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"pig -x mapreduce \\\n   -param INPUT=/user/root/ecommerce/live_eval_run/prepared/daily.tsv \\\n   -param OUTPUT=/user/root/ecommerce/pig_eval_out \\\n   /project/pig/clean_daily.pig\"")

    add_output_box(s11, Inches(0.8), Inches(3.4), Inches(6.0), Inches(1.9),
                   "Pig MapReduce Execution Stats",
                   "Successfully read 69065 records (4286058 bytes)\nSuccessfully stored 69065 records (4401177 bytes) in:\n\"/user/root/ecommerce/pig_eval_out\"\n\nPig script completed in 21 seconds\nJob DAG: job_1794418089843_0003")

    add_viva_callout(s11, Inches(0.8), Inches(5.4), Inches(6.0), Inches(1.6),
                     "Pig Latin (clean_daily.pig) validates date format via regex \\d{4}-\\d{2}-\\d{2}, checks non-empty merchant IDs, and filters out nulls or negative financial figures, generating clean warehouse input for Hive.")

    img_pig = IMAGES_DIR / "screenshot_theme3_pig_hive.png"
    if img_pig.is_file():
        s11.shapes.add_picture(str(img_pig), Inches(7.1), Inches(1.4), width=Inches(5.4))

    # =========================================================================
    # SLIDE 12: Step 5 (Theme 3) — Apache Hive Text vs RCFile Benchmark
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Theme 3 (Part B & C): Apache Hive RCFile Storage & Query Benchmark", "THEME 3 · HIVE ANALYTICAL BENCHMARKING")

    add_code_box(s12, Inches(0.8), Inches(1.4), Inches(6.0), Inches(2.0),
                 "1. Create External Tables & Populate Compressed RCFile",
                 "docker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"beeline -u jdbc:hive2://localhost:10000 -n root \\\n   --hivevar DATABASE=ecommerce_analytics \\\n   --hivevar INPUT=/user/root/ecommerce/pig_eval_out \\\n   --hivevar RC_OUTPUT=/user/root/ecommerce/rcfile \\\n   -f /project/hive/tables.hql\"")

    add_code_box(s12, Inches(0.8), Inches(3.5), Inches(6.0), Inches(1.9),
                 "2. Benchmark Identical SQL Query on Text vs RCFile",
                 "docker exec ecommerce-sales-analytics-master-1 bash -c \\\n  \"beeline -u jdbc:hive2://localhost:10000/ecommerce_analytics -n root \\\n   -e 'SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev \\\n       FROM daily_text GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5; \\\n       SELECT seller_id, count(*) AS days, round(sum(revenue_brl),2) AS total_rev \\\n       FROM daily_rcfile GROUP BY seller_id ORDER BY total_rev DESC LIMIT 5;'\"")

    img_hive = IMAGES_DIR / "theme3_hive_text_vs_rcfile.png"
    if img_hive.is_file():
        s12.shapes.add_picture(str(img_hive), Inches(7.1), Inches(1.4), width=Inches(5.4))

    add_viva_callout(s12, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5),
                     "Benchmark Result: RCFile with GzipCodec achieves a 78.71% storage reduction (915 KB vs 4.2 MB in HDFS) and 1.11x query speedup. Columnar layout reads only requested columns (seller_id, revenue_brl), skipping unneeded fields.")

    # =========================================================================
    # SLIDE 13: Step 6 (Track B Extension) — Interactive Analytics Dashboard
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Step 6: Track B Practical Extension — Interactive Flask Dashboard", "TRACK B EXTENSION · INTERACTIVE SERVING")

    add_code_box(s13, Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.8),
                 "Launch Dependency-Free Analytical Server",
                 "python -m ecommerce dashboard --results \"results/ecommerce\"   -->   Running on http://127.0.0.1:5000")

    img_d1 = IMAGES_DIR / "dashboard_page1_seller.png"
    if img_d1.is_file():
        s13.shapes.add_picture(str(img_d1), Inches(0.8), Inches(2.3), width=Inches(5.7))

    img_d2 = IMAGES_DIR / "dashboard_page2_leaderboard.png"
    if img_d2.is_file():
        s13.shapes.add_picture(str(img_d2), Inches(6.8), Inches(2.3), width=Inches(5.7))

    add_viva_callout(s13, Inches(0.8), Inches(6.0), Inches(11.7), Inches(1.1),
                     "Page 1 (Seller Deep-Dive): Inspects 2016-2018 multi-year trajectories, dynamic SVG pie metric shares, and revenue progression bars. Page 2 (Leaderboards): Filters by year (2016, 2017, 2018) and ranks merchants across core business KPIs.")

    # =========================================================================
    # SLIDE 14: Summary Master Benchmark Table & Viva Takeaways
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Summary Benchmark Matrix & Faculty Viva Takeaways", "EVALUATION SUMMARY & KEY FINDINGS")

    t_sum = s14.shapes.add_table(6, 4, Inches(0.8), Inches(1.4), Inches(11.7), Inches(3.6))
    tbl_s = t_sum.table
    tbl_s.columns[0].width = Inches(2.2)
    tbl_s.columns[1].width = Inches(2.3)
    tbl_s.columns[2].width = Inches(3.2)
    tbl_s.columns[3].width = Inches(4.0)

    s_headers = ["Component", "Technology", "Dataset Grain / Scope", "Benchmark / Key Result"]
    for i, h in enumerate(s_headers):
        c = tbl_s.cell(0, i)
        c.text = h
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_NAVY
        p = c.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = COLOR_WHITE

    s_data = [
        ("Theme 1: Operational DB", "MongoDB 7.0", "69,065 daily sales / 99,441 enriched orders", "229.73x scan reduction (IXSCAN 100 vs COLLSCAN 22,973 docs; 5.67x speedup)"),
        ("Theme 2: Batch Processing", "Hadoop 2.10.2 / YARN", "69,065 rows -> 4,254 summaries", "Distributed MapReduce across 2 DataNodes; exact parity with Python reference"),
        ("Theme 3: Data Cleansing", "Apache Pig 0.17.0", "69,065 records read & verified", "Regex date filtering (\\d{4}-\\d{2}-\\d{2}) and null removal in 21s on YARN"),
        ("Theme 3: Data Warehousing", "Apache Hive 2.3.9", "Text (4.2 MB) vs RCFile (915 KB)", "78.71% storage reduction & 1.11x query speedup via columnar GzipCodec"),
        ("Track B Extension", "Python Flask & SVG", "Multi-year seller analytics (2016–2018)", "Sub-millisecond interactive dashboard serving pre-aggregated analytical artifacts")
    ]
    for r_idx, r_vals in enumerate(s_data, start=1):
        for c_idx, val in enumerate(r_vals):
            c = tbl_s.cell(r_idx, c_idx)
            c.text = val
            p = c.text_frame.paragraphs[0]
            p.font.size = Pt(9.5)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = COLOR_NAVY
            elif c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = COLOR_EMERALD

    add_viva_callout(s14, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.8),
                     "Final Architectural Conclusion: Document databases (MongoDB) excel at low-latency OLTP lookups and flexible nested schemas ($unwind/$facet). Distributed file systems and columnar warehouses (HDFS + Hive RCFile) excel at massive batch aggregations, delivering 78.7% compression and scalable map-reduce parallelization.")

    # Save presentation
    prs.save(str(OUTPUT_PPTX))
    print(f"Presentation saved successfully to: {OUTPUT_PPTX}")


if __name__ == "__main__":
    create_deck()
