## SHOW JOBS

Displays job information owned by the current user, including completed and running jobs. By default, shows records submitted within the last 7 days, up to a maximum of 10,000 records.

## Syntax

```SQL
SHOW JOBS
  [IN VCLUSTER vc_name]
  [LIKE 'pattern']
  [WHERE <expr>]
  [LIMIT num];
```

## Parameters

| Parameter | Required | Description |
|------|------|------|
| `IN VCLUSTER vc_name` | No | Filters jobs under the specified compute cluster. If omitted, returns jobs from all compute clusters |
| `LIKE 'pattern'` | No | Pattern-matches against `job_id`. Supports `%` (any characters) and `_` (single character) wildcards |
| `WHERE <expr>` | No | Filters by return columns. Supported filter fields are listed in the return columns section below |
| `LIMIT num` | No | Limits the number of returned records, range 1-10000. Default is no limit (subject to the 7-day and 10,000-record cap) |

## Return Columns

| Column | Type | Description |
|------|------|------|
| `job_id` | STRING | Unique job identifier |
| `status` | STRING | Job status: `RUNNING`, `SUCCEED`, `FAILED`, `SETUP`, `QUEUED`, `CANCELLED` |
| `creator` | STRING | Username that submitted the job |
| `priority` | STRING | Job priority |
| `start_time` | TIMESTAMP | Job start time (UTC) |
| `end_time` | TIMESTAMP | Job end time (UTC). NULL for running jobs |
| `execution_time` | INTERVAL | Job execution duration |
| `vcluster_name` | STRING | Name of the compute cluster executing the job |
| `job_text` | STRING | SQL text of the job |
| `query_tag` | STRING | Query tag associated with the job |

The `WHERE` clause can filter on any of the above columns, for example `WHERE status='SUCCEED'`, `WHERE vcluster_name='DEFAULT'`, `WHERE execution_time > INTERVAL 2 MINUTE`.

## Examples

1. View the 3 most recent job records:

```SQL
SHOW JOBS LIMIT 3;
```

```
+---------------------------+---------+---------+----------+-------------------------+-------------------------+----------------+--------------+--------------------+-----------+
| job_id                    | status  | creator | priority | start_time              | end_time                | execution_time | vcluster_name | job_text          | query_tag |
+---------------------------+---------+---------+----------+-------------------------+-------------------------+----------------+--------------+--------------------+-----------+
| 2026051922541032000079660 | SUCCEED | qiliang | 0        | 2026-05-19 22:54:11.029 | 2026-05-19 22:54:11.046 | 17             | DEFAULT      | SHOW TABLES ...   | ...       |
| ...                       | ...     | ...     | ...      | ...                     | ...                     | ...            | ...          | ...               | ...       |
+---------------------------+---------+---------+----------+-------------------------+-------------------------+----------------+--------------+--------------------+-----------+
```

2. View jobs under the `DEFAULT` compute cluster with execution time exceeding 2 minutes:

```SQL
SHOW JOBS IN VCLUSTER DEFAULT WHERE execution_time > INTERVAL 2 MINUTE;
```

3. Filter jobs with status `SUCCEED`, returning at most 10 records:

```SQL
SHOW JOBS WHERE status='SUCCEED' LIMIT 10;
```

4. Fuzzy match by `job_id` prefix:

```SQL
SHOW JOBS LIKE '20260519%';
```

5. View the 50 most recent jobs under a specified compute cluster:

```SQL
SHOW JOBS IN VCLUSTER DEFAULT LIMIT 50;
```

## Notes

- By default, only jobs from the last 7 days are returned. Historical jobs beyond this range are not displayed.
- A single query returns at most 10,000 records; any excess is truncated.
- The `execution_time` field is in milliseconds. When used in a `WHERE` clause, it must be used with an `INTERVAL` expression, e.g. `WHERE execution_time > INTERVAL 2 MINUTE`.
- If `IN VCLUSTER` is not specified, jobs from all compute clusters for the current user are returned.
