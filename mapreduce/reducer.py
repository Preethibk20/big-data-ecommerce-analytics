#!/usr/bin/env python3
"""Reduce sorted seller/year records into annual revenue and order summaries."""
import itertools
import math
import sys


def reduce_rows(source, destination):
    records = (line.rstrip("\r\n").split("\t") for line in source if line.strip())
    for key, group in itertools.groupby(records, key=lambda record: record[0]):
        days_count = 0
        total_orders = 0
        revenues = []
        max_daily_revenue = 0.0
        peak_order_brl = 0.0
        for record in group:
            if len(record) != 4:
                raise ValueError("Expected key, daily_revenue, daily_orders, daily_peak")
            revenue = float(record[1])
            orders = int(record[2])
            peak = float(record[3])
            if any(not math.isfinite(val) or val < 0 for val in (revenue, peak)) or orders < 1:
                raise ValueError("Invalid partial aggregate in reducer")
            days_count += 1
            total_orders += orders
            revenues.append(revenue)
            if revenue > max_daily_revenue:
                max_daily_revenue = revenue
            if peak > peak_order_brl:
                peak_order_brl = peak

        total_revenue = math.fsum(revenues)
        mean_daily_revenue = total_revenue / days_count if days_count else 0.0
        seller_id, year = key.rsplit("|", 1)
        print(
            f"{seller_id}\t{year}\t{days_count}\t{total_revenue!r}\t{mean_daily_revenue!r}\t{max_daily_revenue!r}\t{total_orders}\t{peak_order_brl!r}",
            file=destination
        )


if __name__ == "__main__":
    reduce_rows(sys.stdin, sys.stdout)
