# Data Lake Acceleration

"Data Lake Acceleration" is like attaching a Serverless query engine to data on object storage — data stays in place, and Lakehouse mounts, queries, and processes it directly, eliminating migration time and storage redundancy. Compared to traditional solutions (Spark/Hive ETL + Presto/Trino queries), you only need to focus on SQL logic, without managing cluster operations, scheduling configurations, or incremental detection.

---

## Three Acceleration Paths

Data Lake Acceleration is not a single feature but a combination of multiple capabilities. Based on your current data situation and goals, choose the corresponding path:

| Path | Where is the data | How to use | Best for |
|------|---------|--------|---------|
| **In-place queries** | Hive Metastore + object storage | External Schema direct connection, query directly | Existing Hive data warehouse, no migration desired |
| **Auto-ingestion** | Object storage files (CSV/Parquet/JSON) | Volume mount → Pipe auto-import → DT incremental aggregation | Periodic file uploads needing automated pipelines |
| **SQL modeling** | Already in Lakehouse tables | Dynamic Table declarative multi-layer pipeline | Data already loaded, needs cleaning/modeling/aggregation |
| **AI in SQL** | Code already in object storage | External Function = Storage Connection + API Connection | Calling AI/ML/external APIs in SQL |

The three paths complement each other and can be combined: use External Schema to query existing Hive tables → use Pipe to ingest incremental files → use Dynamic Table to build Silver/Gold layers → use External Function for AI analysis in SQL.

If your data is spread across Alibaba Cloud OSS, Tencent Cloud COS, and AWS S3, start with [Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md) — the SQL syntax across all three clouds is 90% identical, with only Storage Connection parameter names differing.

---

## Core Capabilities Overview

| Capability | What it is | What problem it solves |
|------|--------|-------------|
| **External Schema** | Direct connection to external Hive Metastore, zero-migration queries | Existing Hive data warehouse should not be touched, but query cost needs to be reduced |
| **Volume** | Mount OSS/COS/S3 paths as Lakehouse directories | Files stay in object storage, Lakehouse reads and writes directly |
| **Pipe** | Continuously scans Volume for new files, automatic COPY INTO | No scheduled tasks needed — files are automatically loaded when they arrive |
| **Dynamic Table** | Declarative incremental refresh of materialized tables | No scheduling DAGs needed — system automatically detects increments and refreshes along dependency chains |
| **External Function** | Register Python/Java code in OSS as SQL functions | Call AI, ML, and external APIs in SQL without writing application-layer code |

---

## Choose Your Reading Path

### My data is on multiple clouds and I want unified management

→ [Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md)

Real-world comparison of Alibaba Cloud OSS + Tencent Cloud COS + AWS S3. Beyond Storage Connection parameter names, the SQL syntax for Volume, Pipe, and Dynamic Table is completely identical. Includes code reuse strategies, private network acceleration, and security best practices.

### I want to query existing Hive data warehouses without moving data

→ [In-Place Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md)

External Schema connects directly to Hive Metastore, and Lakehouse queries Hive tables directly. Suitable for scenarios with large amounts of historical data in Hive where migration costs should be avoided.

### I want object storage files to be automatically loaded into the warehouse

→ [Volume + Pipe + Dynamic Table End-to-End Practice](lakehouse-volume-pipe-acceleration-guide.md)

Complete pipeline: create Storage Connection → mount Volume → create Pipe for automatic import → Dynamic Table incremental aggregation. When OSS/COS/S3 files arrive, the full pipeline flows automatically.

### I want to build a multi-layer data pipeline using pure SQL

→ [Medallion Architecture Practice: Pure SQL Dynamic Table Approach](lakehouse-medallion-sql-dt-guide.md)

Build a Bronze → Silver → Gold three-layer pipeline declaratively using Dynamic Table. Full example with a real NHL dataset (10 tables, ~14 million rows), including 5 Gold metric tables: top scorers, team records, goalie rankings, and more.

### I want to call AI or external APIs in SQL

→ [Storage Connection + API Connection + External Function Combined Practice](external-function-combo-practice.md)

Build an External Function environment from scratch, covering Python Quickstart, ML dependency packaging, 30 AI functions, and Java UDF/UDAF/UDTF — four scenarios. Supports Alibaba Cloud, Tencent Cloud, and AWS.

---

## Recommended Reading Order

For beginners, it is recommended to progress gradually in the following order:

1. **[Volume + Pipe + Dynamic Table End-to-End Practice](lakehouse-volume-pipe-acceleration-guide.md)** — Understand the core pipeline for automatic data loading; run through your first end-to-end example
2. **[Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md)** — Master the differences across three clouds (only Connection parameters differ); establish a code reuse strategy
3. **[Medallion Architecture Practice: Pure SQL Dynamic Table Approach](lakehouse-medallion-sql-dt-guide.md)** — Master multi-table, multi-layer DT modeling; understand inter-layer references and incremental refresh
4. **[Storage Connection + API Connection + External Function Combined Practice](external-function-combo-practice.md)** — Extend SQL boundaries; call AI/ML within SQL
5. **[In-Place Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md)** — For scenarios with existing Hive data warehouses; zero-migration queries with External Schema
