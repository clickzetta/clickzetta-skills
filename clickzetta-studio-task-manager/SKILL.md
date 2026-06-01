---
name: clickzetta-studio-task-manager
description: |
  Manage ClickZetta Lakehouse Studio tasks, covering task type descriptions (batch sync/multi-table batch sync/
  real-time sync/multi-table real-time sync/data development), task folder organization, task type differentiation,
  cz-cli task command family, scheduling configuration, dependency management, and common issue troubleshooting.
  Implements the "separation of DDL and pipeline management" engineering standard: DDL tasks as drafts,
  ETL tasks with scheduling, Dynamic Tables with auto-refresh.
  Triggered when the user says "create Studio task", "task folder", "task scheduling", "cz-cli task",
  "task dependency", "task failed", "task status", "full database sync task", "ETL task orchestration",
  "task management", "separation of DDL and pipeline", "DDL task", "scheduling DAG", "task folder",
  "Studio task", "batch sync", "real-time sync", "multi-table real-time sync", "data development task",
  "task types", "which sync to choose", "sync task differences".
  Keywords: Studio task, task management, cz-cli task, scheduling, DAG, DDL draft, ETL pipeline, task folder, offline sync, realtime sync, CDC, task types
---

# ClickZetta Studio Task Management

## Wizard: Clarify Intent

Upon receiving a task management request, use an interactive question tool (e.g., `question`) to collect intent. If no such tool is available, list options in text:

```
question({
  questions: [{
    question: "What would you like to do?",
    options: [
      { label: "Build a new pipeline from scratch", description: "Create folders, DDL tasks, sync tasks, ETL tasks" },
      { label: "Manage existing tasks", description: "View status, modify config, configure dependencies, rerun, backfill" },
      { label: "Troubleshoot task issues", description: "Failure diagnosis, dependency check, log analysis → load clickzetta-pipeline-review" },
      { label: "Standards compliance check", description: "Check if existing tasks follow separation of DDL and pipeline standards" }
    ]
  }]
})
```

**If the user has clearly stated what they want to do, proceed directly without asking.**

For **building from scratch**, also collect: business domain/project name, data source type, layering structure.

## Data Pipeline Wizard (Used When Building from Scratch)

Full process: **Requirements Understanding → Data Exploration → Technical Selection → Plan Confirmation → Execution**

---

### Step 0: Requirements Input

**First ask if the user has a requirements document** (PRD, requirements spec, data warehouse design doc, etc.):

```
question({
  questions: [{
    question: "Before we start, do you have a requirements document or background description?",
    options: [
      { label: "Yes, I'll provide it", description: "Paste document content or upload file, I'll extract key information" },
      { label: "No, I'll describe verbally", description: "I'll guide you through a few key questions" }
    ]
  }]
})
```

**If document provided**: read the document, auto-extract business scenario, data sources, target outputs, freshness requirements, skip to Step 1.

**If no document**, collect the following business requirements (prefer interactive tools; if unavailable, list all in text):

```
question({
  questions: [
    {
      question: "What business scenario does this pipeline serve?",
      options: [
        { label: "BI reports / dashboards", description: "Fixed reports, clear metric system, T+1 or hourly" },
        { label: "Real-time monitoring / ops dashboard", description: "Minute-level latency, focus on real-time metrics" },
        { label: "Data science / feature engineering", description: "For model training or inference" },
        { label: "Data sharing / external output", description: "Provided to other systems or teams" }
      ]
    },
    {
      question: "Who are the data consumers?",
      options: [
        { label: "BI tools (Superset/Tableau, etc.)", description: "Need wide tables or aggregation tables" },
        { label: "Data analysts (SQL queries)", description: "Need cleaned detail tables" },
        { label: "Downstream systems / APIs", description: "Need structured output" },
        { label: "Data scientists (Python/ZettaPark)", description: "Need feature tables or raw detail" }
      ]
    },
    {
      question: "Data freshness requirements?",
      options: [
        { label: "T+1 (available next day)", description: "Batch run at midnight, data ready in the morning" },
        { label: "Hourly", description: "Updated every hour" },
        { label: "Minute-level", description: "Near real-time, latency < 10 minutes" },
        { label: "Second-level real-time", description: "CDC continuous sync, second-level latency" }
      ]
    }
  ]
})
```

