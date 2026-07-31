# Sync Task Guide

---

## Four Sync Task Types

### 1. Single-table Offline Batch Sync (INTEGRATION, task_type=10)

3-step flow — source probing → schema review → save config:

```bash
# Step 1: Create task and probe source schema
cz-cli task create-offline-sync <name> \
  --folder <folder> --source <ds_name> \
  --source-db <db> --source-table <table> \
  --target-schema <schema> --target-table <table>

# Step 2: Re-fetch schema for Agent review (returns splitPk, WHERE, write_mode recommendations)
cz-cli task offline-sync-schema <task_id> \
  --source <ds> --source-db <db> --source-table <table> \
  --target-schema <schema> --target-table <table>

# Step 3: Save with Agent-generated config JSON
cz-cli task save-offline-sync <task_id> \
  --config '<json>' --vc <integration_vc> --target-schema <schema>

# If save-offline-sync returns create_table_ddl:
#   write DDL to file → cz-cli sql --file /tmp/table.sql --write → THEN deploy
cz-cli task save-cron <task_id> --cron '0 0 2 * * * *'
cz-cli task save-schedule <task_id> --vc <integration_vc>  # VC/schedule config separate from cron
cz-cli task deploy <task_id> -y
```

**columnMapping direction**: format is `"sink_col": "source_col"` (e.g. `"id": "ID"`).
Reversed direction causes Studio field-mapping switches to appear disabled.

### 2. Multi-table Offline Batch Sync (MULTI_DI, task_type=291)

One-step create + configure. Always specify `--tables` to avoid syncing system tables:

```bash
cz-cli task create-batch-sync <name> \
  --folder <folder> --source <ds_name> \
  --database <db> --tables "t1,t2,t3" \
  --pipeline-type 1 \                    # 1=mirror, 2=merge (sharding)
  --batch-size 4 --connections 4 --parallelism 4 \
  --pk-write-mode OVERWRITE --non-pk-write-mode OVERWRITE \
  --cron '0 0 2 * * * *'
```

> ⚠️ **`--tables` is critical** — omitting it syncs ALL tables. MySQL often exposes 35K+ system tables; syncing everything exhausts resources.

### 3. Multi-table Real-time CDC (MULTI_REALTIME, task_type=281)

Supported sources: MySQL, PostgreSQL, SQL Server, DM. Oracle is NOT supported for CDC.

```bash
cz-cli task create-realtime-sync <name> \
  --folder <folder> --source <ds_name> \
  --database <db> --tables "t1,t2" \     # Omit for whole-database (use with care)
  --pipeline-type 3 \                    # 1=tables mirror, 2=merge, 3=whole-database
  --sync-mode 1 \                        # 1=full+incremental, 2=incremental only
  --skip-check                           # Skip CDC prereq check if already verified

# Deploy → start (CDC tasks run continuously, no cron needed)
cz-cli task deploy <task_id> -y
cz-cli task start <task_id>
```

Check CDC prerequisites first:
```bash
cz-cli datasource check-cdc <ds_name>
```

### 4. Kafka Streaming Sync (REALTIME)

```bash
cz-cli task create-stream-sync <name> \
  --folder <folder> --source <kafka_ds> \
  --topic <topic> --target-schema <schema> --target-table <table> \
  --mode latest-offset --codec json \
  --cron '0 */10 * * * * *'             # heartbeat cron
# Note: field mapping must be configured in Studio UI before data flows
```

---

## Sync Task VC (Virtual Cluster)

Sync tasks require a dedicated INTEGRATION-type VCluster.

```bash
cz-cli sql --sync "SHOW VCLUSTERS"          # Find VCLUSTER_TYPE=INTEGRATION VCs
cz-cli sql --sync "DESC VCLUSTER <name>"    # Confirm type
```

> SUSPENDED VClusters **auto-resume** when a task starts (AUTO_RESUME=TRUE by default).
> No manual resume needed.

If no INTEGRATION VC exists:
```sql
CREATE VCLUSTER IF NOT EXISTS sync_vc VCLUSTER_TYPE=INTEGRATION VCLUSTER_SIZE=1 AUTO_RESUME=TRUE;
```

