#!/usr/bin/env python3
"""Map daily seller revenue records into annual seller groups. Input: daily.tsv."""
import math
import sys


def map_rows(source, destination):
    for number, line in enumerate(source, 1):
        line = line.rstrip("\r\n")
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != 6:
            raise ValueError(f"Expected six fields at line {number}, got {len(fields)}")
        day, seller_id, orders_str, revenue_str, mean_str, peak_str = fields
        if len(day) < 10 or day[4] != "-" or day[7] != "-":
            raise ValueError(f"Invalid date format at line {number}: {day!r}")
        try:
            orders = int(orders_str)
            revenue = float(revenue_str)
            peak = float(peak_str)
        except ValueError as err:
            raise ValueError(f"Numeric parse error at line {number}: {err}") from err
        if orders < 1 or not math.isfinite(revenue) or not math.isfinite(peak) or revenue < 0 or peak < 0:
            raise ValueError(f"Invalid reading at line {number}")
        year = day[:4]
        print(f"{seller_id}|{year}\t{revenue!r}\t{orders}\t{peak!r}", file=destination)


if __name__ == "__main__":
    map_rows(sys.stdin, sys.stdout)