Also confirm verbally (text follow-up, no menu needed):
- **Core metric definitions**: if involving GMV, active users, or other business metrics, confirm calculation logic
- **Project/business domain name**: used for task folder and schema naming (e.g., `ecommerce_dw`)

---

### Step 1: Data Exploration (AI executes autonomously, no user input needed)

After collecting requirements, immediately explore the current data state:

```sql
-- View related schemas and tables
SHOW SCHEMAS;
SHOW TABLES IN <relevant_schema>;

-- Check table sizes and row counts
SELECT table_schema, table_name,
       ROUND(bytes/1024.0/1024/1024, 2) AS size_gb, row_count
FROM information_schema.tables
WHERE table_type = 'MANAGED_TABLE'
ORDER BY bytes DESC NULLS LAST LIMIT 20;

-- Sample to understand field meanings
SELECT * FROM <schema>.<table> LIMIT 5;
```

Also use `cz-cli datasource list` to view configured external data sources.

---

### Step 2: Technical Selection (Choose data source type and ingestion method)

Based on requirements and data exploration results, use interactive tools to collect technical choices:

**Select data source type:**
```
question({ questions: [{ question: "Where does the data come from?", options: [
  { label: "External database", description: "MySQL / PostgreSQL / SQL Server / Oracle, etc." },
  { label: "Kafka message queue", description: "Kafka Topic → Lakehouse" },
  { label: "Object storage", description: "OSS / S3 / COS file import" },
  { label: "Lakehouse internal ETL layering", description: "ODS→DWD→DWS/ADS, SQL tasks + Dynamic Table" },
  { label: "End-to-end complete pipeline", description: "Data ingestion + layered modeling + aggregation" },
  { label: "Not sure, explore data first", description: "Look at existing data before recommending an approach" }
]}]})
```

**Follow-up (only needed for certain options):**

Selected "External database":
```
question({ questions: [{ question: "Sync freshness?", options: [
  { label: "Real-time sync (second-level)", description: "CDC, based on Binlog/WALs, continuously running" },
  { label: "Batch offline (hourly/daily)", description: "Periodic full sync, configure Cron" }
]}]})
```

Selected "Object storage":
```
question({ questions: [{ question: "Ingestion method?", options: [
  { label: "SQL Pipe (continuous auto-import)", description: "LIST_PURGE or EVENT_NOTIFICATION mode" },
  { label: "Studio batch sync task", description: "Periodic batch import, configure Cron" }
]}]})
```

Selected "Kafka":
```
question({ questions: [{ question: "Ingestion method?", options: [
  { label: "SQL Pipe (READ_KAFKA)", description: "Pure SQL, flexible, recommended for engineers" },
  { label: "Studio real-time sync task", description: "GUI configuration, supports JSONPath computed columns" }
]}]})
```

---

### Step 3: Plan Confirmation (Must execute, cannot skip)

Combining requirements and technical selection, present a complete plan summary to the user for confirmation:

```
question({
  questions: [{
    question: "Confirm the following plan to start building:\nBusiness scenario: <scenario>\nData source: <source_name>\nSync method: <batch/real-time/SQL Pipe>\nLayering structure: <ODS/DWD/DWS or Bronze/Silver/Gold>\nTarget schema: <schema>\nScheduling: <Cron or continuous running>\nReady to start?",
    options: [
      { label: "Confirmed, start building", description: "Load corresponding skill, begin creating tasks" },
      { label: "Need adjustments", description: "Re-collect information" }
    ]
  }]
})
```

After user confirmation, load the corresponding skill per routing table:

**Routing Table**

| Data Source | Freshness/Method | Load Skill |
|-------------|-----------------|------------|
| External database | Real-time single-table CDC | `clickzetta-realtime-sync-pipeline` |
| External database | Real-time multi-table/full database CDC | `clickzetta-cdc-sync-pipeline` |
| External database | Batch offline | `clickzetta-batch-sync-pipeline` |
| Kafka | SQL Pipe | `clickzetta-kafka-ingest-pipeline` |
| Kafka | Studio real-time sync | `clickzetta-realtime-sync-pipeline` |
| Object storage | SQL Pipe | `clickzetta-oss-ingest-pipeline` |
| Object storage | Studio batch sync | `clickzetta-batch-sync-pipeline` |
| Lakehouse internal ETL layering | — | `clickzetta-sql-pipeline-manager` |
| End-to-end complete pipeline / Not sure | — | `clickzetta-dw-modeling` |

