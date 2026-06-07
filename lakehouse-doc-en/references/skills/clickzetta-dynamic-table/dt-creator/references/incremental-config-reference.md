# Dynamic Table Incremental Computation Configuration Reference

This document lists the configuration options available to users for incremental refresh in Dynamic Tables / Materialized Views. All configurations take effect at the Session level via `SET` statements.

---

## Refresh Strategy

Controls the switching behavior between incremental and full refresh.

### `cz.optimizer.incremental.force.full.refresh`

- Type: bool, default: `false`

Forces the current refresh to use full mode, skipping incremental logic and doing a full scan and recomputation of all source tables.

**Applicable scenarios:**
- Incremental refresh results show data anomalies (e.g., missing or duplicate data) and a full repair is needed
- A dimension table has undergone an important change (e.g., a mapping relationship was corrected) and all historical data needs to re-JOIN to the latest dimension
- The DT's state table was accidentally deleted or corrupted, causing incremental refresh errors, and a full recomputation from scratch is needed

**Advantage:** Full recomputation guarantees results are completely consistent with directly executing the SQL — it is the most reliable data repair method.

**Risk:** Full refresh requires scanning all data in all source tables; the computation volume and time are far greater than incremental refresh. For DTs with large data volumes, a single full refresh may take minutes or even hours.

**Note:** This is a one-time Session-level switch. After the refresh completes, it must be manually reset to `false`; otherwise every subsequent REFRESH will use full mode, wasting compute resources.

```sql
SET cz.optimizer.incremental.force.full.refresh = true;
REFRESH DYNAMIC TABLE my_dt;
SET cz.optimizer.incremental.force.full.refresh = false;
```

### `cz.optimizer.incremental.try.incremental.refresh.enabled`

- Type: bool, default: `false`

Tries incremental refresh first; if incremental plan generation fails (e.g., the SQL contains operators that do not support incremental), automatically falls back to full refresh instead of reporting an error.

**Applicable scenarios:**
- Just migrated a complex SQL to a DT and unsure whether all operators support incremental computation; want "incremental if possible, full if not"
- In production, want to ensure refresh tasks do not fail due to incremental plan generation failures

**Advantage:** Improves fault tolerance of DT refresh. Even if the SQL contains patterns not yet supported by the incremental engine, the refresh task will not fail — it automatically degrades to full refresh.

**Risk:** If incremental plan generation continuously fails, every refresh will silently fall back to full, and users may not know their DT is always running full refreshes, wasting compute resources. Monitoring logs is recommended to watch for frequent fallbacks.

```sql
-- Execute before the REFRESH statement
SET cz.optimizer.incremental.try.incremental.refresh.enabled = true;
REFRESH DYNAMIC TABLE my_dt;
```

---

## Source Table Data Characteristic Declarations

Declare source table data characteristics to guide the incremental engine toward more efficient computation strategies.

### `cz.optimizer.incremental.dimension.tables`

- Type: string, default: `""`

Marks specified source tables as dimension tables. Once marked, the incremental engine no longer reads change data from those tables; instead, it reads their latest full data directly at each refresh. Only changes in non-dimension tables (fact tables) drive incremental computation.

Format: comma- or colon-separated table names; supports full path `instanceId.ws.schema.table` or short names.

**This is a tradeoff of correctness for performance.** Once marked as a dimension table, any data changes (INSERT/UPDATE/DELETE) to that table will not trigger incremental computation, and already-output result rows will not be updated due to dimension table changes. In return, the incremental engine gains significant performance improvements:
- Skips scanning change data from dimension tables (no need to read change logs)
- Reduces the number of state tables (no state tables needed when one side of a JOIN is all dimension tables)
- Simplifies the incremental plan (only need to JOIN fact table change data with dimension table full data; no reverse computation needed)
- Reduces deduplication and merge operations on incremental data

**Applicable scenarios:**
- Fact table LEFT JOIN lookup/dictionary tables (e.g., region code table, product category table) where the lookup table rarely changes and its changes don't need to be tracked
- Large fact table JOIN small dimension table where the core goal is incremental performance on the fact table, and brief inconsistency after occasional dimension table changes is acceptable
- External tables (e.g., MySQL external tables) that don't support time travel and can't provide change data — marking as dimension table enables normal incremental computation
- T+1 dimension table + real-time fact table: dimension table updates in batch once per day; can be treated as unchanged between two updates

