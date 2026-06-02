---
name: clickzetta-dw-modeling
description: |
  ClickZetta Lakehouse data warehouse modeling wizard. Autonomously explores data landscape,
  then presents justified recommendations — never asks questionnaire-style questions.
  Covers three layering patterns: Traditional DW (ODS/DWD/DWS/ADS), Medallion (Bronze/Silver/Gold),
  and hybrid. Pipeline and modeling designed together — DDL and pipeline config output simultaneously.
  Core principle: use Dynamic Table for aggregation layers, not Materialized View.
  Trigger when the user says: "data warehouse modeling", "layering design", "ODS/DWD/DWS",
  "Medallion", "Bronze/Silver/Gold", "fact table", "dimension table", "star schema",
  "layered architecture", "modeling wizard", "build a data warehouse", "DW architecture",
  "design my data layers".
  Keywords: data warehouse, modeling, star schema, medallion, ODS, DWD, DWS, ADS, layering
---

# ClickZetta Data Warehouse Modeling Wizard

See [references/modeling-patterns.md](references/modeling-patterns.md) for layer definitions, naming conventions, DDL templates, scheduling DAGs, and common pitfalls for all three layering patterns.

---

## Working Mode: Explore First, Then Recommend

**Do not ask questionnaire-style questions. Look at the data first, then present justified choices.**

The user should answer at most 2 questions:
1. Choose from the presented options (A/B/C)
2. Provide information that cannot be inferred (business purpose, query patterns)

---

## Phase 1: Autonomous Data Exploration

On receiving a modeling request, immediately run the following — **do not ask the user anything first**:

```sql
-- Step 1: List all schemas
SHOW SCHEMAS;

-- Step 2: List tables in schemas that look like business data
SHOW TABLES IN <schema>;

-- Step 3: Check table sizes and row counts
SELECT table_schema, table_name, table_type,
       ROUND(bytes/1024.0/1024/1024, 2) AS size_gb,
       row_count, last_modify_time
FROM information_schema.tables
WHERE table_type = 'MANAGED_TABLE'
ORDER BY bytes DESC NULLS LAST LIMIT 20;

-- Step 4: Sample the 2-3 largest tables
SELECT * FROM <schema>.<table> LIMIT 5;
```

**Inference logic:**

| Observed characteristic | Inference |
|---|---|
| Table name contains order/user/product/trade | Business DB raw data → ODS/Bronze |
| Table name contains log/event/track/click | Tracking/log data, high volume, needs partitioning |
| Table name contains dw/ods/dwd/dws/ads | Already layered — evaluate existing structure |
| Table name contains tmp/temp/bak | Temporary — exclude from modeling scope |
| Fields contain _op/_ts/binlog | CDC-synced data |
| Single table > 10GB | Needs partitioning + bucketing |

---

## Phase 2: Present Justified Recommendations

Based on exploration results, present three sections:

### 1. Data landscape summary (self-summarize, do not ask)

```
Here's what I found:
- `raw` schema: orders (2.3GB / 12M rows), users (450MB)
  → Fields look like MySQL business DB sync; orders has _op/_ts (CDC ingestion)
- `events` schema: user_events (18GB / 800M rows)
  → Fields include event_time, event_type — tracking/log data
- No existing layered structure found
```

### 2. Option choices (A/B or A/B/C, no more than 3)

```
Based on the above, two directions:

A. Traditional DW (ODS → DWD → DWS → ADS)
   Reuse existing data as ODS. New: DWD (cleanse) + DWS (aggregate, Dynamic Table) + ADS (output)
   Best for: BI reporting as primary use case, well-defined metric system

B. Medallion (Bronze → Silver → Gold)
   Reuse existing data as Bronze. New: Silver (standardize) + Gold (metrics, Dynamic Table)
   Best for: multi-scenario reuse — both BI and data science
```

### 3. Ask only one question

```
What do you primarily use this data for?
- BI reporting (fixed reports, well-defined metrics) → recommend A
- Multi-scenario (reporting + analytics + data science) → recommend B
- Real-time dashboards (minute-level latency) → let me know, the plan will adjust
```

### 4. Flag cost considerations when confirming

- **Dynamic Table refresh frequency**: match business freshness needs, not maximum frequency. T+1 → `1 DAY`, hourly → `1 HOUR`, minute-level → `10~30 MINUTE`
- **Number of layers**: each additional DT layer adds refresh cost — evaluate whether all layers are necessary
- **VCluster size**: start small, scale up based on actual consumption

---

## Phase 3: Complete Output After Confirmation

After the user selects a direction, deliver the complete plan in one pass. Read [references/modeling-patterns.md](references/modeling-patterns.md) for DDL templates and scheduling DAG patterns.

