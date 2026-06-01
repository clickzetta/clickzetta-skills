# Non-partitioned Table + Continuous Writes: DT Risk Alert and MERGE INTO Alternative

## Trigger Conditions

When the DT the user is about to create simultaneously meets all of the following conditions, **an alert must be issued to the user**:

1. The DT itself is a non-partitioned table (no `PARTITIONED BY` and no `SESSION_CONFIGS()` references)
2. The source table is also a non-partitioned table with continuous writes (e.g., a Kafka consumer landing table, a CDC detail table)
3. The SQL contains a window function deduplication pattern by primary key: `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) WHERE rn = 1`

## Alert Content

Explain the following three risks to the user:

### Risk 1: Unbounded Storage Growth

Non-partitioned DTs and non-partitioned source tables both lack automatic data lifecycle management (`data_lifecycle` only works for partitioned tables). As data continues to be written:
- Source table data grows without bound
- DT state tables are maintained globally and grow linearly with data volume
- Target table data grows in sync
- All three combined result in continuously rising and uncontrollable storage costs

### Risk 2: Source Table Archiving Causes Performance Disaster

When storage grows to a certain point, operations teams typically archive the source table — migrating historical data to cold storage or an archive table, then deleting it from the source table to free space. At this point:

- The DT captures the source table's delete events and reflects them in incremental computation results
- The `ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) WHERE rn = 1` delete handling cost is extremely high:
  - Window functions cannot handle deletes incrementally — they need to re-read all historical data for that key and re-sort
  - Non-partitioned tables have no partition boundaries to limit the re-read scope; may need to scan the entire table
  - Large-scale archiving produces massive delete changes; each key needs to be independently recomputed
- A single source table archiving operation can cause DT REFRESH duration to spike from seconds to hours, or even fail

### Risk 3: Cannot Filter Archive-generated Delete Events

The DT's incremental engine automatically captures all changes to the source table (INSERT / UPDATE / DELETE); users cannot intervene in this process. `WHERE op <> 'DELETE'` in the SQL filters business-level delete markers, not physical deletes from the source table. Users have no way to tell the DT "these deletes are archiving operations; please ignore them."

## Recommended Alternative

Suggest the user use MERGE INTO + Table Stream instead:

```sql
-- Step 1: Enable change tracking on source table
ALTER TABLE source_table SET PROPERTIES ('change_tracking' = 'true');

-- Step 2: Create Table Stream
CREATE TABLE STREAM source_stream ON TABLE source_table
WITH (TABLE_STREAM_MODE = 'STANDARD', SHOW_INITIAL_ROWS = TRUE);

-- Step 3: Create target table
CREATE TABLE target_table (
    id BIGINT,
    col1 STRING,
    col2 INT,
    event_time TIMESTAMP
);

-- Step 4: Scheduled MERGE INTO to consume Stream
MERGE INTO target_table t
USING (
    SELECT id, col1, col2, event_time,
        CASE WHEN `value` IS NULL OR `value` = '' THEN 'DELETE' ELSE 'UPSERT' END AS op
    FROM source_stream
) s ON t.id = s.id
WHEN MATCHED AND s.op = 'UPSERT' THEN UPDATE SET
    t.col1 = s.col1, t.col2 = s.col2, t.event_time = s.event_time
WHEN NOT MATCHED AND s.op = 'UPSERT' THEN INSERT
    (id, col1, col2, event_time) VALUES (s.id, s.col1, s.col2, s.event_time);
```

Advantages of MERGE INTO + Table Stream:
- **Each computation is independent**: only consumes incremental data from the Stream; does not depend on the source table's full state
- **Archive-immune**: when the source table is archived, archive-generated delete events can be filtered via WHERE conditions in the USING subquery
- **Independent target table management**: the target table's lifecycle is decoupled from the source table; independent archiving strategies can be set
- **Offset auto-advances**: after MERGE INTO consumes the Stream, the offset automatically advances; only new changes are processed next time

## Alert Message Template

When the user's DT is detected to meet the trigger conditions, use the following message:

> ⚠️ **Risk Warning**: You are creating a non-partitioned Dynamic Table, and the source table is also a non-partitioned table with continuous writes. This combination has the following long-term operational risks:
>
> 1. **Unbounded storage growth**: the source table, DT target table, and DT state tables will all grow continuously and cannot be automatically cleaned up via `data_lifecycle`
> 2. **Source table archiving will cause a performance disaster**: when you need to archive the source table (migrate historical data then delete), the DT will capture these delete events. Because the SQL contains `ROW_NUMBER() ... WHERE rn = 1` deduplication logic, each deleted key needs to re-read historical data and re-sort; non-partitioned tables have no boundary limits, which may cause serious REFRESH performance regression
> 3. **Cannot filter archive deletes**: the DT incremental engine automatically captures all source table changes; you cannot tell the DT to ignore deletes generated by archiving operations
>
> **Recommendation**: For this type of "merge non-partitioned CDC detail table into result table" scenario, the MERGE INTO + Table Stream approach is recommended. Each run only consumes incremental data; archive-generated delete events can be filtered via WHERE conditions, without affecting downstream.

## Detection Logic

When helping users create a DT, check in the following order:

1. Does the DT have `PARTITIONED BY` or `SESSION_CONFIGS()`? → If yes, do not trigger alert
2. Is the source table a non-partitioned table with continuous writes (e.g., Kafka consumer table, CDC detail table)? → If not, do not trigger alert
3. Does the SQL contain the `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ... DESC) WHERE rn = 1` pattern? → If yes, highest risk; must alert
4. Even without ROW_NUMBER, if conditions 1+2 are met, remind the user of the storage growth risk