**Correctness impact:** After a dimension table changes, already-output results will not be automatically updated. For example, if a row's `name` changes from `'A'` to `'B'` in the dimension table, historical results that already JOINed that row will still show `'A'`. Only new fact table increments will JOIN to the latest `'B'`. If historical data correction is needed, a full refresh must be manually executed.

For detailed correctness impact analysis and behavior under each JOIN type, see the Dimension Table JOIN Guide (dimension-table-join-guide).

```sql
-- Recommended: declare via DT table properties (follows DT definition; no need to set before each REFRESH)
CREATE DYNAMIC TABLE my_dt
TBLPROPERTIES('mv_const_tables' = 'dim_product,dim_region')
AS SELECT ...;

-- Or via Session configuration (set before REFRESH statement)
SET cz.optimizer.incremental.dimension.tables = 'dim_product,dim_region';
REFRESH DYNAMIC TABLE my_dt;

-- After an important dimension table change, manually trigger a full refresh to correct data
SET cz.optimizer.incremental.force.full.refresh = true;
REFRESH DYNAMIC TABLE my_dt;
SET cz.optimizer.incremental.force.full.refresh = false;
```

### `cz.optimizer.incremental.append.only.tables`

- Type: string, default: `""`

Marks specified source tables as "expected append-only". This is an optimization hint telling the optimizer that the table is expected to have INSERT operations only, allowing the optimizer to choose a more efficient incremental plan (e.g., creating intermediate state optimized for append-only scenarios in advance).

**This does not affect correctness.** Even if a table marked as append-only later has actual UPDATE or DELETE operations, the incremental engine will still correctly capture and compute those changes — results will not be wrong. The difference is: when actual UPDATE/DELETE occurs, the plan the optimizer chose based on the "append-only" assumption may not be optimal, and performance may be worse than if the table were not marked.

**Applicable scenarios:**
- Kafka consumer landing tables, log tables, event tracking tables, and other data sources that have INSERT operations the vast majority of the time
- Source tables that may occasionally have a small number of UPDATE/DELETE operations (e.g., data corrections), but whose primary write pattern is INSERT

**Advantage:** The optimizer can choose a more efficient incremental plan based on the "append-only" assumption, reducing unnecessary intermediate state maintenance overhead. For aggregation scenarios, it can directly accumulate without maintaining complete intermediate state. Performance improvement is significant, especially in complex SQL with JOINs and aggregations.

**Risk:** If the table actually has frequent UPDATE/DELETE operations, the plan chosen by the optimizer based on the "append-only" assumption may not be optimal, and incremental refresh performance may be worse than without the marking. However, result correctness is not affected.

```sql
-- Recommended: declare via table properties (permanent; no need to set before each refresh)
ALTER TABLE event_log SET PROPERTIES('INCR_APPEND_ONLY_TABLE' = 'true');

-- Or via Session configuration (set before REFRESH statement)
SET cz.optimizer.incremental.append.only.tables = 'event_log,click_stream';
REFRESH DYNAMIC TABLE my_dt;
```

---

## Full Refresh Fallback Strategy

Automatically switches from incremental to full refresh when source table change volume is too large or specific tables change.

### `cz.optimizer.incremental.full.refresh.if.these.tables.change`

- Type: string, default: `""`

Comma-separated list of table names. When any table in the list has data changes during the current refresh cycle, a full refresh is automatically triggered.

**Applicable scenarios:**
- The DT's SQL JOINs a critical dimension table (e.g., a price table or exchange rate table) where any change requires all historical data to be recomputed with the new values
- Difference from `cz.optimizer.incremental.dimension.tables`: `dimension.tables` ignores changes and continues incremental; this config detects changes and triggers full recomputation

**Advantage:** Guarantees correctness after critical table changes — once a change is detected, full recomputation is automatic without manual intervention.

**Risk:** If the specified tables change frequently (e.g., updated every hour), every refresh will trigger a full refresh, completely losing the performance advantage of incremental. Should only be used for tables with very low change frequency but large impact scope.