### Layer structure

**Traditional DW:**

| Layer | Type | Notes |
|---|---|---|
| ODS | Regular table | Raw, no transformation |
| DWD | Regular table | Cleanse and standardize |
| DWS | **Dynamic Table** | Incremental aggregation, auto-refresh |
| ADS | **Dynamic Table** | Application-facing |

**Medallion:**

| Layer | Type | Notes |
|---|---|---|
| Bronze | Regular table | Zero transformation, preserve raw |
| Silver | Regular table or Dynamic Table | Cleanse and standardize |
| Gold | **Dynamic Table** | Aggregated metrics, auto-refresh |

> Use Dynamic Table for aggregation layers — not Materialized View. Dynamic Table uses CBO incremental compute, only refreshes changed partitions, and supports Time Travel.

### Data ingestion pipeline

Based on data source characteristics found during exploration:

| Data source characteristic | Recommended pipeline | Skill |
|---|---|---|
| Has _op/_ts fields (CDC) | CDC sync | `clickzetta-cdc-sync-pipeline` |
| Kafka message data | Kafka Pipe | `clickzetta-kafka-ingest-pipeline` |
| OSS/S3 files | OSS Pipe | `clickzetta-oss-ingest-pipeline` |
| Regular DB tables (no CDC markers) | Batch sync | `clickzetta-batch-sync-pipeline` |

### Partition and bucketing

```
Single table < 1GB:    no partitioning
1GB – 100GB:           PARTITIONED BY (days(event_date))
> 100GB:               PARTITIONED BY (days(event_date))
                       CLUSTERED BY (user_id) INTO 32 BUCKETS
```

Note: ClickZetta uses `PARTITIONED BY (days(col))`, not `PARTITIONED BY (col)`.

### Separation of DDL and scheduling

| Task type | Scheduling config | Studio state |
|---|---|---|
| DDL (CREATE TABLE, CREATE SCHEMA) | **No Cron, no dependencies** | DRAFT |
| ETL transform / data sync | Cron + upstream dependencies | PUBLISHED |
| DWS/ADS aggregation (Dynamic Table) | **No Studio task** — system auto-refreshes | — |

> Common mistake: configuring Cron on DDL tasks causes repeated execution and scheduling conflicts. DDL tasks must stay DRAFT.

### Studio task directory

```
<domain>_dw/
├── 00_sync_<source>_to_ods    ← data sync (Cron, runs first)
├── 01_ddl_ods                 ← ODS DDL (DRAFT, no scheduling)
├── 02_ddl_dwd                 ← DWD DDL (DRAFT, no scheduling)
├── 03_ddl_dws_ads             ← DWS/ADS dynamic table DDL (DRAFT, no scheduling)
├── 04_transform_ods_to_dwd    ← ODS→DWD cleansing (Cron, depends on 00)
└── 05_dqc_check               ← data quality check (optional)
```

### Data quality checkpoints

| Layer | Key checks |
|---|---|
| ODS/Bronze | NULL rate, CDC _op distribution, row count matches source |
| DWD/Silver | Uniqueness, LEFT JOIN match rate, key field non-null rate |
| DWS/Gold/ADS | Metric anomalies, Dynamic Table refresh history = SUCCESS |

### Delivery checklist

- [ ] Row counts match expectations at each layer
- [ ] Dynamic Table refresh history shows SUCCESS
- [ ] Key field NULL rate within acceptable range
- [ ] No redundant scheduled tasks for DWS/ADS layer
- [ ] All DDL tasks in DRAFT state

---

## Core Principles

1. **Explore data first, then recommend** — no questionnaires
2. **Give choices, not blank forms** — user picks A/B
3. **Dynamic Table for aggregation layers, not Materialized View**
4. **Modeling and pipeline together** — DDL and pipeline config output simultaneously
5. **ODS/Bronze zero transformation** — preserve raw data for traceability
6. **Separate DDL from scheduling** — DDL tasks DRAFT, DWS/ADS no scheduled tasks
7. **REFRESH immediately after creating Dynamic Table** — reset refresh baseline

## Routing

| Scenario | Route to |
|---|---|
| Want to use dbt for modeling instead of raw SQL | `clickzetta-dbt-project-setup` |
| Need SQL pipeline objects only (DT/MV/Stream/Pipe) | `clickzetta-sql-pipeline-manager` |
| Need to sync data from MySQL/PostgreSQL in real-time | `clickzetta-cdc-sync-pipeline` |
| Need to sync data from any DB in batch | `clickzetta-batch-sync-pipeline` |
| Not sure which ingestion method to use | `clickzetta-data-ingest-pipeline` |
| Need comprehensive pipeline health check | `clickzetta-pipeline-review` |
