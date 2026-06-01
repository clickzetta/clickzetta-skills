---
name: clickzetta-sql-pipeline-manager
description: >
  Manage ClickZetta Lakehouse SQL pipeline objects: Dynamic Table, Materialized View,
  Table Stream, and Pipe. Covers full lifecycle: create, modify, suspend/resume, drop,
  and status inspection. SQL commands only — no Studio GUI involved.

  Trigger when the user says: "create dynamic table", "create materialized view",
  "create pipe", "create table stream", "suspend/resume dynamic table",
  "view refresh history", "change refresh interval", "ingest from Kafka",
  "continuous ingest from object storage", "CDC change capture", "incremental compute",
  "real-time ETL", "data pipeline", "pipeline", "streaming", "dynamic table refresh failed",
  "design ETL", "build data pipeline", "data ingestion plan",
  "Medallion Architecture", "Bronze Silver Gold", "lakehouse layering",
  "Bronze layer", "Silver layer", "Gold layer".
  Keywords: SQL pipeline, dynamic table, materialized view, table stream, Pipe, data pipeline
---

# ClickZetta SQL Pipeline Manager

See [references/scenarios.md](references/scenarios.md) for worked pipeline examples (Kafka, CDC, MV, operations, parameterized DT).
See [references/troubleshooting.md](references/troubleshooting.md) for common errors and delivery checklist.
See [references/dynamic-table.md](references/dynamic-table.md), [references/pipe.md](references/pipe.md), [references/table-stream.md](references/table-stream.md), [references/materialized-view.md](references/materialized-view.md) for object-specific syntax.

---

## ⚠️ Key Syntax Differences: ClickZetta vs Standard SQL / Snowflake

| Feature | ❌ Wrong (Snowflake/Standard SQL) | ✅ ClickZetta Correct |
|---|---|---|
| Dynamic table compute cluster | `WAREHOUSE = compute_wh` | `vcluster default` (name directly, no equals sign) |
| Dynamic table refresh schedule | `TARGET_LAG = '1 minutes'` | `REFRESH INTERVAL 1 MINUTE vcluster default` |
| Kafka read function | `TABLE(READ_KAFKA(KAFKA_BROKER => ...))` | `read_kafka('broker', 'topic', '', 'group', '', '', '', '', 'raw', 'raw', 0, MAP(...))` — positional args |
| Materialized view scheduled refresh | `REFRESH EVERY 1 HOUR` | `REFRESH INTERVAL 60 MINUTE vcluster default` |
| Materialized view manual refresh | Inside CREATE | Execute separately: `REFRESH MATERIALIZED VIEW <name>;` |
| Modify dynamic table SQL | `ALTER DYNAMIC TABLE ... AS ...` | `CREATE OR REPLACE DYNAMIC TABLE ...` |
| JSON field access | `$1:field::TYPE` | `parse_json(value::string)['field']::TYPE` |
| COPY INTO import format | `FILE_FORMAT = (TYPE = CSV)` | `USING CSV OPTIONS(...)` |

---

## Wizard: Clarify Intent

On receiving a request, determine the user's intent:

> **A. Design and create a new pipeline** (complete SQL from source to layered DTs) → Pipeline Wizard below
> **B. Manage existing objects** (modify refresh interval, suspend/resume, view history) → Execute directly
> **C. Troubleshoot** (DT refresh failure, Pipe stopped, Stream backlog) → Read [references/troubleshooting.md](references/troubleshooting.md)

If the user has already stated clearly what they want, execute directly without asking.

---

## Pipeline Wizard

Triggered by: "design/build ETL", "complete data pipeline", "ingest from Kafka/OSS", "ODS→DWD→DWS", "Medallion Architecture", "Bronze/Silver/Gold".

### Layer naming

Preserve the user's chosen naming — do not remap Bronze→ODS, Silver→DWD, etc.:

| User says | Schema naming |
|---|---|
| Bronze / Silver / Gold | `{prefix}_bronze` / `{prefix}_silver` / `{prefix}_gold` |
| ODS / DWD / DWS | `{prefix}_ods` / `{prefix}_dwd` / `{prefix}_dws` |
| Raw / Cleansed / Aggregated | `{prefix}_raw` / `{prefix}_cleansed` / `{prefix}_agg` |