```sql
-- Execute before the REFRESH statement
SET cz.optimizer.incremental.full.refresh.if.these.tables.change = 'dim_pricing,dim_exchange_rate';
REFRESH DYNAMIC TABLE my_dt;
```

### `cz.optimizer.incremental.full.refresh.if.source.table.changes.significantly`

- Type: bool, default: `false`

When enabled, automatically switches to full refresh when the ratio of incremental data volume to total data volume in the source table exceeds a threshold.

**Applicable scenarios:**
- Source table occasionally has large batch data imports (e.g., historical data backfill), where incremental data volume approaches or exceeds full volume, making incremental refresh actually slower than full
- Want the system to automatically judge "is incremental worth it?" and automatically switch to full when it's not

**Advantage:** Automatically selects the optimal strategy between incremental and full, avoiding the problem where incremental refresh is actually slower when incremental data volume is too large (incremental has additional overhead for change data computation, deduplication merging, state table read/write, etc.).

**Risk:** Threshold judgment is based on statistics and may not be fully accurate. If statistics are imprecise, unnecessary full refreshes may occur, or a switch to full may not happen when it should.

Requires `cz.optimizer.incremental.threshold.of.source.table.change.for.full.refresh` to set the threshold.

### `cz.optimizer.incremental.threshold.of.source.table.change.for.full.refresh`

- Type: double, default: `1.0`

The change ratio threshold that triggers a full refresh. When incremental data volume / total data volume exceeds this value, a full refresh is triggered.

- `1.0`: triggers only when incremental data exceeds total (very conservative)
- `0.5`: triggers when incremental exceeds half of total
- `0.1`: triggers when incremental exceeds 10% of total (aggressive; suitable for complex SQL with high incremental computation overhead)

```sql
-- Execute before the REFRESH statement
SET cz.optimizer.incremental.full.refresh.if.source.table.changes.significantly = true;
SET cz.optimizer.incremental.threshold.of.source.table.change.for.full.refresh = 0.5;
REFRESH DYNAMIC TABLE my_dt;
```

---

## State Table Management

State tables are internal tables automatically created by the incremental engine during refresh to store intermediate computation results (e.g., intermediate aggregation state, historical JOIN data, etc.) to accelerate subsequent incremental refreshes.

### `cz.optimizer.incremental.enable.state.table`

- Type: bool, default: `true`

Master switch for state tables. The system defaults to a limit of 5 state tables per DT to prevent excessive state tables from causing excessive disk storage in extreme scenarios. When the DT's SQL contains more than 5 stateful computation operators (e.g., aggregation, JOIN, window functions), if the user has not explicitly enabled this config, the system will **abandon creating all state tables**, and incremental refresh degrades to recomputing intermediate results from source tables each time.

If the user wants to create state tables for these operators to get better incremental refresh performance, this config must be explicitly set to `true`. **Explicitly enabling this config means the user understands and accepts the tradeoff of additional disk storage for better incremental refresh performance.**

When set to `false`, the incremental engine does not create or reuse any state tables; all intermediate results are recomputed from source tables each time.

**Applicable scenarios:**

Set to `true` (explicitly enable):
- The DT's SQL contains many stateful operators (e.g., multi-level JOIN + aggregation + window functions), and the default 5 state table limit is insufficient to cover all operators; want to create more state tables for optimal incremental performance
- User has evaluated storage overhead and confirmed the additional state table storage is acceptable

Set to `false` (disable):
- Troubleshooting state table related issues (e.g., suspecting state table data inconsistency is causing incremental result anomalies)
- Source table data volume is small; the cost of full recomputation is acceptable; state tables are not needed for acceleration
- Need to strictly control storage overhead; don't want the system to automatically create additional tables

**Advantage:** When explicitly enabled, the system can create state tables for all stateful operators, maximizing incremental refresh performance gains. When disabled, all storage overhead from state tables is eliminated.

**Risk:** When explicitly enabled, the number of state tables may exceed the default limit of 5, bringing additional disk storage overhead. When disabled, complex DTs with aggregation or multi-table JOINs need to read full data from source tables to recompute intermediate results on every incremental refresh, which may significantly degrade performance.