> Real-time CDC single vs multi-table: user says "full database" or "multiple tables" → `cdc-sync-pipeline`; "one table" → `realtime-sync-pipeline`; if unclear, ask.

---

## Studio Task Types

Studio provides four major task categories. Choosing the wrong type is the most common engineering mistake:

### Batch Sync (Single-table)
Periodically full-sync a single source table to Lakehouse.

- **Use cases**: single-table periodic overwrite, low data freshness requirements (daily/hourly batch), resource optimization (no real-time needed)
- **Run mode**: scheduled (Cron required), full overwrite or append each run
- **Data sources**: MySQL, PostgreSQL, SQL Server, and other relational databases
- **Corresponding skill**: `clickzetta-batch-sync-pipeline` (single-table mode)

### Multi-table Batch Sync
Periodically batch-sync multiple tables or an entire database to Lakehouse.

- **Use cases**:
  - Full database migration (batch sync all tables, reducing per-table configuration effort)
  - Sharded table merge (merge multiple sharded tables into a unified target table)
  - Periodic data calibration (periodic full sync to ensure target matches source)
- **Run mode**: scheduled (Cron required), supports full database mirror, multi-table mirror, and sharded table merge modes
- **Data sources**: MySQL, PostgreSQL, SQL Server, etc.
- **Corresponding skill**: `clickzetta-batch-sync-pipeline` (multi-table mode)

### Real-time Sync (Single-table)
Continuously sync a single Kafka topic to Lakehouse in real time.

- **Use cases**: Kafka message stream real-time ingestion, second/minute-level latency requirements, single-topic fine-grained sync
- **Run mode**: continuously running (no Cron needed, runs upon submission)
- **Data sources**: **Kafka only** (JSON message parsing, supports JSONPath computed columns)
- **Corresponding skill**: `clickzetta-realtime-sync-pipeline`

### Multi-table Real-time Sync (CDC)
Sync entire MySQL / PostgreSQL databases or multiple tables to Lakehouse via CDC in real time, with full load + incremental two-phase sync.

- **Use cases**: full database real-time mirror, second-level end-to-end latency, sharded table real-time merge
- **Run mode**: continuously running (no Cron needed, runs upon submission)
- **Data sources**:

| Type | Incremental Read Mode | Supported Versions |
|------|----------------------|-------------------|
| MySQL (including Aurora MySQL, PolarDB MySQL) | Binlog | 5.6+, 8.x |
| PostgreSQL (including Aurora PG, PolarDB PG) | WALs | 14+ |

- **Corresponding skill**: `clickzetta-cdc-sync-pipeline`

### Data Development Tasks (SQL / Python / Shell)
Write and schedule data processing logic in Studio — the core vehicle for data warehouse ETL.

- **SQL tasks**: ODS→DWD cleaning/transformation, data quality checks, ad-hoc data repairs
- **Python tasks**: custom data processing scripts, external API calls, ML inference
- **Shell tasks**: system commands, file operations, external tool invocations
- **Run mode**: scheduled (Cron) or manual trigger
- **Corresponding skill**: `clickzetta-studio-task-manager` (this skill)

### Four Task Types Quick Comparison

| Task Type | Data Source | Sync Granularity | Run Mode | Freshness |
|-----------|------------|-----------------|----------|-----------|
| Batch Sync | Relational DB | Single table | Scheduled | Hourly/daily |
| Multi-table Batch Sync | Relational DB | Multi-table/full DB | Scheduled | Hourly/daily |
| Real-time Sync | **Kafka only** | Single topic | Continuously running | Seconds/minutes |
| Multi-table Real-time Sync | MySQL / PostgreSQL | Multi-table/full DB | Continuously running | Seconds |
| Data Development | Any (SQL/Python/Shell) | Custom logic | Scheduled or manual | Depends on schedule frequency |

---

## Core Principle: Separation of DDL and Pipeline Management

**Different task types have completely different scheduling strategies.** Confusing task types is the most common engineering mistake.