Always add a project/domain prefix to schema names to avoid conflicts. If the user hasn't provided one, ask.

### Requirements collection

If the user has already provided enough information, generate the complete SQL directly. Otherwise ask two questions: (1) data source type (Kafka / OSS/S3/COS / existing table INSERT-only / existing table with UPDATE/DELETE); (2) refresh frequency (seconds / minutes / hours/days).

### Generate complete SQL

Produce end-to-end SQL covering all parts:
1. Schema creation (using user's layer names)
2. Ingestion layer table (if external source)
3. Data entry point (Pipe or Table Stream, based on source)
4. Intermediate layer Dynamic Table (cleanse/filter)
5. Service layer Dynamic Table (aggregate/dimension)
6. `REFRESH DYNAMIC TABLE` immediately after each DT creation
7. Verification commands

**Source → entry object:**
- Kafka → `CREATE PIPE ... AS COPY INTO ... FROM (SELECT ... FROM read_kafka(...))`
- OSS/S3/COS → `CREATE PIPE ... INGEST_MODE = 'LIST_PURGE' AS COPY INTO ... FROM VOLUME ... PURGE=true`
- Existing table + UPDATE/DELETE → `CREATE TABLE STREAM ... WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD')`
- Existing table + INSERT only → Dynamic Table reads source directly

**After generating SQL, save each segment as a Studio task** (code asset management):

```bash
# DDL → DRAFT task (no Cron, no dependencies — DDL must never be scheduled)
cz-cli task save-content <ddl_task_name> --content "<ddl_sql>"

# ETL/transform → scheduled task
cz-cli task save-content <etl_task_name> --content "<etl_sql>"
cz-cli task save-cron <etl_task_name> --cron '0 30 2 * * ? *'
cz-cli task deploy <etl_task_name>
```

**Scheduling rules (hard constraints):**

| Task type | Scheduling config | Studio state |
|---|---|---|
| DDL (CREATE/DROP/ALTER TABLE) | No Cron, no dependencies | DRAFT |
| ETL transform / data sync | Cron + upstream dependencies | PUBLISHED |
| Dynamic Table (DWS/ADS) | No Studio task — system auto-refreshes | — |

---

## Object Type Reference

| Object | Use case | Key characteristics |
|---|---|---|
| **Dynamic Table** | Real-time / near-real-time incremental ETL | SQL-defined, auto incremental refresh |
| **Materialized View** | Fixed aggregation to accelerate queries | Pre-computed, manual or scheduled full refresh |
| **Table Stream** | CDC change data capture | Captures INSERT/UPDATE/DELETE |
| **Pipe** | Continuous data ingestion | Auto-ingests from Kafka or object storage |

## Decision Tree

```
User requirement
├── Continuously ingest from external source (Kafka / OSS / S3)
│   └── → Pipe
├── Real-time / incremental transform on existing table
│   ├── Need to detect UPDATE/DELETE → Table Stream + Dynamic Table
│   └── INSERT append only → Dynamic Table (reads source directly)
├── Fixed aggregation, real-time not required
│   └── → Materialized View
└── Multi-layer ETL (ODS→DWD→DWS or Bronze→Silver→Gold)
    └── → Cascaded Dynamic Tables (each layer sets its own REFRESH INTERVAL)
```

## Routing

| Scenario | Route to |
|---|---|
| Want to use dbt for modeling instead of raw SQL | `clickzetta-dbt-project-setup` |
| Need full DW modeling design (layering, DDL, pipeline together) | `clickzetta-dw-modeling` |
| Need to sync data from MySQL/PostgreSQL | `clickzetta-cdc-sync-pipeline` |
| Need to ingest files from OSS/S3/COS | `clickzetta-oss-ingest-pipeline` |
| Need to ingest from Kafka | `clickzetta-kafka-ingest-pipeline` |
| Not sure which ingestion method to use | `clickzetta-data-ingest-pipeline` |
