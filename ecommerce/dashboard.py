"""Read-only Flask dashboard for saved Brazilian E-Commerce analytics."""

import json
from pathlib import Path

from flask import Flask, abort, render_template, request

from .analytics import METRICS, seller_year_view, year_seller_ranking


def create_app(results_dir):
    app = Flask(__name__)
    results_dir = Path(results_dir).resolve()

    @app.get("/")
    def home():
        path = results_dir / "analytics.json"
        if not path.is_file():
            abort(404, description=f"No analytics found at {path}")
        with path.open(encoding="utf-8") as source:
            data = json.load(source)

        page = request.args.get("page", "seller")
        if page not in {"seller", "year"}:
            abort(400, description="Choose the seller or year view")

        years = sorted(data["years"])
        default_top_k = min(10, data["sellers"])
        top_seller_ids = data.get("top_seller_ids", [])[:8]

        if page == "seller":
            seller_query = request.args.get("seller_id", "").strip()
            if len(seller_query) > 64:
                abort(400, description="Seller query is too long")
            pie_metric = request.args.get("pie_metric", "revenue_brl")
            if pie_metric not in METRICS:
                abort(400, description="Choose a supported pie-chart metric")

            # Default to first top seller if no query provided
            if not seller_query and top_seller_ids:
                seller_query = top_seller_ids[0]

            seller = seller_year_view(data, seller_query, pie_metric) if seller_query else None
            return render_template(
                "dashboard.html",
                data=data,
                page=page,
                years=years,
                selected_year=years[0] if years else None,
                seller=seller,
                seller_id=seller_query,
                top_seller_ids=top_seller_ids,
                ranking=None,
                metrics=METRICS,
                pie_metric=pie_metric,
                rank_metric="revenue_brl",
                top_k=default_top_k,
            )

        raw_year = request.args.get("year", str(years[-1] if years else ""))
        try:
            selected_year = int(raw_year)
        except ValueError:
            abort(400, description="Select a valid year")
        if selected_year not in years:
            abort(400, description="The selected year is not in this dataset")

        rank_metric = request.args.get("metric", "revenue_brl")
        if rank_metric not in METRICS:
            abort(400, description="Choose a supported ranking metric")

        raw_top_k = request.args.get("top_k", str(default_top_k))
        try:
            top_k = int(raw_top_k)
        except ValueError:
            abort(400, description="Top K must be a whole number")
        if not 1 <= top_k <= data["sellers"]:
            abort(400, description=f"Top K must be between 1 and {data['sellers']}")

        ranking = year_seller_ranking(data, selected_year, rank_metric, top_k)
        return render_template(
            "dashboard.html",
            data=data,
            page=page,
            years=years,
            selected_year=selected_year,
            seller=None,
            seller_id="",
            top_seller_ids=top_seller_ids,
            ranking=ranking,
            metrics=METRICS,
            pie_metric="revenue_brl",
            rank_metric=rank_metric,
            top_k=top_k,
        )

    return app