```sql
-- Explicitly enable: allow the system to create state tables for all stateful operators (execute before REFRESH)
SET cz.optimizer.incremental.enable.state.table = true;
REFRESH DYNAMIC TABLE my_dt;

-- Disable: do not create or reuse any state tables
SET cz.optimizer.incremental.enable.state.table = false;
REFRESH DYNAMIC TABLE my_dt;
```

### `cz.optimizer.incremental.state.table.lifecycle`

- Type: string, default: `"3"`

Number of days to retain state table data. Historical version data older than this number of days will be automatically cleaned up.

**Applicable scenarios:**
- The DT's refresh interval is long (e.g., once per week), and the default 3 days will cause state tables to be cleaned up between two refreshes, making them unusable for the next refresh and degrading to full refresh. In this case, increase this value.
- Want to reduce state table storage overhead; can shorten the retention period appropriately (but not shorter than the refresh interval)
- State table content is very large; want to reclaim storage space promptly; can explicitly shorten the lifecycle (e.g., set to 1 day) to let expired versions be cleaned up sooner

**Advantage:** Increasing the retention period ensures state tables are not cleaned up within the refresh interval, guaranteeing incremental refresh can normally reuse state.

**Risk:** The longer the retention period, the more storage space state tables occupy. Each version of a state table is retained until expiry; if refresh frequency is high (e.g., hourly) and retention period is long (e.g., 30 days), state table storage can be very substantial.

```sql
-- Execute before the REFRESH statement
SET cz.optimizer.incremental.state.table.lifecycle = '10';
REFRESH DYNAMIC TABLE my_dt;
```

### `cz.optimizer.incremental.rebuild.rule.based.state.table`

- Type: bool, default: `false`

When set to `true`, rebuilds all state tables on the next refresh. The rebuild process clears old state table data and regenerates it based on current source table data.

**Applicable scenarios:**
- State table data is corrupted (e.g., incomplete state table writes due to system anomalies), causing incremental refresh result anomalies
- The DT's SQL has changed (e.g., aggregation logic was modified), and the old state table schema doesn't match the new SQL
- Incremental refresh keeps reporting errors; suspecting a state table issue; want to rebuild from scratch

**Advantage:** After rebuilding, state table data is fully consistent with the current source table, eliminating historical accumulated data inconsistencies.

**Risk:** The rebuild process causes that refresh to use full mode, which takes longer. Incremental refresh is unavailable until the rebuild is complete.

**Note:** This is a one-time switch. After the rebuild is complete, it must be reset to `false`; otherwise every refresh will rebuild state tables, completely defeating the purpose of incremental.

```sql
SET cz.optimizer.incremental.rebuild.rule.based.state.table = true;
REFRESH DYNAMIC TABLE my_dt;
SET cz.optimizer.incremental.rebuild.rule.based.state.table = false;
```

### `cz.optimizer.incremental.state.table.specified.schema`

- Type: string, default: `""`

Specifies the Schema where state tables are stored. By default, state tables are in the same Schema as the DT target table.

**Applicable scenarios:**
- Want to isolate state tables from business tables for unified management and monitoring of state table storage overhead
- Multiple DTs share the same Schema for state tables, making batch cleanup easier

**Advantage:** After separating business tables and state tables, Schema-level permissions, quotas, and lifecycle policies can be set independently, preventing state tables from interfering with business table management.

**Risk:** Cross-Schema access may bring slight metadata query overhead. Additionally, if the specified Schema does not exist or permissions are insufficient, state table creation will fail.

```sql
SET cz.optimizer.incremental.state.table.specified.schema = 'incr_state';
```

---

## DT Definition Changes

Controls compatibility check behavior when executing `CREATE OR REPLACE DYNAMIC TABLE`.

### `cz.sql.mv.check.before.replacing.sql`

- Type: bool, default: `true`

Controls whether a compatibility check is performed on the old and new SQL when executing `CREATE OR REPLACE DYNAMIC TABLE`.

**Check enabled (`true`, default):** The system compares the column structure of the old and new SQL to determine compatibility. If judged compatible (e.g., only adding columns), the system retains existing incremental state and continues incremental refresh afterward. However, compatibility judgment is not perfect — for changes judged as "compatible", newly added columns will be filled with NULL in historical data, and existing historical rows will not be recomputed according to the new SQL, which may cause inconsistency between old and new data.