| Task Type | Typical Content | Studio Task Type | Scheduling | Status |
|-----------|----------------|-----------------|------------|--------|
| **DDL table creation** | CREATE TABLE / CREATE SCHEMA | SQL task | ❌ No Cron, no dependencies | DRAFT |
| **Data sync tasks** | External source (relational DB/object storage) → ODS | **SINGLE_DI / MULTI_DI / REALTIME** (not SQL tasks) | ✅ Configure Cron (batch) or continuous (real-time) | PUBLISHED |
| **ETL transformation** | ODS→DWD cleaning SQL (Lakehouse internal) | SQL task | ✅ Configure Cron + depend on upstream sync | PUBLISHED |
| **Data quality tasks** | Row count checks, NULL rate validation | SQL task | ✅ Configure Cron + depend on ETL | PUBLISHED |
| **DWS/ADS aggregation** | Metric summaries, report wide tables | ❌ Use Dynamic Table, no task needed | — | — |

**Data sync task supported data sources:**
- Batch sync (SINGLE_DI/MULTI_DI): MySQL, PostgreSQL, Oracle, SQL Server and other relational databases, plus OSS/COS/S3 object storage
- Single-table real-time sync (REALTIME): Kafka
- Multi-table real-time sync CDC: MySQL (Binlog, 5.6+/8.x), PostgreSQL (WALs, 14+)

**Other data access methods (not data sync tasks):**
- Kafka/OSS/S3/COS → can also use SQL Pipe (`READ_KAFKA`/Volume Pipe), both Studio sync tasks and SQL Pipes are valid — choose based on scenario
- Hive/Databricks/Snowflake Open Catalog → External Catalog federated read-only queries, not data sync

> ⚠️ **DDL tasks must never have Cron**: repeated execution of CREATE TABLE statements causes `SCHEDULE_TASK_HAD_CHILDREN_NODES_EXCEPTION` and other scheduling conflicts. DDL tasks should be demoted to DRAFT immediately after execution.

> ⚠️ **Do not create scheduled tasks for DWS/ADS layer**: Dynamic Tables auto-refresh by the system. Creating additional tasks is redundant computation and wastes resources.

> ⚠️ **Never use SQL tasks as a substitute for data sync tasks**: you cannot use SQL tasks to write `SELECT FROM EXTERNAL` to simulate sync (syntax not supported), nor use JDBC tasks (JDBC can only execute SQL on external databases, cannot sync data to Lakehouse).

---

## Task Folder Organization Standards

Each data warehouse project creates an independent task folder in Studio to manage all task assets uniformly:

```
<business_domain>_dw/                     ← Project task folder (e.g., shenyu_gateway_dw, ecommerce_dw)
├── 00_sync_<source>_to_ods               ← Data sync (Cron, runs earliest)
├── 01_ddl_ods                            ← ODS table creation (DRAFT, no scheduling, run once manually)
├── 02_ddl_dwd                            ← DWD table creation (DRAFT, no scheduling, run once manually)
├── 03_ddl_dws_ads                        ← DWS/ADS Dynamic Table creation (DRAFT, no scheduling)
├── 04_transform_ods_to_dwd               ← ODS→DWD transformation (Cron, depends on 00)
└── 05_dqc_check                          ← Data quality check (Cron, depends on 04, optional)
```

> DWS/ADS layer is auto-refreshed by Dynamic Tables — **no task creation needed**.

---

## cz-cli task Command Family

### Task Folder Management

```bash
# Create task folder
cz-cli task folder create <folder_name>

# List all task folders
cz-cli task folder list
```

### Task Queries

```bash
# List all tasks
cz-cli task list

# Filter by folder
cz-cli task list --folder <folder_name>

# View task details
cz-cli task get <task_id>

```

### Task Execution

```bash
# Manually trigger task run
cz-cli task run <task_id>

# View task run logs
cz-cli task logs <task_id>

```

### Task Creation

```bash
# Create SQL task (ETL/DDL)
cz-cli task create \
  --name "04_transform_ods_to_dwd" \
  --type SQL \
  --folder <folder_name> \
  --vcluster default \
  --sql-file ./transform.sql

# Create data sync task (single-table)
cz-cli task create \
  --name "00_sync_mysql_to_ods" \
  --type SINGLE_DI \
  --folder <folder_name>
```

