# Dynamic Table Scheduling Method Selection Guide

## Comparison of Two Scheduling Methods

| Method | Approach | Advantages | Disadvantages |
|------|------|------|------|
| **DDL built-in scheduling** (REFRESH INTERVAL) | Write a `REFRESH INTERVAL` clause in CREATE DYNAMIC TABLE; Lakehouse triggers automatically | Simple; no additional configuration needed | No alerts, no dependency orchestration; refresh status can only be checked via manual SQL |
| **Studio Task scheduling** (recommended) | Create a scheduled task in Studio; task content is the `REFRESH DYNAMIC TABLE` command | Supports upstream/downstream dependencies, unified alerts, visual monitoring | Requires creating an additional Task |

**Studio Task scheduling is recommended for production environments.** DDL built-in scheduling is suitable for quick validation and development/testing phases.

---

## DDL Built-in Scheduling

Define the refresh frequency via the `REFRESH INTERVAL` clause in the CREATE statement; Lakehouse triggers periodically:

```sql
CREATE DYNAMIC TABLE sales_daily
REFRESH INTERVAL 1 DAY
VCLUSTER default
AS
SELECT DATE(created_at) AS dt, SUM(amount) AS total
FROM orders
GROUP BY 1;
```

### Drawbacks

- **No alerts**: refresh failures are not proactively notified; status can only be checked by manually executing SQL
- **No dependency orchestration**: cannot declare "refresh only after upstream task completes"; can only stagger by time interval
- **High monitoring cost**: need to periodically manually execute the following command to check whether refresh is normal

```sql
-- View refresh history; confirm state is SUCCEED
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'your_dt_name';
```

Key field descriptions:

| Field | Meaning |
|------|------|
| `state` | SUCCEED / FAILED / RUNNING / QUEUED |
| `refresh_mode` | INCREMENTAL / FULL / NO_DATA |
| `error_message` | Error message on failure |
| `duration` | Duration of this refresh |
| `stats` | Incremental row count (rows_inserted / rows_deleted) |

---

## Studio Task Scheduling (Recommended for Production)

Create a SQL task in Studio; task content is the REFRESH command; managed by Studio's scheduling system.

### Task Content

**Non-partitioned DT:**

```sql
REFRESH DYNAMIC TABLE schema_name.dt_name;
```

**Partitioned DT (with parameters):**

```sql
SET dt.args.ds = '${bizdate}';
REFRESH DYNAMIC TABLE schema_name.dt_name PARTITION (ds = '${bizdate}');
```

`${bizdate}` is automatically replaced with the business date by the Studio scheduling engine at each execution.

### Must Configure Self-dependency

Concurrent REFRESH on the same DT is prohibited (causes write conflicts or data inconsistency). The Task must enable **self-dependency** to ensure the next instance starts only after the previous one completes.

### Upstream Dependency Configuration

- If the DT's source table data needs to wait for an upstream task to produce before refreshing → configure upstream dependency
- If source table data does not require synchronized readiness (e.g., real-time write table) → upstream dependency is optional

### Alert Configuration

Studio Tasks support the following alert rules; all are recommended for production environments:

- **Failure alert**: notify when task execution fails
- **Timeout alert**: notify when refresh duration exceeds a threshold (used to detect performance regression)
- **Not-run alert**: notify when the task has not started within the expected time

---

## Scheduling Orchestration for Multi-level DT Pipelines

When multiple DTs form upstream/downstream dependencies (e.g., DT_A → DT_B → DT_C), each DT corresponds to one Studio Task; task dependency relationships ensure execution order:

```
Task_A (REFRESH DT_A)
    └─ Task_B (REFRESH DT_B, depends on Task_A)
        └─ Task_C (REFRESH DT_C, depends on Task_B)
```

REFRESHes for different partitions can run in parallel (assigned to different Task instances); concurrent refresh of the same partition/non-partitioned DT is prohibited.

---

## Decision Logic: Recommend Scheduling Method to Users

When helping users create or configure a DT, recommend based on the following logic:

1. **Is Studio available?**
   - Yes → always recommend Studio Task scheduling, regardless of development or production environment
   - No → use DDL built-in scheduling or a third-party scheduling engine

2. **Are there upstream/downstream dependencies?**
   - Yes (e.g., source table is produced by another task) → must use Studio Task; configure upstream dependency
   - No → still recommend Studio Task to gain alert capability

3. **User has already written a REFRESH INTERVAL clause?**
   - Suggest: the REFRESH INTERVAL clause can be removed and replaced with Studio Task scheduling to gain alert and dependency management capability
   - REFRESH INTERVAL and Studio Task can coexist, but will cause double triggering; choosing one is recommended

---

## Alert Message Template

When the user is using DDL built-in scheduling, use the following message:

> 💡 **Suggestion**: You are currently using DDL built-in scheduling (REFRESH INTERVAL), which has the following limitations:
>
> 1. **No alerts**: refresh failures are not proactively notified; you need to manually execute `SHOW DYNAMIC TABLE REFRESH HISTORY` to check status
> 2. **No dependency orchestration**: upstream/downstream task dependencies cannot be declared; can only stagger by time interval
>
> **Recommendation**: Create a scheduled task in Studio with content `REFRESH DYNAMIC TABLE schema.dt_name`, and configure:
> - Self-dependency (prevent concurrent refresh)
> - Failure alert + timeout alert
> - Upstream dependency (if source table is produced by other tasks)
