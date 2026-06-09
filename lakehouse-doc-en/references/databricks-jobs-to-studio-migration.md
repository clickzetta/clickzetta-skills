# Databricks Jobs → Lakehouse Studio Migration Guide: E-Commerce ETL Pipeline

If your data pipeline runs on Databricks Jobs — multi-task DAGs, task dependencies, scheduled triggers — the core migration effort to Singdata Lakehouse Studio is very low. Task content (PySpark/SQL code) is minimally rewritten with ZettaPark (4 mechanical substitutions). Task orchestration (DAG dependencies, cron scheduling) is rebuilt with a few `cz-cli` commands, all configured in one pass.

This article validates this with a real e-commerce ETL pipeline: Bronze ingestion → Silver cleansing and joining → Gold aggregation. 3 tasks + DAG dependencies + daily 02:00 schedule, fully migrated to Lakehouse Studio, passing all 8 automated validations.

Full code on GitHub: [databricks2lakehouse-jobs](https://github.com/clickzetta/databricks2lakehouse-jobs)

---

## Source Project

`01_source/jobs/ecommerce_etl_job.json`: Original Databricks Jobs definition — 3 notebook tasks, dependency chain 01→02→03, daily trigger at 02:00 AM:

```json
{
  "name": "ecommerce_etl_pipeline",
  "schedule": {"quartz_cron_expression": "0 0 2 * * ?"},
  "tasks": [
    {"task_key": "ingest_raw",       "notebook_task": {...}},
    {"task_key": "transform_silver", "depends_on": [{"task_key": "ingest_raw"}]},
    {"task_key": "aggregate_gold",   "depends_on": [{"task_key": "transform_silver"}]}
  ],
  "email_notifications": {"on_failure": ["oncall@company.com"]}
}
```

The pipeline processes e-commerce clickstream: 500 events × 30 products → daily sales summary across 5 categories.

Migrated code is in `03_lakehouse/tasks/`, comparable file-by-file with `01_source/notebooks/`.

## Conclusion First

| Change | Effort | Notes |
|--------|--------|------|
| Task content (Python code) | Very low | ZettaPark 4 substitutions (import/session/table path/saveAsTable) |
| Task creation | Low | `cz-cli task create --type PYTHON --folder <id>` |
| Dependencies | Low | `--dep-tasks '[{"taskId":N,"taskName":"x"}]'` |
| Quartz cron → standard cron | Very low | `"0 0 2 * * ?"` → `"0 2 * * *"` |
| Alert notifications | Low | Databricks email → Studio monitoring rules (email/DingTalk/Feishu) |

`dbutils.notebook.run(nb)`, Job cluster configuration — no migration needed, handled automatically by Studio DAG and Virtual Cluster.

---

## Tech Stack Comparison

| | Databricks Jobs | Lakehouse Studio |
|---|---|---|
| Pipeline definition | Job JSON (`tasks: [...]`) | `cz-cli task create/save-config` |
| Task dependencies | `depends_on: [{task_key}]` | `--dep-tasks '[{"taskId":N,"taskName":"x"}]'` |
| Task content | Databricks Notebook (PySpark) | Studio Python task (ZettaPark) |
| Session | `spark` (global injection) | `clickzetta_dbutils.get_active_lakehouse_engine()` |
| Schedule cron | Quartz `"0 0 2 * * ?"` | Standard `"0 2 * * *"` |
| Cluster configuration | `job_clusters: [{...EC2 config}]` | Virtual Cluster auto-managed, no configuration needed |
| `dbutils.notebook.run(nb)` | Chained invocation | Replaced by Studio DAG dependencies |
| Failure alerts | `email_notifications.on_failure` | Studio monitoring rules (email/DingTalk/Feishu) |

---

![](.topwrite/assets/anim-32-databricks-jobs-migration.svg)

---

## Migration Steps

### Step 1: Task Content — ZettaPark 4 Substitutions

Each notebook requires minimal changes; all business logic is preserved:

```python
# Databricks notebook (original)
from pyspark.sql import functions as F                   # ← pyspark

df = spark.read.csv("/Volumes/ecommerce/landing/events/") # ← spark global
events = spark.table("ecommerce.bronze.raw_events")       # ← 3-level naming

df.write.saveAsTable("ecommerce.silver.events_enriched")
```

```python
# Studio Python task (03_lakehouse/tasks/02_transform_silver.py)
from clickzetta.zettapark import functions as F           # ① import
# session injected by platform (via clickzetta_dbutils)   # ② session

events = session.table("jobs_bronze.raw_events")          # ③ table path
df.write.saveAsTable("jobs_silver.events_enriched")        # ④ saveAsTable
```

DataFrame logic (join/filter/groupBy/agg/withColumn) is completely unchanged.

### Step 2: Task Creation

```bash
# "task_key" in Databricks Jobs JSON corresponds to Studio task name
# --type is required (SQL / PYTHON / SHELL etc.)
# --folder specifies task folder ID (query via cz-cli task list-folders)

cz-cli task create etl_01_ingest_raw      --type PYTHON --folder 91047 --profile aws_singapore_prod
cz-cli task create etl_02_transform_silver --type PYTHON --folder 91047 --profile aws_singapore_prod
cz-cli task create etl_03_aggregate_gold   --type PYTHON --folder 91047 --profile aws_singapore_prod

# Upload task scripts
cz-cli task save-content <task_id> --file 03_lakehouse/tasks/01_ingest_raw.py
```

### Step 3: Set DAG Dependencies

Databricks Jobs uses `depends_on: [{task_key}]`; Studio uses `--dep-tasks` (requires both taskId and taskName):

```bash
# Databricks Job JSON:
# {"task_key": "transform_silver", "depends_on": [{"task_key": "ingest_raw"}]}

# Studio equivalent (requires taskId + taskName both):
cz-cli task save-config <id_02> \
  --deps replace \
  --dep-tasks '[{"taskId":10143594,"taskName":"etl_01_ingest_raw"}]'

cz-cli task save-config <id_03> \
  --deps replace \
  --dep-tasks '[{"taskId":10144488,"taskName":"etl_02_transform_silver"}]'
```

### Step 4: Schedule Cron

Databricks uses Quartz 6-field format; Studio uses standard 5-field cron:

```bash
# Databricks: "quartz_cron_expression": "0 0 2 * * ?"  (seconds minutes hours day month weekday)
# Studio:     standard cron "0 2 * * *"                 (minutes hours day month weekday)

cz-cli task save-cron <id_01> --cron "0 2 * * *"
```

### Step 5: Deploy

```bash
cz-cli task deploy <id_01>   # Must deploy before task can be scheduled
cz-cli task deploy <id_02>
cz-cli task deploy <id_03>

# Manual trigger (equivalent to Databricks "Run now")
cz-cli task execute <id_01>
```

### Step 6: Failure Alert Configuration

Databricks configures `email_notifications` directly in the Job JSON; Studio configures via monitoring rules:

| Databricks | Studio |
|---|---|
| Job JSON `email_notifications.on_failure` | Studio UI: Alert Monitoring → New Monitoring Rule |
| Email only | Supports email, SMS, phone (high severity), Webhook (DingTalk/Feishu) |
| Task-level configuration | Notification policies can be reused across tasks |

**Configuration path**: Studio UI → Operations Monitoring → Alert Monitoring → New Monitoring Rule → Select "Task Instance Failure" event → Configure notification method (email/DingTalk/Feishu Webhook)

---

## E2E Validation Results

Tested on AWS Singapore instance, 8/8 all passed:

| Check | Expected | Result |
|--------|--------|------|
| jobs_bronze.raw_events | 500 | ✅ |
| jobs_bronze.products | 30 | ✅ |
| jobs_silver.events_enriched | 500 | ✅ |
| jobs_gold.daily_sales rows | 115 | ✅ |
| Total sales amount | 12,814.84 | ✅ |
| Total order count | 119 | ✅ |
| Category count | 5 | ✅ |
| Studio tasks all ONLINE | 3/3 | ✅ |

---

## Notes

- **`--dep-tasks` requires both taskId and taskName**: Passing only taskId will return `taskName is required`. Both fields are mandatory.
- **`--folder` takes folder ID, not name**: Query the ID with `cz-cli task list-folders`.
- **Task names cannot contain slashes**: The `folder/taskname` format will be parsed as a path in the CLI. Use the `--folder <id>` parameter to specify the folder, and only write the task name in the name field.
- **`--type` is required**: `cz-cli task create` will error without `--type`. Common types: `PYTHON`, `SQL`, `SHELL`.
- **Cron format conversion**: Quartz 6-field (seconds minutes hours day month weekday) → standard 5-field (minutes hours day month weekday). `"0 0 2 * * ?"` → `"0 2 * * *"`.

## Related Documentation

### Studio Task Development

- [Task Development and Scheduling](task-develop.md): Creating, editing content, and scheduling Studio tasks
- [Task Scheduling Dependencies](task_scheduling_dependency.md): DAG dependency configuration details
- [Studio Python Task Development Guide (ZettaPark)](studio-python-task-zettapark.md)
- [Studio Task Development and Operations (cz-cli)](cz-cli-studio-tasks.md)

### Other Migration Guides

- [Databricks Notebook → Lakehouse Migration Guide](databricks-notebook-to-studio-migration.md): Single Notebook → Studio task
- [Databricks DLT → Lakehouse Migration Guide](databricks-dlt-to-lakehouse-migration.md): Declarative pipeline migration
- [Databricks Unity Catalog → Lakehouse Migration Guide](databricks-uc-governance-to-lakehouse-migration.md): Permissions and governance