---

## INTEGRATION Config JSON

`save-offline-sync --config` requires JSON with `templateKey`, `sourceConnection`, `sinkConnection`, `jobs[]`.
Use `offline-sync-schema` output as the base — it returns `source_params_template.params` ready to use.

### WHERE Condition Syntax

> ⚠️ WHERE is pushed to the **source database via JDBC** — use the source DB's SQL dialect, not Lakehouse SQL.

| Source | Correct WHERE | Wrong |
|---|---|---|
| PostgreSQL | `created_at >= '2026-01-01'::date` | `created_at >= DATE '2026-01-01'` |
| MySQL | `created_at >= '2026-01-01'` | `created_at >= DATE '2026-01-01'` |
| SQL Server | `created_at >= '2026-01-01'` | — |
| Oracle | `CREATED_AT >= TO_DATE('2026-01-01', 'YYYY-MM-DD')` | Verified from schema probe — `TO_DATE` format confirmed |

### Scheduling Variables

| Behavior | Detail |
|---|---|
| `${bizdate}` in scheduled run | Replaced by the scheduler with current business date (e.g. `2026-06-17`) |
| `${bizdate}` in manual `execute` | **NOT replaced** — pass `--param bizdate=2026-06-17` for testing |
| Empty WHERE `""` | Rejected by CLI — remove the `where` key to sync all rows |

### writeMode Behavior

| writeMode | 0 rows from source |
|---|---|
| `OVERWRITE` | **⚠️ Target NOT cleared** — old data remains when source returns 0 rows |
| `APPEND` | Target unchanged (correct for incremental loads) |

### SQL Server Unsupported Column Types

Tested against `test_sqlserve_alltype` (28 columns) on aliyun_shanghai_prod:

| Type | Status | Notes |
|---|---|---|
| `sql_variant` | ❌ Unsupported | Fails at submit with `UnsupportedTypeException: Unsupported type: [SQL_VARIANT]` |
| `binary`, `varbinary` | ✅ Supported | Map to `BINARY` |
| `image` | ✅ Supported | Map to `BINARY` |
| `text`, `ntext` | ✅ Supported | Map to `STRING` |
| `timestamp` (rowversion) | Not tested | Not present in test table |
| `uniqueidentifier` | ✅ Supported | Map to `STRING` |
| `xml` | ✅ Supported | Map to `STRING` |

Only `sql_variant` needs to be removed from column lists before calling `save-offline-sync`.

### Source Type Mapping Principles

| Principle | Example |
|---|---|
| String: char/text/varchar → STRING | PG `varchar`, `text`, `bpchar` → `STRING` |
| Integer family maps directly | PG `int4`→`INT`, `int8`→`BIGINT`, `int2`→`INT` |
| Decimal: preserve precision | PG `numeric(10,2)`→`DECIMAL(10,2)`, `money`→`DECIMAL(19,4)` |
| Time: TIMESTAMP for all datetime | PG `timestamp`, `timestamptz`→`TIMESTAMP` |
| PG `serial`→`INT`, `uuid`→`STRING` | — |
| PG `vector` → `STRING` or `VECTOR(FLOAT, dim)` | Confirm dimension with user |
| PG `bit(1)`/`bit(n)` → `STRING` (ODS safe) | Avoid `BOOLEAN` for BIT(1) — may cause sync failures |
| PG `_text`, `_int4` (array types) → `ARRAY<STRING>`, `ARRAY<INT>` | Underscore prefix = array |
| MySQL `BIT(1)` → `TINYINT` (ODS), cast in DWD | `BOOLEAN` may cause sync failures |
| Oracle `NUMBER(p,0)` → `INT`/`BIGINT`; `NUMBER(p,s)` → `DECIMAL(p,s)` | — |
| Oracle `DATE` → `TIMESTAMP` | Oracle DATE includes time component |
| **PG column name case**: `a` and `A` collide in Iceberg | Rename one in sink; add `COMMENT` for traceability |
