---
name: clickzetta-dba-guide
description: |
  ClickZetta Lakehouse DBA daily operations handbook. Covers the 5 most common DBA tasks:
  compute cluster operations, job monitoring and diagnosis, data recovery and protection,
  storage optimization and maintenance, schema and object management.
  Each operation provides directly executable SQL with ClickZetta-specific constraints noted.

  Trigger when the user says: "start/stop cluster", "resize cluster", "cancel job",
  "slow query", "recover dropped table", "UNDROP", "RESTORE", "compact small files",
  "OPTIMIZE", "ANALYZE TABLE", "storage usage", "DBA operations",
  "create schema", "drop schema", "rename table", "object management", "schema management".

  For user/role/permission management and network policies, use lakehouse-doc-en.
  For cost analysis and billing, use this skill or clickzetta-metadata.
  Keywords: DBA, operations, monitoring, troubleshooting, cluster management, storage
---

# ClickZetta Lakehouse DBA Guide

See [references/operations-sql.md](references/operations-sql.md) for complete SQL reference:
job monitoring queries, data recovery, storage optimization, and schema/object management.

---

## Cluster Operations

```sql
-- Start / stop
ALTER VCLUSTER my_cluster RESUME;
ALTER VCLUSTER my_cluster SUSPEND;
ALTER VCLUSTER my_cluster SUSPEND FORCE;   -- interrupt running jobs
ALTER VCLUSTER my_cluster CANCEL ALL JOBS;

-- Status
SHOW VCLUSTERS;
SHOW VCLUSTERS WHERE state = 'RUNNING';
DESC VCLUSTER EXTENDED my_cluster;
USE VCLUSTER my_cluster;

-- Resize GP cluster (fixed or elastic)
ALTER VCLUSTER my_gp SET VCLUSTER_SIZE = 8;
ALTER VCLUSTER my_gp SET MIN_VCLUSTER_SIZE = 2 MAX_VCLUSTER_SIZE = 16;

-- Resize AP cluster
ALTER VCLUSTER my_ap SET MIN_REPLICAS = 1 MAX_REPLICAS = 4;
ALTER VCLUSTER my_ap SET MAX_CONCURRENCY = 16;

-- Auto-suspend / auto-resume
ALTER VCLUSTER my_cluster SET AUTO_SUSPEND_IN_SECOND = 60 AUTO_RESUME = TRUE;
ALTER VCLUSTER my_cluster SET AUTO_SUSPEND_IN_SECOND = -1;  -- disable auto-suspend

-- AP cluster cache preload
ALTER VCLUSTER my_ap SET PRELOAD_TABLES = "sales.orders,sales.products";
SHOW PRELOAD CACHED STATUS;
```

**Constraints:**
- OPTIMIZE (small file compaction) only works on GP clusters — not AP clusters
- AP cluster size steps: 2^n (1/2/4/8/16...); GP cluster steps: 1
- Query timeout: `ALTER VCLUSTER my_cluster SET QUERY_RUNTIME_LIMIT_IN_SECOND = 3600`

---

## Job Monitoring Quick Reference

```sql
-- Real-time jobs
SHOW JOBS LIMIT 20;
CANCEL JOB '<job_id>';
EXPLAIN SELECT ...;
```

For slow query analysis, failed job diagnosis, and CRU consumption reports, see [references/operations-sql.md](references/operations-sql.md#job-monitoring-information_schema).

---

## Data Recovery Quick Reference

```sql
-- Recover dropped object
SHOW TABLES HISTORY IN my_schema;
UNDROP TABLE my_schema.orders;

-- Restore to point in time (⚠️ must use CAST, not plain string)
RESTORE TABLE my_schema.orders TO TIMESTAMP AS OF CAST('2024-01-15 10:00:00' AS TIMESTAMP);

-- Query historical data (read-only)
SELECT * FROM my_schema.orders TIMESTAMP AS OF CAST('2024-01-15 10:00:00' AS TIMESTAMP);
```

For full recovery SQL and constraints, see [references/operations-sql.md](references/operations-sql.md#data-recovery).

---

## Storage Optimization Quick Reference

```sql
-- Compact small files (GP cluster only)
OPTIMIZE my_schema.orders;
OPTIMIZE my_schema.orders WHERE dt = '2024-01-01';

-- Collect statistics
ANALYZE TABLE my_schema.orders COMPUTE STATISTICS;

-- Truncate
TRUNCATE TABLE my_schema.staging;
```

For full storage SQL, see [references/operations-sql.md](references/operations-sql.md#storage-optimization).

---

## Schema & Object Management Quick Reference

```sql
CREATE SCHEMA IF NOT EXISTS dwd;
ALTER SCHEMA ods SET COMMENT 'ODS raw data layer';
DROP SCHEMA IF EXISTS temp_schema CASCADE;
ALTER TABLE my_schema.orders RENAME TO my_schema.orders_v2;
DROP TABLE IF EXISTS my_schema.temp_table;
```

For full object management SQL, see [references/operations-sql.md](references/operations-sql.md#schema--object-management).

---

## ClickZetta DBA Key Constraints

| Scenario | Constraint |
|---|---|
| Permission model | No superuser; `instance_admin` cannot directly access workspace data |
| Custom roles | Workspace-level only; SQL creation only, not via web UI |
| OPTIMIZE | GP clusters only; AP clusters do not support small file compaction |
| UNDROP | Must be within `data_retention_days` retention period (default: 1 day) |
| RESTORE | Target timestamp cannot be earlier than table creation time |
| Dynamic masking | Preview feature — contact support to enable |
| Cluster sizing | AP: 2^n steps; GP: step 1; Sync type: minimum 0.25 CRU |