> ⚠️ **Full database sync task (MULTI_DI) capability boundary**: `cz-cli` can create the task framework, but source/target column mapping configuration **must be completed manually in Studio UI**. Recommended SOP:
> 1. `cz-cli task create --type MULTI_DI` to create task framework
> 2. Copy the output task link, open in browser
> 3. Configure source database, target schema, column mapping in Studio UI
> 4. Click publish to run

---

## Scheduling Configuration Best Practices

### Cron Expression Reference

```
# Daily at 02:00 (data sync)
0 2 * * *

# Daily at 02:30 (ETL transformation, 30 minutes after sync completes)
30 2 * * *

# Daily at 03:00 (data quality check)
0 3 * * *

# Every hour
0 * * * *
```

### Dependency Configuration Principles

```
Correct dependency chain:
00_sync (Cron 02:00)
    ↓ depends on
04_transform (Cron 02:30)
    ↓ depends on
05_dqc (Cron 03:00)

Incorrect dependencies:
❌ DDL tasks (01/02/03) should not appear in the dependency chain
❌ Dynamic Tables should not appear in the dependency chain
```

---

## Data Sync Task Type Selection

| Scenario | Task Type | Notes |
|----------|-----------|-------|
| MySQL/PG single-table sync to Lakehouse | `SINGLE_DI` | Simple, CLI can fully configure |
| MySQL/PG full database sync (multi-table mirror) | `MULTI_DI` | CLI creates framework, UI configures mapping |
| Kafka real-time ingestion | `REALTIME_SYNC` | Continuously running, no Cron needed |
| File batch import (OSS/S3) | SQL task (COPY INTO) | Use SQL task to execute COPY INTO |

---

## Common Issue Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `SCHEDULE_TASK_HAD_CHILDREN_NODES_EXCEPTION` | DDL task was configured with Cron or dependencies | Clear DDL task scheduling config, demote to DRAFT |
| Task publish failed, circular dependency | Task A depends on B, B depends on A | Check dependency chain, remove circular dependencies |
| Sync task keeps failing, no clear error | Column type incompatibility (e.g., MySQL BIT(1) vs Lakehouse BOOLEAN) | Check column type mapping, refer to type mapping table below |
| Full database sync task cannot run after creation | MULTI_DI task missing column mapping config | Enter Studio UI to configure source/target mapping, then republish |
| ETL task not triggered on time | Upstream sync task failed, dependency not satisfied | Fix upstream sync task first, then manually trigger ETL |
| DWS layer data not updated | Mistakenly created scheduled task but Dynamic Table not refreshing | Delete redundant scheduled task, confirm Dynamic Table status is RUNNING |
| Task run succeeded but data is empty | SQL logic issue (e.g., LEFT JOIN filter condition in wrong position) | Check SQL — LEFT JOIN right-table filter conditions must be in the ON clause |

### MySQL → Lakehouse Column Type Mapping (Common Sync Pitfalls)

| MySQL Type | ❌ Don't Use | ✅ ODS Layer Use | DWD Layer Conversion |
|-----------|-------------|-----------------|---------------------|
| `BIT(1)` | `BOOLEAN` | `TINYINT` | `CAST(col AS BOOLEAN)` |
| `DATETIME` | `DATETIME` | `TIMESTAMP` | Use directly |
| `ENUM('a','b')` | `ENUM` | `STRING` | Use directly |
| `TEXT` / `LONGTEXT` | `TEXT` | `STRING` | Use directly |
| `DECIMAL(p,s)` | `FLOAT` | `DECIMAL(p,s)` | Use directly |
| `TINYINT(1)` | `BOOLEAN` | `TINYINT` | `CAST(col AS BOOLEAN)` |

> **ODS layer principle: prefer broad types** — sync successfully first, then do precise type conversion in the DWD layer to avoid sync failures due to type incompatibility.

---

## Complete Engineering SOP

### Code-as-Asset Principle

**In data pipeline development / data warehouse modeling scenarios, all SQL code should be saved as Studio tasks as manageable code assets.**

- Tasks are the vehicle for code, not just scheduling configurations
- Even one-time DDL executions should be saved as DRAFT tasks for easy reference, reuse, and multi-environment migration
- Scenarios that don't need to be saved as tasks: SELECT queries, ad-hoc fix SQL, one-time validation queries