**Check disabled (`false`):** The system skips the compatibility check and directly treats the old and new SQL as incompatible, resetting incremental state (clearing state tables and historical version information). The next refresh after replacement will execute full computation, ensuring all data is regenerated according to the new SQL.

**Applicable scenarios:**

Set to `false` (disable check):
1. **`CREATE OR REPLACE` is stuck or reports an error**: In some cases, the compatibility check itself may take a long time or report an error due to metadata issues, preventing `CREATE OR REPLACE` from completing. Disabling the check skips this step and allows the replacement to complete smoothly. The tradeoff is that the next refresh will be a full refresh.
2. **SQL has undergone substantive changes and a full recomputation is desired**: E.g., JOIN logic or aggregation method was modified. Disabling the check ensures the system doesn't incorrectly judge it as "compatible" and retain old incremental state.

Keep `true` (enable check, default):
1. **Simple changes like adding columns only**: Want the system to automatically judge compatibility; retain incremental state when compatible to avoid full refresh. Suitable for scenarios where NULL in new columns for historical data is acceptable.
2. **Frequent DT definition adjustments during daily iteration**: Rely on automatic system judgment to reduce unnecessary full refreshes.

**Risk of enabling check:** Compatibility judgment may classify actually incompatible changes as "compatible", causing new columns to be NULL in historical data, or existing historical rows to never be updated according to the new SQL.

**Risk of disabling check:** The next refresh will execute full computation, which may take a long time for DTs with large data volumes.

```sql
-- Disable check to ensure full recomputation after replacement
SET cz.sql.mv.check.before.replacing.sql = false;
CREATE OR REPLACE DYNAMIC TABLE my_dt AS SELECT ...;
SET cz.sql.mv.check.before.replacing.sql = true;
-- Note: the next REFRESH will execute a full refresh
```

---

## Historical Partition Backfill

### `cz.optimizer.incremental.backfill.enabled`

- Type: bool, default: `false`

