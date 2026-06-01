# View Object History (DESC HISTORY)

The `DESC HISTORY` command is used to view the historical version records of a table, dynamic table, or materialized view. Through these records, you can understand how an object has changed over time, or use them together with the Time Travel feature to query data at a specific point in time.

## Syntax

```sql
DESC HISTORY [schema_name.]<object_name>;
```

### Parameter Description

| Parameter | Description |
|-----------|-------------|
| `schema_name` | Optional. Specifies the schema name. |
| `object_name` | The name of the table, dynamic table, or materialized view. |

## Examples

### Example 1: View the History of a Regular Table

```sql
DESC HISTORY students;
+---------+-------------------------+------------+-------------+----------+-----------------+---------------------------+
| version | time                    | total_rows | total_bytes | user     | operation       | job_id                    |
+---------+-------------------------+------------+-------------+----------+-----------------+---------------------------+
| 2       | 2024-06-14 11:18:43.238 | 37         | 1387        | UAT_TEST | CREATE_TABLE_AS | 2024061403184277861pl5... |
+---------+-------------------------+------------+-------------+----------+-----------------+---------------------------+
```

### Example 2: View the History of a Dynamic Table

```sql
DESC HISTORY public.event_gettime;
+---------+-------------------------+------------+-------------+-------+-----------+---------------------------+----------------------+-------+
| version | time                    | total_rows | total_bytes | user  | operation | job_id                    | source_tables        | stats |
+---------+-------------------------+------------+-------------+-------+-----------+---------------------------+----------------------+-------+
| 3       | 2024-01-31 17:49:28.814 | 5          | 7578        |       | REFRESH   | 202401310949284215k3...   | [...]                | NULL  |
| 2       | 2024-01-31 17:48:11.862 | 4          | 3820        |       | REFRESH   | 2024013109481169177w...   | [...]                | NULL  |
| 1       | 2024-01-31 17:48:11.656 | 0          | 0           |       | CREATE    | 2024013109481148777w...   | [...]                | NULL  |
+---------+-------------------------+------------+-------------+-------+-----------+---------------------------+----------------------+-------+
```

The history of a dynamic table includes the additional `source_tables` (source table information) and `stats` (refresh statistics) fields.

### Example 3: View the History of a Materialized View

```sql
DESC HISTORY mv_inventory_basic;
+---------+-------------------------+------------+-------------+---------+-----------+---------------------------+----------------------+-------+
| version | time                    | total_rows | total_bytes | user    | operation | job_id                    | source_tables        | stats |
+---------+-------------------------+------------+-------------+---------+-----------+---------------------------+----------------------+-------+
| 2       | 2024-12-26 15:18:21.626 | 1          | 2915        | qiliang | CREATE    | 202412261518212641gm...   | [...]                | NULL  |
+---------+-------------------------+------------+-------------+---------+-----------+---------------------------+----------------------+-------+
```

### Example 4: Combine with Time Travel to Query Historical Data

```sql
-- View historical versions
DESC HISTORY event_gettime;

-- Query data at a specific point in time
SELECT * FROM event_gettime TIMESTAMP AS OF '2024-01-31 17:48:11.862';
```

## Return Field Description

| Field | Description |
|-------|-------------|
| `version` | Version number, incremented with each change |
| `time` | Version creation time |
| `total_rows` | Total number of rows in this version |
| `total_bytes` | Total number of bytes in this version |
| `user` | The user who performed the operation |
| `operation` | Operation type: `CREATE`, `REFRESH`, `INSERT`, `TRUNCATE`, etc. |
| `job_id` | The associated job ID |
| `source_tables` | Source table information (dynamic tables and materialized views only) |
| `stats` | Refresh statistics (dynamic tables only) |

## Notes

- The number of historical versions you can view is limited by the `data_retention_days` retention period (default: 1 day).
- Historical versions beyond the retention period are physically deleted and cannot be queried.
- Regular views (VIEW) do not support `DESC HISTORY`.

## Related Documentation

- [Time Travel Query](timetravel.md)
- [UNDROP TABLE](undrop-table.md)
- [RESTORE TABLE](restore.md)