### New Project Launch Process (with Quick Verification Checkpoints)

Agile principle: **verify immediately after each step, know within 30 seconds if it succeeded — don't wait until the full pipeline runs to discover issues.**

```
1. Create task folder
   cz-cli task folder create <business_domain>_dw

2. Create ODS layer tables, verify immediately
   cz-cli task save-content 01_ddl_ods --content "<ods_ddl_sql>"
   cz-cli task run 01_ddl_ods
   ✅ Verify: SHOW TABLES IN <ods_schema>  → confirm tables created

3. Create data sync task, trigger once manually, verify immediately
   - 00_sync: full database or single-table sync to ODS (MULTI_DI requires UI mapping config)
   cz-cli task execute 00_sync
   ✅ Verify: SELECT COUNT(*) FROM <ods_schema>.<table>  → compare with source row count
            SELECT * FROM <ods_schema>.<table> LIMIT 5  → sample check fields

4. Create DWD layer tables, verify immediately
   cz-cli task save-content 02_ddl_dwd --content "<dwd_ddl_sql>"
   cz-cli task run 02_ddl_dwd
   ✅ Verify: SHOW TABLES IN <dwd_schema>  → confirm tables created

5. Generate ETL transformation SQL, manually execute once to verify logic, then configure scheduling
   cz-cli task save-content 04_transform_ods_to_dwd --content "<etl_sql>"
   cz-cli task execute 04_transform_ods_to_dwd   ← run manually first
   ✅ Verify: SELECT COUNT(*) FROM <dwd_schema>.<table>  → row count meets expectations
            Check key field non-null rate, LEFT JOIN result rows ≥ left table rows
   After confirmation, configure scheduling:
   cz-cli task save-cron 04_transform_ods_to_dwd --cron '0 30 2 * * ? *'
   cz-cli task deploy 04_transform_ods_to_dwd

6. Create DWS/ADS Dynamic Tables, trigger first refresh for verification
   cz-cli task save-content 03_ddl_dws_ads --content "<dws_ads_ddl_sql>"
   cz-cli task run 03_ddl_dws_ads
   REFRESH DYNAMIC TABLE <dws_schema>.<table>
   ✅ Verify: SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 3
            → status = SUCCESS, row count matches aggregation logic

7. Optional: data quality check task (Cron + depends on 04)
   cz-cli task save-content 05_dqc_check --content "<dqc_sql>"
   cz-cli task save-cron 05_dqc_check --cron '0 0 3 * * ? *'
   cz-cli task deploy 05_dqc_check
```

> **Fail-fast principle**: if any step's verification fails, stop immediately and fix — don't continue. If ODS data is wrong, DWD will definitely be wrong too.

---

## Incremental Iteration Guide

**When modifying an existing pipeline, follow the incremental process — don't re-run the full pipeline build process.**

When the user says "add a table", "add a field", "add a metric", "change ETL logic", use interactive tools to collect the iteration type:

```
question({
  questions: [{
    question: "What modification do you want to make to the existing pipeline?",
    options: [
      { label: "Add sync table", description: "Add a source table to an existing sync task" },
      { label: "Add field", description: "Source table added a field, ODS/DWD need to follow" },
      { label: "Add metric/DWS layer", description: "Add aggregation logic or Dynamic Table" },
      { label: "Modify ETL logic", description: "Cleaning rules, filter conditions, JOIN relationship changes" }
    ]
  }]
})
```

### Add Sync Table

```
1. Check lineage, confirm impact scope
   Load clickzetta-table-lineage, confirm if new table has relationships with existing tables

2. Add table to existing sync task (or create new single-table sync task)
   cz-cli task content 00_sync  → view existing config
   Modify as needed and redeploy

3. Manually trigger sync, verify immediately
   cz-cli task execute 00_sync
   ✅ SELECT COUNT(*) FROM <ods_schema>.<new_table>

4. If DWD layer processing needed, add ETL SQL to 04_transform task
   cz-cli task content 04_transform_ods_to_dwd  → view existing SQL
   Append new table cleaning logic, manually execute to verify, then redeploy
```

### Add Field (Schema Evolution)

