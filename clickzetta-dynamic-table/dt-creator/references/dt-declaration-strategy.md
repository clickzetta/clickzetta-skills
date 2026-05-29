# Dynamic Table Declaration Strategy

DT has two creation syntaxes: static partition DT and dynamic partition DT (non-partitioned DT can be viewed as a special case of dynamic partition). The two differ fundamentally in creation syntax, refresh behavior, and incremental behavior.

## Core Concepts

### Static Partition DT (Partitioned DT with SESSION_CONFIGS args)

The SQL references partition parameters via `SESSION_CONFIGS()`, and a specific partition value is specified at each REFRESH. Each partition refreshes independently — each partition refresh unit can be viewed as an independent DT.

```sql
CREATE DYNAMIC TABLE order_daily (
    id BIGINT, amount DECIMAL(12,2), ds STRING
)
PARTITIONED BY (ds)
AS
SELECT id, amount, SESSION_CONFIGS()['dt.args.ds'] AS ds
FROM orders
WHERE ds = SESSION_CONFIGS()['dt.args.ds'];

-- Specify partition at refresh time
set dt.args.ds=2025-01-01
REFRESH DYNAMIC TABLE order_daily PARTITION(ds = '2025-01-01');
```

### Dynamic Partition DT (Non-partitioned DT / DT without args)

The SQL does not reference `SESSION_CONFIGS()`, or although partitioned, the partition values are dynamically produced by the query logic. Each REFRESH processes all incremental data from all source tables.

Dynamic partition DTs do not allow any command other than REFRESH to modify data (INSERT/UPDATE/DELETE/MERGE are all unavailable); data is driven entirely by REFRESH.

Therefore, the following ETL scenarios are not suitable for dynamic partition DT:
- Need to manually patch data (e.g., a few rows are found to be incorrect and need to be directly UPDATEd)
- Need to delete data by condition (e.g., cleaning dirty data, deleting expired records)
- Need MERGE INTO for upsert (e.g., consuming a stream and merging into a target table in a CDC scenario)
- Need INSERT INTO to append external data (e.g., manually importing a batch of supplementary data)
- Need to backfill or re-refresh partitions independently (dynamic partition DT can only do a full table refresh; individual partitions cannot be refreshed separately)
- Downstream tasks need to write to the same table (DT has exclusive write ownership)

```sql
CREATE DYNAMIC TABLE order_summary (
    category STRING, total_amount DECIMAL(12,2)
)
AS
SELECT category, SUM(amount) AS total_amount
FROM orders
GROUP BY category;

-- No partition specified at refresh time
REFRESH DYNAMIC TABLE order_summary;
```

## Key Differences

| Dimension | Static Partition DT | Dynamic Partition DT |
|------|-----------|-----------|
| Does SQL contain `SESSION_CONFIGS()`? | Yes, used to reference partition parameters | No |
| REFRESH syntax | `REFRESH ... PARTITION(ds='xxx')` | `REFRESH ...` (no PARTITION) |
| Incremental scope | Only processes incremental data for the specified partition | Processes all incremental data from all source tables |
| Scheduling method | External scheduler triggers one partition at a time | External scheduler triggers on a timer |
| Data lifecycle | Managed per partition; can backfill/delete independently | Managed as a whole table |
| State tables | Maintained independently per partition | Maintained globally |
| Suitable data patterns | T+1 batch processing, time-partitioned ETL | Real-time streams, global aggregation, no clear partition key |

## Selection Decision Tree

```
Does your data have a clear time/business partition key?
│
├─ Yes → Was the original ETL doing INSERT OVERWRITE by partition?
│       │
│       ├─ Yes → Use static partition DT
│       │       (maintain the original partition granularity; each partition refreshes independently)
│       │
│       └─ No → Is the data volume large? Do you need per-partition lifecycle management?
│               │
│               ├─ Yes → Use static partition DT
│               │       (even if the original was not partitioned, adding partitions is recommended for manageability)
│               │
│               └─ No → Use dynamic partition DT
│                       (simple scenario; no partition management needed)
│
└─ No → Use dynamic partition DT
        (global aggregation, real-time summary, etc.)
```

