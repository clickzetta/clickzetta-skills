# Data Engineering Agent Pipeline Launch Checklist

Before a Pipeline goes live, confirm that the task code, directory, scheduling, dependencies, run impact, and rollback approach are all clear. The purpose of a pre-launch check is not to block publishing, but to avoid discovering after publishing that a table was written incorrectly, dependencies are missing, the compute cluster is wrong, or the schedule time is incorrect.

This checklist applies to SQL, Python, Shell, JDBC, composite tasks, and other task types before they enter periodic execution.

## Pre-Launch Check Workflow

Check in the following order:

1. Review task drafts
2. Check data impact
3. Check directories and naming
4. Check schedule configuration
5. Check upstream/downstream dependencies
6. Check compute resources
7. Check run and rollback plans
8. Confirm publishing

## Task Draft Check

| Check item | Description |
| --- | --- |
| Task name | Whether it follows the naming convention |
| Task directory | Whether it is in the correct business domain, project, or production directory |
| Task type | Whether SQL, Python, Shell, JDBC, or composite task is correct |
| Code content | Whether it matches the plan |
| Parameters | Whether environment, date, partition, or other parameters exist |
| Save status | Whether the latest version has been saved |

Suggested prompt:

> Please review the draft content of task `{task_id}`. Return the task name, directory, type, SQL summary, input table, output table, whether saved, and whether published. Do not modify the task.

## Data Impact Check

Before launching, confirm whether running the task will change any data.

| Check item | Risk |
| --- | --- |
| Whether read-only | Read-only tasks are generally lower risk |
| Whether it creates a table | Confirm the target table name and schema |
| Whether it appends writes | Confirm whether duplicate writes may occur |
| Whether it overwrites a partition | Confirm the partition range |
| Whether it deletes or updates | High-impact operations |
| Whether it is idempotent | Determines whether it is safe to re-run after failure |

Suggested prompt:

> Based on the code of task `{task_id}`, determine whether running it will create, insert, overwrite, update, or delete any tables. List the input table, output table, partition range, and re-run risk. Do not run the task.

## Directory and Naming Check

Before a Pipeline goes live, tasks should be in a stable directory — not in a temporary or personal test directory.

Check items:

* Whether it is in a production task directory
* Whether it is in the same directory as other tasks in the same pipeline
* Whether it is isolated from test tasks
* Whether the task name has meaningful business context
* Whether multi-layer tasks show order and layering in their names

Example:

```text
Sales Domain/DWD/dwd_sales_order_clean
Sales Domain/DWS/dws_sales_product_daily
Sales Domain/ADS/ads_sales_dashboard
```

## Schedule Configuration Check

Before publishing, confirm the schedule configuration — do not just save it.

| Check item | Description |
| --- | --- |
| Cron | Whether it matches the expected run time |
| Timezone | Whether it aligns with the business date |
| Retry strategy | Whether failure triggers automatic retry |
| Timeout | Whether it matches the data volume and resource expectations |
| Whether to run immediately | Whether it will trigger immediately after publishing |
| Next run time | Whether it matches expectations |

Suggested prompt:

> Please check the schedule configuration of task `{task_id}`. Return the Cron, retry, timeout, whether published, and next scheduled run time. Do not publish the task.

## Dependency Check

Multi-task Pipelines must verify upstream/downstream dependencies.

Check items:

* Whether Gold / DWS / ADS depends on upstream success
* Whether cross-directory or cross-project dependencies exist
* Whether downstream tasks stop when upstream fails
* Whether circular dependencies exist
* Whether task groups or composite tasks are involved

Suggested prompt:

> Please check the upstream/downstream dependency relationships for this set of tasks. For each task, explain who it depends on, who depends on it, and whether there are missing dependencies, circular dependencies, or downstream impacts. Do not modify the configuration.

## Compute Resource Check

Before publishing, confirm the VCluster the task will use.

Check items:

* Whether the VCluster is correct
* Whether the cluster is available
* Whether resources are sufficient for the estimated data volume
* Whether it will compete for resources with other tasks
* Whether peak hours need to be avoided

If the Agent returns inconsistent VCluster information at different points, re-read the task details before publishing.

Suggested prompt:

> Please re-read the task details of task `{task_id}`. Confirm the actual VCluster, Schema, Cron, retry, and timeout in use. Do not publish or execute the task.

## Pre-Publish Confirmation

Before publishing, ask the Agent to output a final confirmation:

```text
Task name:
Task directory:
Task type:
SQL type:
Input table:
Output table:
Whether data will be written:
Cron:
VCluster:
Retry:
Timeout:
Upstream/downstream dependencies:
Whether it will run immediately after publishing:
Next scheduled run:
How to cancel publishing:
```

Confirm everything before publishing.

Suggested prompt:

> Please prepare to publish task `{task_id}` to the scheduling system. Before publishing, state the task name, task directory, SQL type, input table, output table, Cron, retry, timeout, VCluster, dependencies, whether it will run immediately after publishing, the next scheduled run time, and how to cancel publishing. Request my confirmation first; do not publish directly.

## Post-Launch Observation

After publishing, do not immediately conclude. Observe the most recent runs.

Check items:

* Whether it triggered as planned
* Whether it ran successfully
* Whether the run duration is reasonable
* Whether the expected data was produced
* Whether downstream tasks ran in order
* Whether timeout, empty results, or data anomalies occurred

Suggested prompt:

> Please view the most recent run status of task `{task_id}` since publishing. Return the run status, duration, error summary, next scheduled run time, and whether there is downstream impact. Do not re-run the task.

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Safe Operation Guide](dataagent-safe-operation-guide.md)
* [Scheduling and Release Guide](dataagent-scheduling-and-release-guide.md)
* [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
* [Task Directory and Governance Guide](dataagent-task-directory-governance-guide.md)