```
1. Check lineage, identify all affected downstream tasks/DTs
   Load clickzetta-table-lineage

2. Update layer by layer (upstream to downstream, cannot skip layers)
   ODS layer: ALTER TABLE <ods_schema>.<table> ADD COLUMN <col> <type>
   ✅ Verify: DESC TABLE <ods_schema>.<table>  → confirm field added

   DWD layer: update ETL SQL, add cleaning logic for new field
   Manually execute 04_transform to verify, then redeploy
   ✅ Verify: SELECT <new_col>, COUNT(*) FROM <dwd_schema>.<table> GROUP BY 1 LIMIT 5

   DWS/ADS layer (if needed): Dynamic Table doesn't support ALTER, use CREATE OR REPLACE to rebuild
   Immediately REFRESH DYNAMIC TABLE after rebuild
   ✅ Verify: SHOW DYNAMIC TABLE REFRESH HISTORY LIMIT 3  → status = SUCCESS

3. Update Studio task scripts (keep code assets in sync)
   cz-cli task save-content <task_name> --content "<updated_sql>"
```

### Add Metric/DWS Layer

```
1. Confirm metric definition (confirm calculation logic with user to avoid rework)

2. Check if DWD layer has required fields — if not, follow "Add Field" process first

3. Create new Dynamic Table
   CREATE OR REPLACE DYNAMIC TABLE <dws_schema>.<new_metric_table>
     REFRESH INTERVAL <n> <unit> vcluster <gp_cluster>
   AS SELECT ...;
   REFRESH DYNAMIC TABLE <dws_schema>.<new_metric_table>
   ✅ Verify: SELECT COUNT(*), SUM(<metric>) FROM <dws_schema>.<new_metric_table>
            Compare with known baseline values

4. Save DDL to Studio task
   cz-cli task save-content 03_ddl_dws_ads --content "<updated_ddl>"
```

### Modify ETL Logic

```
1. Check lineage, confirm downstream impact scope
   Load clickzetta-table-lineage

2. Verify new logic in dev/test environment first (if available)

3. Update ETL SQL
   cz-cli task content 04_transform_ods_to_dwd  → view existing logic
   After modification, manually execute to verify:
   cz-cli task execute 04_transform_ods_to_dwd
   ✅ Verify: row count comparison, key field sampling, compare with pre-modification results

4. After verification passes, redeploy
   cz-cli task save-content 04_transform_ods_to_dwd --content "<new_sql>"
   cz-cli task deploy 04_transform_ods_to_dwd

5. If downstream Dynamic Tables are affected, trigger full refresh
   SET cz.optimizer.incremental.force.full.refresh = true;
   REFRESH DYNAMIC TABLE <dws_schema>.<table>;
   SET cz.optimizer.incremental.force.full.refresh = false;
```

### Delivery Verification Checklist

- [ ] Row counts at each layer match expectations
- [ ] Dynamic Table's VCluster exists and `status = RUNNING` (`SHOW VCLUSTERS`)
- [ ] Dynamic Table refresh history shows SUCCESS
- [ ] Key field NULL rate within acceptable range
- [ ] LEFT JOIN result row count ≥ left table row count
- [ ] All DDL tasks are in DRAFT status
- [ ] No redundant scheduled tasks for DWS/ADS layer
- [ ] Scheduling DAG has no circular dependencies
- [ ] **ETL task dependency chain is complete** (`cz-cli task deps <task>` to verify, `task_dependencies` is not empty)
- [ ] Key tables and fields have comments; use ClickZetta comment syntax from `lakehouse-doc-en`

---

## Multi-environment Management (dev → prod)

ClickZetta isolates environments via **Workspace** (dev/staging/prod correspond to different Workspaces). Cross-Workspace pipeline migration currently has limited automation and mainly relies on manual operations.

**When the user raises multi-environment migration needs**, inform them of the following limitations and guide accordingly:

- Data source configurations, schemas, and VCluster names are independent across different Workspaces — each must be confirmed and replaced during migration
- There is currently no one-click migration tool — recommend contacting **data operations (lh-dba role)** for help planning multi-environment strategy
- You can use `cz-cli task content <task_id>` to export task scripts, manually adjust, then recreate in the target Workspace

> Multi-environment management is a platform capability evolution direction. At the current stage, it's recommended to use schema naming within a single Workspace to differentiate (e.g., `ecommerce_ods_dev` vs `ecommerce_ods`) to reduce migration complexity.
