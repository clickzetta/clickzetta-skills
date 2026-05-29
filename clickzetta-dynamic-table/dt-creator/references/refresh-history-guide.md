# Dynamic Table Incremental Refresh History Query Guide

There are three ways to view the incremental refresh history of a DT/MV, each suited to different scenarios.

---

## Method 1: SHOW DYNAMIC TABLE REFRESH HISTORY

View job-level information for DT refreshes, including the status, duration, trigger type, and refresh mode of each refresh.

### Syntax

```sql
-- Filter by WHERE (name column matches table name)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt';

-- Combine WHERE + LIMIT
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt' AND state = 'SUCCEED' LIMIT 20;

-- MV supports the same syntax
SHOW MATERIALIZED VIEW REFRESH HISTORY WHERE name = 'my_mv' LIMIT 10;
```

### Output Columns

| Column | Type | Description |
|------|------|------|
| workspace_name | STRING | Workspace the DT/MV belongs to |
| schema_name | STRING | Schema the DT/MV belongs to |
| name | STRING | DT/MV name |
| virtual_cluster | STRING | Virtual cluster that executed the refresh |
| start_time | TIMESTAMP | Refresh start time |
| end_time | TIMESTAMP | Refresh end time (NULL while running) |
| duration | INTERVAL | Refresh duration (shows elapsed time while running) |
| state | STRING | Refresh status (SUCCEED / FAILED / RUNNING, etc.) |
| refresh_trigger | STRING | Trigger type: `SYSTEM_SCHEDULED` (auto-triggered by system) or `MANUAL` (user manually triggered REFRESH) |
| refresh_mode | STRING | Refresh mode; see detailed description below |
| error_message | STRING | Error message on failure (NULL on success) |
| source_tables | ARRAY<MAP<STRING,STRING>> | Source table list; each element is a MAP with keys `workspace`, `schema`, `table_name` |
| stats | MAP<STRING,STRING> | Refresh statistics, including `rows_inserted` and `rows_deleted` |
| job_id | STRING | Corresponding Job ID; can be used to join `information_schema.job_history` for more details |

### refresh_mode Details

`refresh_mode` is the key field for determining whether incremental computation is working:

| Value | Meaning | Description |
|----|------|------|
| `INCREMENTAL` | Incremental refresh | The incremental engine successfully generated an incremental plan and only processed change data from source tables |
| `FULL` | Full refresh | Fell back to full recomputation. Possible reasons: first refresh, dimension table change, incremental plan generation failed, user forced full, etc. |
| `NO_DATA` | No data changes | No new data changes in source tables since the last refresh; this refresh skipped computation |

### source_tables Details

The `source_tables` column returns information about all input tables involved in this refresh; each element is a MAP:

```
[
  {"workspace": "my_ws", "schema": "public", "table_name": "orders"},
  {"workspace": "my_ws", "schema": "public", "table_name": "dim_product"}
]
```

### stats Details

The `stats` column returns write statistics for the target table from this refresh:

```
{"rows_inserted": "1000", "rows_deleted": "50"}
```

- `rows_inserted`: number of rows inserted into the target table in this refresh
- `rows_deleted`: number of rows deleted from the target table in this refresh (in incremental mode, update operations produce delete + insert)

### Typical Usage

```sql
-- View failed refresh records
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt' AND state = 'FAILED';

-- Check if it fell back to full refresh (troubleshoot whether incremental is working)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt' AND refresh_mode = 'FULL';

-- View no-data-change refreshes (appears when source table has no new data)
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt' AND refresh_mode = 'NO_DATA';

-- View system auto-scheduled refreshes
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'my_dt' AND refresh_trigger = 'SYSTEM_SCHEDULED';
```

---

## Method 2: DESC HISTORY

View version-level history of a table, including row count, bytes, and operation type for each version. Useful for understanding data change granularity.

### Syntax

```sql
-- View version history of a DT
DESC HISTORY my_dt;

-- View version history of a source table
DESC HISTORY source_table;

-- Supports WHERE filtering
DESC HISTORY my_dt WHERE version > 10;

-- Supports LIMIT
DESC HISTORY my_dt LIMIT 20;
```

### Output Columns

For regular tables (DESC_TABLE_HISTORY):

| Column | Type | Description |
|------|------|------|
| sequence | BIGINT | Sequence number |
| version | BIGINT | Version number |
| time | TIMESTAMP | Version creation time |
| total_rows | BIGINT | Total row count for this version |
| total_bytes | BIGINT | Total bytes for this version |
| user | STRING | User who performed the operation |
| operation | STRING | Operation type (INSERT / COMPACTION / REFRESH, etc.) |
| job_id | STRING | Corresponding Job ID |

For DT/MV (DESC_MV_HISTORY), additionally includes:

| Column | Type | Description |
|------|------|------|
| source_tables | ARRAY<MAP<STRING,STRING>> | Source tables and their corresponding version information |

DESC HISTORY's `source_tables` for DT/MV is more detailed than SHOW REFRESH HISTORY, including snapshot information for each source table at that version:

