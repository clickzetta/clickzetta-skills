## DESC JOB

View detailed information about a specified job, including job configuration, running status, execution time, input/output statistics, and more.

## Syntax

```SQL
DESC JOB 'job_id';
```

## Parameters

| Parameter | Required | Description |
|------|------|------|
| `job_id` | Yes | The unique job identifier, in string format. Can be obtained from `SHOW JOBS` output or job execution logs |

## Return Columns

`DESC JOB` returns a list of `info_name` / `info_value` key-value pairs, including the following fields:

| info_name | Description |
|-----------|------|
| `name` | Job ID (same as `job_id`) |
| `creator` | Username who submitted the job |
| `created_time` | Job creation time |
| `last_modified_time` | Job last modified time |
| `comment` | Job description/notes |
| `workspace` | The workspace the job belongs to |
| `job_id` | Unique job identifier |
| `status` | Job status: `RUNNING`, `SUCCEED`, `FAILED`, `SETUP`, `QUEUED`, `CANCELLED` |
| `start_time` | Job start execution time |
| `end_time` | Job end time; empty if not yet completed |
| `execution_time` | Execution duration (in milliseconds) |
| `priority` | Job priority |
| `vcluster_name` | Name of the compute resource executing the job |
| `vcluster_type` | Compute resource type (e.g., `GENERAL`, `ANALYTICS`) |
| `job_text` | SQL text of the job |
| `query_tag` | Associated query tag |
| `hint` | Hint parameters used during job execution |
| `input_tables` | Input tables with rows read and bytes read |
| `output_tables` | Number of rows and bytes in output results |

## Examples

1. View detailed information for a specified job:

```SQL
DESC JOB '2026051922541032000079660';
```

```
+--------------------+------------------------------------------+
| info_name          | info_value                               |
+--------------------+------------------------------------------+
| name               | 2026051922541032000079660                |
| creator            | qiliang                                  |
| created_time       | 2026-05-19 22:54:11.031                  |
| last_modified_time | 2026-05-19 22:54:11.101                  |
| comment            |                                          |
| workspace          | quick_start                              |
| job_id             | 2026051922541032000079660                |
| status             | SUCCEED                                  |
| start_time         | 2026-05-19 22:54:11.029                  |
| end_time           | 2026-05-19 22:54:11.046                  |
| execution_time     | 17                                       |
| priority           | 0                                        |
| vcluster_name      | DEFAULT                                  |
| vcluster_type      | GENERAL                                  |
| job_text           | SHOW TABLES WHERE is_dynamic=true LIMIT 5|
| query_tag          | 00-a7a0f9af48f34b57d00b0b0331e2fd8e-...  |
| hint               | ((...))                                  |
| input_tables       | quick_start.__dql__.show_tables_impl ... |
| output_tables      | 0 rows , 0 bytes                         |
+--------------------+------------------------------------------+
```

2. First find the target job via `SHOW JOBS`, then view its details:

```SQL
-- Step 1: Find recently failed jobs
SHOW JOBS WHERE status='FAILED' LIMIT 5;

-- Step 2: View detailed information of the job
DESC JOB '<job_id obtained from the previous step>';
```

## Notes

- `job_id` must be enclosed in single quotes, in string format.
- Job IDs can be obtained from: the output of the `SHOW JOBS` command, the return information after SQL execution, or the job history page in Lakehouse Studio.
- `execution_time` is measured in milliseconds.
- The `input_tables` and `output_tables` fields record the data read/write volume of the job, which can be used to evaluate the job's resource consumption.