Enables backfill mode. Used to backfill or correct data in historical partitions of a DT. When enabled, the system automatically performs the following:
- Forces the current refresh to use full mode (equivalent to enabling `force.full.refresh`)
- Skips reading incremental data to avoid reading large amounts of historical change logs
- For partitioned DTs, disables state table creation and matching (backfilled partitions don't need incremental state)
- Allows DML operations on the DT (e.g., `INSERT OVERWRITE`)

**Applicable scenarios:**

Set to `true` (enable backfill):
1. **Historical partition data correction**: A historical partition's data has issues and needs to be regenerated from correct source data.
2. **Supplement historical data after creating a new DT**: After a DT is created, historical partitions need to have data generated one by one.
3. **Recompute after source table data backfill**: The source table had historical data backfilled; affected partitions need to be recomputed.

**Notes:**
- Backfill mode is a one-time operation; after backfill is complete, reset to `false`; otherwise every subsequent refresh will use full mode.
- Backfill mode does not create or update state tables, so it does not affect subsequent normal incremental refresh state.
- Backfill is typically used with `INSERT OVERWRITE` to overwrite existing data in the target partition.

```sql
-- Backfill a specified historical partition (execute before REFRESH statement)
SET cz.optimizer.incremental.backfill.enabled = true;
SET dt.args.ds = '2025-01-01';
REFRESH DYNAMIC TABLE my_dt PARTITION(ds = '2025-01-01');
SET cz.optimizer.incremental.backfill.enabled = false;

-- Can also backfill directly via INSERT OVERWRITE
SET cz.optimizer.incremental.backfill.enabled = true;
INSERT OVERWRITE TABLE my_dt
SELECT id, amount, '2025-01-01' AS ds
FROM source_table
WHERE ds = '2025-01-01';
SET cz.optimizer.incremental.backfill.enabled = false;
```

---

## Write Behavior for Partitioned Tables During Full Refresh

### `cz.optimizer.incremental.full.refresh.overwrite.partitioned.table`

- Type: bool, default: `true`

Controls the write mode for partitioned DTs during full refresh.

**Background:** For partitioned tables, full refresh (`force.full.refresh = true` or system-triggered full refresh) defaults to overwrite (OVERWRITE) mode — this is standard behavior in big data: full recomputation results overwrite all partitions of the target table. However, in some scenarios, the DT's SQL only computes data for some partitions (e.g., only the last 7 days), and the full refresh result also only includes those partitions. In this case, using overwrite would cause historical partitions (e.g., data older than 7 days) to be cleared.

**Overwrite enabled (`true`, default):** During full refresh, all partitions of the target table are overwritten. Partitions not included in the refresh result will be cleared. This is suitable for scenarios where the DT's SQL covers the entire data range of the target table.

**Overwrite disabled (`false`):** During full refresh, only the partition data produced by the current computation is written; other existing partitions in the target table are not affected. Historical partition data remains unchanged.

**Applicable scenarios:**

Set to `false` (disable overwrite):
1. **DT's SQL only computes some partitions**: E.g., the SQL has a `WHERE ds >= '2025-01-01'` filter condition and only computes recent data. Don't want to clear earlier historical partitions during full refresh.
2. **DT that accumulates data partition by partition**: Each refresh only produces data for the current partition; historical partitions were produced by previous refreshes. Full refresh should only recompute the current partition without affecting historical partitions.
3. **Sliding window scenarios**: The DT's SQL computes data within a time window based on partition parameters; full refresh only recomputes partitions within the window.

Keep `true` (enable overwrite, default):
1. **DT's SQL covers all data**: SQL has no partition filter conditions; full refresh result includes all data in the target table.
2. **Need to fully rebuild the target table**: Want the target table data after full refresh to be completely consistent with directly executing the SQL, without retaining any historical residuals.

**Risks:**
- With overwrite enabled, if the DT's SQL only computes some partitions, full refresh will clear historical partitions not covered by the computation, causing data loss.
- With overwrite disabled, if the DT's SQL covers all data, old data may remain in the target table after full refresh (because old partitions were not cleared), causing data inconsistency.

```sql
-- Disable overwrite: retain historical partitions during full refresh (execute before REFRESH statement)
SET cz.optimizer.incremental.full.refresh.overwrite.partitioned.table = false;
SET cz.optimizer.incremental.force.full.refresh = true;
REFRESH DYNAMIC TABLE my_dt;
SET cz.optimizer.incremental.force.full.refresh = false;
```

---

## Configuration Quick Reference

Quickly locate the required configuration by use case:

| Scenario | Configuration | Recommended value |
|------|--------|--------|
| Data anomaly; need full recomputation for repair | `cz.optimizer.incremental.force.full.refresh` | `true` (one-time) |
| Unsure if SQL supports incremental | `cz.optimizer.incremental.try.incremental.refresh.enabled` | `true` |
| Small table JOIN; no need to track changes | `cz.optimizer.incremental.dimension.tables` or table property `mv_const_tables` | Table name list |
| Source table is mainly INSERT; want to optimize incremental performance | `cz.optimizer.incremental.append.only.tables` or table property `INCR_APPEND_ONLY_TABLE` | Table name list / `true` |
| Must do full recomputation when critical table changes | `cz.optimizer.incremental.full.refresh.if.these.tables.change` | Table name list |
| Auto-switch to full when incremental data volume is too large | `cz.optimizer.incremental.full.refresh.if.source.table.changes.significantly` + `threshold` | `true` + `0.5` |
| Many SQL operators; need more state tables for acceleration | `cz.optimizer.incremental.enable.state.table` | `true` (explicitly enable) |
| No state tables needed, or troubleshooting state table issues | `cz.optimizer.incremental.enable.state.table` | `false` |
| State table data corrupted; need to rebuild | `cz.optimizer.incremental.rebuild.rule.based.state.table` | `true` (one-time) |
| Long refresh interval; state tables cleaned up prematurely | `cz.optimizer.incremental.state.table.lifecycle` | Increase to cover refresh interval |
| Isolate state tables from business tables | `cz.optimizer.incremental.state.table.specified.schema` | Schema name |
| `CREATE OR REPLACE` is stuck or SQL has substantive changes | `cz.sql.mv.check.before.replacing.sql` | `false` (one-time) |
| Historical partition data backfill or correction | `cz.optimizer.incremental.backfill.enabled` | `true` (one-time) |
| Retain historical partition data during full refresh | `cz.optimizer.incremental.full.refresh.overwrite.partitioned.table` | `false` |