## Static Partition DT — Details

### Applicable Scenarios

1. **T+1 batch ETL migration**
   - Original SQL follows the `INSERT OVERWRITE TABLE t PARTITION(ds='${ds}')` pattern
   - Refreshes once per day/hour by partition
   - Needs to support historical partition backfill

2. **Sliding window computation**
   - E.g., aggregation over the last 7 days, period-over-period comparison
   - SQL references `SESSION_CONFIGS()['dt.args.ds']` and `sub_days(...)` for window range

3. **Per-partition data lifecycle management**
   - Automatically clean up expired partitions via `data_lifecycle`
   - Can backfill a single partition without affecting others

4. **Self-referencing DT (daily comparison, SCD)**
   - Current partition depends on the result of the previous partition
   - Must use static partition, because "current partition" and "previous partition" need to be explicitly specified

### Refresh Method

```sql
-- Refresh one partition at a time
set dt.args.ds=2025-01-15
REFRESH DYNAMIC TABLE my_dt PARTITION(ds = '2025-01-15');

-- Multi-level partition
set dt.args.pt=20250411
set dt.args.pt_hour=01
REFRESH DYNAMIC TABLE my_dt PARTITION(pt = '20250411', pt_hour = '01');
```

### Notes

- Use `cz.optimizer.incremental.backfill.enabled=TRUE` for backfill; it will automatically use full refresh
- Partition parameters are passed via `set dt.args.xxx=value`; the PARTITION clause in the REFRESH statement specifies the partition value

## Dynamic Partition DT — Details

### Applicable Scenarios

1. **Real-time stream data aggregation**
   - Source table continuously writes; DT refreshes on a schedule
   - No partition management needed; each refresh processes all new data

2. **Global summary tables**
   - E.g., global TopN, global count, global deduplication
   - No clear partition key

3. **Simple JOIN + filter**
   - Simple transformations without partition parameters
   - E.g., fact table JOIN dimension table, output wide table

4. **Multi-source merge (UNION ALL)**
   - Data from multiple source tables merged into one table
   - No partition management needed

### Refresh Method

```sql
-- Refresh directly; processes all incremental data from all source tables
REFRESH DYNAMIC TABLE my_dt;
```

### Notes

- Each refresh processes all incremental data from all source tables; if source table change volume is large, refresh may be slow
- State tables are maintained globally and may grow as data volume increases
- Per-partition backfill is not supported; only full table refresh is possible
- Suitable for scenarios where the change ratio is small (< 5%)

## Partition Granularity Selection

When choosing a static partition DT, you also need to decide on partition granularity:

| Data pattern | Recommended granularity | Notes |
|---------|------------|------|
| Strictly ordered time series (e.g., logs) | Minute-level (`dt_min`) | High data volume, frequent writes |
| Roughly ordered, small amount of late data | Hour-level (`dt_hour`) | Balance between granularity and management complexity |
| T+1 batch import | Day-level (`ds`) | Most common ETL scenario |
| By business cycle | Weekly/monthly | Reporting scenarios |
| Multi-level partition | Day + hour (`ds`, `hour`) | Finer-grained lifecycle management needed |

Selection principles:
- Finer granularity → smaller data volume per refresh → higher incremental efficiency
- Finer granularity → more partitions → more complex management and scheduling
- Granularity should match the data write frequency: if data is written hourly, partition granularity should not be finer than hourly

## Determining Partition Strategy from Original ETL

| Original ETL pattern | Recommended DT partition strategy |
|--------------|----------------|
| `INSERT OVERWRITE TABLE t PARTITION(ds='${ds}')` | Static partition DT, day-level |
| `INSERT OVERWRITE TABLE t PARTITION(ds='${ds}', hour='${hour}')` | Static partition DT, day+hour level |
| `INSERT OVERWRITE TABLE t PARTITION(ds)` (dynamic partition write) | Dynamic partition DT or static partition DT (depends on whether per-partition management is needed) |
| `INSERT INTO TABLE t SELECT ...` (no partition) | Dynamic partition DT |
| `INSERT OVERWRITE TABLE t SELECT ...` (full table overwrite) | Dynamic partition DT |
