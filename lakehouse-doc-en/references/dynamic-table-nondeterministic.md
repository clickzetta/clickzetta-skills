# Nondeterministic Functions in Dynamic Tables

You can use nondeterministic functions such as `CURRENT_TIMESTAMP()`, `RAND()`, `UUID()`, and `CURRENT_DATE()` in a Dynamic Table definition. Creation and refresh will not fail, and these functions will not cause the refresh to fall back to full. The problem is not performance — it is the result: they cause **values to be inconsistent across rows in the same table**, and the root cause is the incremental computation mechanism of Dynamic Tables.

## Why Values Become Inconsistent Across Rows

Incremental computation only re-executes the SQL for **rows that changed**; unchanged rows retain their result from the previous computation. Therefore:

- A row inserted today has its nondeterministic function evaluated during this refresh, producing today's value.
- A row written last week with no changes since then had its nondeterministic function evaluated last week; that result is retained.

In the same Dynamic Table, different rows' function values come from executions at different moments, splitting the data across rows.

## Behavior of Each Function

Actual behavior during an incremental refresh:

| Function | Refresh with no upstream changes | Refresh with changed rows (INSERT/UPDATE) | Specific problem |
|------|-------------|------------------------|---------|
| `CURRENT_TIMESTAMP()` | All row values unchanged | Changed rows update to the current refresh timestamp; unchanged rows keep the original timestamp | Timestamps differ across rows in the same table; cannot represent a single unified refresh time |
| `CURRENT_DATE()` | All row values unchanged | Changed rows update to today's date; unchanged rows keep the date from when they were written | After a day boundary, dates split across rows |
| `RAND()` | All row values unchanged | Changed rows get a new random value; unchanged rows keep the old value | Values in the same column come from different executions at different times; cannot be reproduced |
| `UUID()` | All row values unchanged | Changed rows get a new UUID; unchanged rows keep the old UUID | A logically same row changes its UUID after an UPDATE, breaking row identity semantics |

**DELETE behavior is unaffected**: rows deleted from the source table are also deleted from the Dynamic Table, with no interaction with nondeterministic functions.

## Example: Row Inconsistency Caused by CURRENT_TIMESTAMP()

Initial state (first refresh — all three rows written at the same time):

```
id | val | refresh_ts
1  | 100 | 2026-06-01 08:00:00  <- written on first refresh
2  | 200 | 2026-06-01 08:00:00
3  | 300 | 2026-06-01 08:00:00
```

One week later, the source row with id=2 has its val updated, triggering an incremental refresh:

```
id | val | refresh_ts
1  | 100 | 2026-06-01 08:00:00  <- unchanged; retains timestamp from a week ago
2  | 999 | 2026-06-08 09:30:00  <- changed row; timestamp updated to current refresh time
3  | 300 | 2026-06-01 08:00:00  <- unchanged; retains timestamp from a week ago
```

`refresh_ts` can no longer represent "when this table was last refreshed" and cannot be used to filter data by refresh batch.

## A Full Refresh Resets the Entire Column

The row inconsistency above is not even stable. Dynamic Tables fall back to a full refresh under certain conditions (the first refresh after table creation, an excessively large single-batch change, certain operator combinations, etc.). A full refresh recomputes the entire table, so this column is **reset uniformly to the timestamp of that full execution**. Subsequent incremental refreshes then cause it to split again. The column ends up neither consistent nor stable, and cannot be reproduced across refreshes — this is the fundamental reason not to write nondeterministic functions into a Dynamic Table definition. For how to tell whether a refresh was incremental or full, see [Viewing Dynamic Table Refresh Mode](dynamic-table-incre.md).

> ⚠️ **Note**: Writing nondeterministic functions into a Dynamic Table definition does not cause an error, but results are not reproducible. When you need timestamps, random values, or unique identifiers, use the alternatives below and handle them outside the Dynamic Table.

## Alternatives

**For time-based filtering**: use a parameterized Dynamic Table and pass the date parameter via `SESSION_CONFIGS()['dt.args.bizdate']` instead of relying on `CURRENT_DATE()`. See [Dynamic Table Parameterized Definitions](dynamic-table-parameters.md).

**For recording the refresh time**: add the timestamp in the downstream query using `CURRENT_TIMESTAMP()` — do not write it into the Dynamic Table definition. For example:

```sql
-- Don't do this (inside the Dynamic Table definition)
CREATE DYNAMIC TABLE dws_report ... AS
SELECT id, val, CURRENT_TIMESTAMP() AS refresh_ts FROM ods_source;

-- Do this instead (when querying the Dynamic Table)
SELECT id, val, CURRENT_TIMESTAMP() AS query_ts
FROM dws_report;
```

**For unique row identifiers**: use the business primary key from the source table rather than `UUID()`, ensuring the row identifier remains stable across refreshes.

## Related Documentation

- [Viewing Dynamic Table Refresh Mode](dynamic-table-incre.md) — how to tell whether a refresh was incremental or full
- [Dynamic Table Parameterized Definitions](dynamic-table-parameters.md) — the correct way to filter by time
- [Dynamic Table](om-dynamic-table.md) — full usage limitations