```
[
  {"table_name": "orders", "workspace": "my_ws", "schema": "public", "version": "123", "sequence": "5", "commit_time": "2025-01-15 10:30:00"},
  {"table_name": "dim_product", "workspace": "my_ws", "schema": "public", "version": "456", "sequence": "2", "commit_time": "2025-01-15 08:00:00"}
]
```

- `version`: snapshot_id of the source table
- `sequence`: sequence number of the source table
- `commit_time`: commit time of that version of the source table

This information can be used to trace which version of source table data was read in a given refresh.

### Typical Usage

```sql
-- View recent version changes of a DT; confirm compaction is executing normally
DESC HISTORY my_dt LIMIT 10;

-- View version history of a source table; determine data write frequency
DESC HISTORY source_table LIMIT 20;

-- View compaction records of a DT
DESC HISTORY my_dt WHERE operation = 'COMPACTION';
```

---

## Method 3: information_schema.materialized_view_refresh_history

Query refresh history from information_schema; suitable for cross-table batch analysis, integration with other systems, or long-term trend monitoring. Data is partitioned by day (pt_date); retention days are determined by system configuration.

### Syntax

```sql
-- View refresh history for a specific DT
SELECT *
FROM information_schema.materialized_view_refresh_history
WHERE materialized_view_name = 'my_dt'
ORDER BY start_time DESC
LIMIT 10;

-- View refresh status of all DTs on a given day
SELECT materialized_view_name, status, start_time, end_time, error_message
FROM information_schema.materialized_view_refresh_history
WHERE pt_date = '2025-01-15'
ORDER BY start_time DESC;

-- View failed refreshes
SELECT materialized_view_name, error_code, error_message, start_time
FROM information_schema.materialized_view_refresh_history
WHERE status = 'FAILED' AND pt_date >= '2025-01-01'
ORDER BY start_time DESC;
```

### Output Columns

| Column | Type | Description |
|------|------|------|
| workspace_name | STRING | Workspace the DT/MV belongs to |
| schema_name | STRING | Schema the DT/MV belongs to |
| materialized_view_name | STRING | DT/MV name |
| cru | DOUBLE | Compute resource units consumed |
| virtual_cluster_name | STRING | Virtual cluster that executed the refresh |
| status | STRING | Refresh status |
| scheduled_start_time | TIMESTAMP | Scheduled start time |
| start_time | TIMESTAMP | Actual start time |
| end_time | TIMESTAMP | End time |
| error_code | STRING | Error code |
| error_message | STRING | Error message |
| pt_date | STRING | Partition date |

### Typical Usage

```sql
-- Calculate the refresh success rate of a DT over the last 7 days
SELECT
    pt_date,
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'SUCCEED' THEN 1 ELSE 0 END) AS success,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed
FROM information_schema.materialized_view_refresh_history
WHERE materialized_view_name = 'my_dt'
  AND pt_date >= DATE_FORMAT(DATEADD(DAY, -7, CURRENT_DATE()), '%Y-%m-%d')
GROUP BY pt_date
ORDER BY pt_date;

-- View refreshes that consumed the most CRU
SELECT materialized_view_name, cru, start_time, end_time
FROM information_schema.materialized_view_refresh_history
WHERE pt_date >= '2025-01-01'
ORDER BY cru DESC
LIMIT 10;
```

### Difference from information_schema.job_history

`information_schema.job_history` records all types of Jobs (SQL queries, DML, DDL, etc.), while `materialized_view_refresh_history` specifically records DT/MV refresh history with more targeted fields.

If you need to view complete information about a refresh Job (e.g., job_text, input_bytes, etc.), you can join via job_id:

```sql
-- Get job_id from SHOW DYNAMIC TABLE REFRESH HISTORY, then look up details in job_history
SELECT *
FROM information_schema.job_history
WHERE job_id = '<job_id from SHOW REFRESH HISTORY>'
  AND pt_date = '2025-01-15';
```

---

## Comparison of Three Methods

| Feature | SHOW REFRESH HISTORY | DESC HISTORY | information_schema |
|------|---------------------|--------------|-------------------|
| Granularity | Refresh job level | Table version level | Refresh job level |
| Refresh mode (incremental/full/no data) | ✅ refresh_mode | ❌ | ❌ |
| Trigger type (scheduled/manual) | ✅ refresh_trigger | ❌ | ❌ |
| Write statistics (inserted/deleted) | ✅ stats | ❌ | ❌ |
| Source table list | ✅ table name level | ✅ includes version/sequence/commit_time | ❌ |
| Version number / total rows / total bytes | ❌ | ✅ version/total_rows/total_bytes | ❌ |
| CRU consumption | ❌ | ❌ | ✅ cru |
| Cross-table batch queries | ❌ (single table) | ❌ (single table) | ✅ (batch supported) |
| Compaction records | ❌ | ✅ | ❌ |
| Applicable scenarios | Troubleshoot whether incremental is working; refresh status | View data version changes; trace source table versions | Batch analysis / monitoring / CRU statistics |
