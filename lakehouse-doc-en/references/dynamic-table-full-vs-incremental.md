# Increasing the Incremental Refresh Ratio for Dynamic Tables

Seeing `FULL` for a `refresh_mode` in a refresh record is not cause for alarm. Each time a Dynamic Table refreshes, the engine **automatically chooses between incremental and full based on cost** — you cannot predict whether a refresh was incremental just by looking at the SQL operators you wrote. Use `refresh_mode` in the refresh history as the source of truth. This guide explains how to read the refresh mode, what causes a full refresh, and how to maximize incremental refreshes.

## Reading the Refresh Mode

Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to examine each refresh. Focus on three fields:

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = '<dynamic_table_name>' LIMIT 10;
```

- `refresh_mode`: how this refresh was executed.
  - `INCREMENTAL`: only the changed parts were processed.
  - `FULL`: the entire table was recomputed.
  - `NO_DATA`: no upstream changes were detected; nothing was computed this cycle. This is normal, not an error.
- `stats`: how many rows changed in an incremental refresh, for example `{"rows_deleted":"1","rows_inserted":"1"}`.
- `duration`: elapsed time for this refresh, useful for checking whether the refresh interval is long enough or whether tasks are accumulating.

See [Viewing Dynamic Table Refresh Mode](dynamic-table-incre.md) for the full field reference.

## Do Not Assume: These Patterns Still Refresh Incrementally

The most common mistake is concluding "I used a certain operator, so it must fall back to full." Many patterns assumed to "not support incremental" still run incrementally in practice.

Take `ORDER BY` as an example:

```sql
CREATE TABLE doc_fr_src (id INT, grp STRING, val INT);
INSERT INTO doc_fr_src VALUES (1,'A',10),(2,'A',20),(3,'B',30);

CREATE DYNAMIC TABLE doc_fr_ordered REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT AS
SELECT id, val FROM doc_fr_src ORDER BY val;
REFRESH DYNAMIC TABLE doc_fr_ordered;

-- Insert a row and refresh again
INSERT INTO doc_fr_src VALUES (4,'B',40);
REFRESH DYNAMIC TABLE doc_fr_ordered;

SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'doc_fr_ordered' LIMIT 2;
```

Both refreshes are incremental:

| Refresh | refresh_mode | stats |
| --- | --- | --- |
| First refresh after creation | `INCREMENTAL` | `{"rows_deleted":"0","rows_inserted":"3"}` |
| After inserting 1 row | `INCREMENTAL` | `{"rows_deleted":"0","rows_inserted":"1"}` |

`ORDER BY` did not cause a fallback to full. Similarly, window aggregation `SUM(...) OVER (PARTITION BY ...)`, retraction in aggregation (subtracting a refund from a total), and `ROW_NUMBER()` to get the latest per key (`rn = 1`) all run incrementally. The conclusion is simple: **do not guess from the operators — run a refresh and check `refresh_mode`.**

## What Causes a Full Refresh

Full refreshes have two distinct categories.

**1. The engine proactively chose full based on cost (the most common reason).** When the engine judges that "full is cheaper than incremental this time," it picks full. Typical situations: the data volume is very small (full is inherently cheap), a single change affects a large portion of the table, or patterns with higher incremental cost such as multi-table JOINs or wide tables. **This is not "incremental is unsupported" — it means "incremental is not worth it this time."**

One direct consequence: **on a few rows of test data you will easily see `FULL`; with production data volumes the same table runs incrementally.** For example, a two-table join wide table typically runs `FULL` on the first change after creation, then switches to `INCREMENTAL` for subsequent small changes. Do not use the refresh mode on a small dataset to predict production behavior.

**2. A recomputation triggered after a definition change.** After using `CREATE OR REPLACE` to change processing logic (modifying `SELECT`, adding computed columns, changing column types), the engine triggers one recomputation to align with the new definition. Once the definition stabilizes, subsequent refreshes run incrementally as normal.

> 💡 **Tip**: `NO_DATA` is not a full refresh — it means there were no upstream changes since the last refresh and no computation was needed. Frequent `NO_DATA` often means the refresh interval is shorter than the data change frequency; consider increasing the interval to reduce cost.

## How to Maximize Incremental Refreshes

- **Evaluate with real data volumes**: do not judge incremental behavior on a few rows of test data. With small data the engine proactively chooses full; seeing `FULL` there is expected.
- **Keep the definition stable**: frequent `CREATE OR REPLACE` definition changes trigger repeated recomputations. Finalize logic before releasing to production.
- **Control the fraction of data changed per batch**: loading data close to the full table size in one batch makes incremental not worthwhile and triggers a full refresh. Continuous, steady changes are the best fit for incremental.
- **Give the engine exploitable clustering**: ensure `JOIN key`, `GROUP key`, and partition keys can distinguish hot and cold data so the engine can touch only the relevant subset. See [Incremental Computing and Dynamic Tables](incremental-computing.md) for the underlying principles.
- **When in doubt, run it and check**: use `refresh_mode` as the source of truth, not operator intuition or outdated assumptions.

## Related Documentation

- [Viewing Dynamic Table Refresh Mode](dynamic-table-incre.md): full field reference for `SHOW DYNAMIC TABLE REFRESH HISTORY`
- [Incremental Computing and Dynamic Tables](incremental-computing.md): incremental principles and per-operator incremental behavior
- [Dynamic Table Design: From Processing Goals to Incremental Pipelines](dynamic-table-design.md): four processing patterns and their refresh characteristics
- [Nondeterministic Functions in Dynamic Tables](dynamic-table-nondeterministic.md): they do not cause full refreshes but produce inconsistent values across rows
- [Dynamic Table](om-dynamic-table.md): object concepts, commands, and limitations
