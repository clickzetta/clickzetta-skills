#!/usr/bin/env python3
"""Generate small physical tables for apache/ossie examples/tpcds_semantic_model.yaml, and expected results.

Writes, into --out:
  tables.sql    CREATE TABLE + INSERT statements for ClickZetta (schema given by --schema)
  queries.json  [{name, view, sv_args, expected}] - expected rows are computed with sqlite from the
                same data, never read from ClickZetta.

Expected values follow ClickZetta's metric semantics: every table-qualified metric aggregates at its
own table's grain, and a view-scoped metric combines those results. The Ossie model's
customer_lifetime_value = SUM(store_sales.ss_ext_sales_price) / COUNT(DISTINCT customer.c_customer_sk)
therefore divides by ALL customers in the customer table (customer 5 never buys), not only buyers.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3

TABLES = {
    "date_dim": [("d_date_sk", "INT"), ("d_date", "DATE"), ("d_year", "INT"), ("d_quarter_name", "STRING"),
                 ("d_moy", "INT")],
    "customer": [("c_customer_sk", "INT"), ("c_customer_id", "STRING"), ("c_first_name", "STRING"),
                 ("c_last_name", "STRING"), ("c_email_address", "STRING")],
    "item": [("i_item_sk", "INT"), ("i_item_id", "STRING"), ("i_item_desc", "STRING"), ("i_brand", "STRING"),
             ("i_category", "STRING"), ("i_current_price", "DECIMAL(10,2)")],
    "store": [("s_store_sk", "INT"), ("s_store_id", "STRING"), ("s_store_name", "STRING"), ("s_city", "STRING"),
              ("s_state", "STRING"), ("s_number_employees", "INT")],
    "store_sales": [("ss_sold_date_sk", "INT"), ("ss_item_sk", "INT"), ("ss_customer_sk", "INT"),
                    ("ss_store_sk", "INT"), ("ss_ticket_number", "INT"), ("ss_quantity", "INT"),
                    ("ss_sales_price", "DECIMAL(10,2)"), ("ss_ext_sales_price", "DECIMAL(10,2)"),
                    ("ss_net_profit", "DECIMAL(10,2)")],
}


def data() -> dict[str, list[tuple]]:
    dates = [(1, "2025-11-03", 2025, "2025Q4", 11), (2, "2025-11-20", 2025, "2025Q4", 11),
             (3, "2025-12-05", 2025, "2025Q4", 12), (4, "2026-01-09", 2026, "2026Q1", 1),
             (5, "2026-01-28", 2026, "2026Q1", 1), (6, "2026-02-14", 2026, "2026Q1", 2)]
    customers = [(1, "C001", "Ada", "Lovelace", "ada@example.com"), (2, "C002", "Alan", "Turing", "alan@example.com"),
                 (3, "C003", "Grace", "Hopper", "grace@example.com"), (4, "C004", "Edsger", "Dijkstra", "ed@example.com"),
                 (5, "C005", "Barbara", "Liskov", "barbara@example.com")]          # never buys
    items = [(1, "I001", "Trail shoe", "Northpeak", "Shoes", 89.00), (2, "I002", "Rain jacket", "Northpeak", "Apparel", 129.00),
             (3, "I003", "City shoe", "Urbanite", "Shoes", 75.00), (4, "I004", "Backpack", "Urbanite", "Bags", 59.00)]
    stores = [(1, "S001", "Downtown", "Seattle", "WA", 12), (2, "S002", "Harbor", "Tacoma", "WA", 8),
              (3, "S003", "Riverside", "Portland", "OR", 10)]
    sales = []
    ticket = 1000
    for i in range(20):
        d = dates[i % 6][0]
        item = items[(i * 3) % 4]
        cust = customers[i % 4][0]
        store = stores[(i * 2) % 3][0]
        qty = 1 + i % 3
        price = round(item[5] * (0.9 if i % 4 == 0 else 1.0), 2)
        ext = round(price * qty, 2)
        profit = round(ext * 0.25 - (5 if i % 5 == 0 else 0), 2)
        ticket += 1 + i % 2
        sales.append((d, item[0], cust, store, ticket, qty, price, ext, profit))
    return {"date_dim": dates, "customer": customers, "item": items, "store": stores, "store_sales": sales}


def lit(v, ty: str) -> str:
    if v is None:
        return "NULL"
    if ty == "DATE":
        return f"DATE '{v}'"
    if ty.startswith(("INT", "DECIMAL")):
        return str(v)
    return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"


SS = "FROM store_sales ss"
QUERIES = [  # name, semantic_view args, sqlite SQL computing the same thing
    ("sales_by_year", "DIMENSIONS date_dim.d_year METRICS store_sales.total_sales, store_sales.total_profit",
     f"SELECT d.d_year, SUM(ss.ss_ext_sales_price), SUM(ss.ss_net_profit) {SS} JOIN date_dim d ON ss.ss_sold_date_sk=d.d_date_sk GROUP BY d.d_year"),
    ("sales_by_brand", "DIMENSIONS item.i_brand METRICS store_sales.sales_by_brand",
     f"SELECT i.i_brand, SUM(ss.ss_ext_sales_price) {SS} JOIN item i ON ss.ss_item_sk=i.i_item_sk GROUP BY i.i_brand"),
    ("customer_full_name", "DIMENSIONS customer.customer_full_name METRICS store_sales.total_sales",
     f"SELECT c.c_first_name || ' ' || c.c_last_name, SUM(ss.ss_ext_sales_price) {SS} JOIN customer c ON ss.ss_customer_sk=c.c_customer_sk GROUP BY 1"),
    # view-scoped: each part at its own grain, then divided (store employees are not fanned out by sales rows)
    ("store_productivity_by_state", "DIMENSIONS store.s_state METRICS store_productivity",
     "SELECT s.s_state, (SELECT SUM(ss.ss_ext_sales_price) FROM store_sales ss JOIN store s2 ON ss.ss_store_sk=s2.s_store_sk "
     "WHERE s2.s_state=s.s_state) * 1.0 / SUM(s.s_number_employees) FROM store s GROUP BY s.s_state"),
    ("customer_lifetime_value", "METRICS customer_lifetime_value",
     "SELECT (SELECT SUM(ss_ext_sales_price) FROM store_sales) * 1.0 / (SELECT COUNT(DISTINCT c_customer_sk) FROM customer)"),
    ("cumulative_sales", "DIMENSIONS date_dim.d_date METRICS store_sales.cumulative_sales",
     f"SELECT d.d_date, SUM(SUM(ss.ss_ext_sales_price)) OVER (ORDER BY d.d_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) "
     f"{SS} JOIN date_dim d ON ss.ss_sold_date_sk=d.d_date_sk GROUP BY d.d_date"),
    ("monthly_sales_change", "DIMENSIONS date_dim.d_year, date_dim.d_moy METRICS store_sales.monthly_sales_change",
     f"SELECT d.d_year, d.d_moy, SUM(ss.ss_ext_sales_price) - LAG(SUM(ss.ss_ext_sales_price), 1) OVER (ORDER BY d.d_year, d.d_moy) "
     f"{SS} JOIN date_dim d ON ss.ss_sold_date_sk=d.d_date_sk GROUP BY d.d_year, d.d_moy"),
    # brand_rank_in_store (RANK() OVER (... ORDER BY SUM(...))) is not representable: ClickZetta window
    # metrics may only PARTITION/ORDER BY declared dimensions. The importer leaves it out (sidecar keeps it).
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", default="ossie_skill_test")
    ap.add_argument("--view", default="tpcds_sv")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = data()
    db = sqlite3.connect(":memory:")
    lines = [f"-- Physical tables for apache/ossie examples/tpcds_semantic_model.yaml (schema {a.schema})"]
    for t, cols in TABLES.items():
        lines.append(f"CREATE TABLE {a.schema}.{t} ({', '.join(f'{c} {ty}' for c, ty in cols)});")
        lines.append(f"INSERT INTO {a.schema}.{t} VALUES\n  " + ",\n  ".join(
            "(" + ", ".join(lit(v, ty) for v, (_, ty) in zip(r, cols)) + ")" for r in d[t]) + ";")
        db.execute(f"CREATE TABLE {t} ({', '.join(c for c, _ in cols)})")
        db.executemany(f"INSERT INTO {t} VALUES ({', '.join('?' * len(cols))})", d[t])
    with open(os.path.join(a.out, "tables.sql"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    out = [{"name": n, "view": a.view, "sv_args": args, "expected": [list(r) for r in db.execute(q).fetchall()]}
           for n, args, q in QUERIES]
    with open(os.path.join(a.out, "queries.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote tables.sql ({sum(len(v) for v in d.values())} rows) and queries.json ({len(out)} queries)")


if __name__ == "__main__":
    main()
