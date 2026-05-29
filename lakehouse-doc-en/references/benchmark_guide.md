# Performance Benchmarks

This page collects benchmark reports comparing Singdata Lakehouse against similar data processing systems, covering three industry-standard test suites: SSB, TPC-H, and TPC-DS. Comparison targets include columnar databases (ClickHouse), distributed query engines (Trino), and big data compute engines (Spark SQL). The goal is to provide objective query performance reference data at the same data scale and comparable compute resources.

---

## Benchmark Summary

| Standard | Comparison target | Data scale | Query count | Result |
|---------|---------|---------|---------|------|
| SSB | ClickHouse 23.3 | 100 GB | 13 queries | ClickHouse total time is **1.48×** that of Singdata Lakehouse |
| TPC-H | Trino 422 | 100 GB | 22 queries | Trino total time is **9.84×** that of Singdata Lakehouse |
| TPC-DS | Spark SQL 3.4.2 | 10 TB | 103 queries | Spark total time is **9.51×** that of Singdata Lakehouse |

---

## SSB Benchmark

Star Schema Benchmark (SSB) is based on TPC-H's star schema dataset, which ClickHouse officially flattens into a single wide table to test large-scale single-table scan and aggregation performance. This test runs 13 queries at 100 GB data scale. Singdata Lakehouse uses a Large compute cluster (64 vCPU equivalent), with the same LZ4 compression as ClickHouse.

ClickHouse is slightly faster on the Q1 series (high-selectivity filters); Singdata Lakehouse has a clear advantage on the Q2–Q4 series (multi-dimensional aggregation). Singdata Lakehouse has lower total time across all 13 queries.

[View SSB Detailed Report](ssb-benchmark.md)

---

## TPC-H Benchmark

TPC-H is a decision support benchmark published by the Transaction Processing Performance Council (TPC), containing 8 tables and 22 ad-hoc queries covering subqueries, multi-table JOINs, aggregations, and other typical analytics scenarios. This test compares against Trino at 100 GB data scale. Singdata Lakehouse uses an XLarge compute cluster (128 vCPU equivalent); both sides use the same Parquet + LZ4 storage format and bucketing/sorting settings.

Singdata Lakehouse outperforms Trino on all 22 queries; some queries (Q6, Q14, Q17) show performance gaps exceeding 25×.

[View TPC-H Detailed Report](tpch-benchmark.md)

---

## TPC-DS Benchmark

TPC-DS is a benchmark closer to real-world data warehouse scenarios than TPC-H, containing 24 tables and covering complex scenarios including analytical reports, interactive queries, and data mining. This test compares against Spark SQL at 10 TB data scale. Singdata Lakehouse uses an XLarge compute cluster (128 vCPU equivalent), running 103 complex queries measured on first execution (no warm-up).

Singdata Lakehouse shows particularly significant improvements on long-running jobs; some queries (query16, query82) show performance gaps exceeding 45×.

[View TPC-DS Detailed Report](tpcds-benchmark.md)
