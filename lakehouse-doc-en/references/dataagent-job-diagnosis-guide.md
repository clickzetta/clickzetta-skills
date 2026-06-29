# Data Engineering Agent Job Diagnosis Guide

Job diagnosis is used to locate the cause of task run failures, timeouts, unexpected results, or missed scheduled triggers. The Data Engineering Agent can combine task configuration, run instances, error messages, SQL content, dependency relationships, and scheduling state to output root cause judgments, evidence, impact scope, and fix recommendations.

The goal of diagnosis is not to simply restate the error message but to answer four questions:

- Why did it fail
- What was affected
- Does it need to be rerun
- What are the next fix steps

## Explore First, Then Diagnose Deeply

Task diagnosis is one of the most typical "explore first, then execute" scenarios.

Users often do not initially know:

- In which instance the most recent failure occurred
- Whether it was an ad-hoc execution failure or a scheduled run failure
- Whether the problem is in SQL, permissions, resources, dependencies, or data itself

The more natural approach is not to immediately ask the Agent to diagnose a specific instance, but to explore run status first and then narrow down.

Better exploratory opening questions:

- Help me check the latest run status of this task.
- Help me check whether there are any failed or timed-out instances in the last 24 hours.
- Help me check whether this task has any run history at all.

Once run instances, failure time, and error summaries are clear, moving into root cause diagnosis is more stable.

## When to Use Job Diagnosis

The following scenarios are suited for job diagnosis:

- Task run fails
- Task runs for a long time or times out
- Task runs successfully but the result is empty or clearly anomalous
- Task does not trigger at the scheduled time
- Downstream tasks did not run
- First run after publishing needs status confirmation
- Confirming impact scope before backfill, rerun, or unpublish

If you only need to check whether a task is published or the next run time, check task status first without moving directly into failure diagnosis.

## Empty Monitoring Is Not an Anomaly

In new workspaces, test workspaces, or workspaces where tasks were only created as drafts but never run, run monitoring may show:

- No run instances in the last 24 hours
- No run instances in the last 30 days
- No failed instances
- No backfill tasks

These results should first be interpreted as "no run history currently exists" — not as a product malfunction.

When monitoring is empty, first confirm:

- Whether tasks were only created as drafts and never executed
- Whether tasks were never published to the scheduling system
- Whether the query time range is too narrow
- Whether the current workspace is primarily for testing or development

## Prepare Information Before Diagnosing

When asking for diagnosis, try to provide:

| Information | Purpose |
|---|---|
| Task ID or task name | Locate task configuration and code |
| Run instance ID | Locate a specific run |
| Execution instance ID | Locate a specific attempt or retry |
| Failure time | Narrow the query scope |
| Error summary | Helps quick classification |
| Whether published | Determine if the scheduling system is involved |
| Whether upstream/downstream dependencies exist | Determine impact scope |

If you don't know the instance ID, ask the Agent to query recent run history first.

Recommended question:

> Please view the run history of task `{task_name}` in the last 24 hours. If there are failures or timeouts, list the run instance ID, execution instance ID, failure time, error summary, and recommended next steps. Do not rerun tasks; do not modify configuration.

If the last 24 hours are empty, continue:

> Please expand the run monitoring range to the last 30 days and check whether there are any run instances, failed instances, scheduling instances, or backfill tasks. If still empty, explain whether this is because there is no run history or because the query range or workspace selection is incorrect. Do not take any action.

## Recommended Diagnosis Flow

### Confirm Run Status First

The Agent should first confirm the current task state:

- Whether it succeeded, failed, was cancelled, or timed out
- Whether it was an ad-hoc execution or scheduled run
- Whether it is published to the scheduling system
- Which VCluster is used
- Whether there are run instances and execution instances
- Whether downstream was affected

If there are no run instances, state directly "no instances available for diagnosis" rather than outputting generic failure analysis.

Recommended question:

> Please view the current status and recent run history of task `{task_id}`. Return whether it is published, the latest run status, run instance ID, execution instance ID, error summary, and next scheduled run time. Do not modify configuration.

### Classify the Root Cause

Common failure types:

| Type | Typical symptom | Common handling |
|---|---|---|
| Table not found | `table or view not found` | Check catalog, schema, table name, and upstream output |
| Column not found | `column not found` | Check field names, table schema, SQL version |
| SQL syntax error | `syntax error` | Fix SQL syntax |
| Insufficient permissions | `permission denied`, `access denied` | Check roles and resource permissions |
| Compute cluster issue | VCluster unavailable, insufficient resources | Check cluster status and resources |
| Scheduling dependency issue | Upstream not complete, dependency not triggered | Check upstream/downstream relationships |
| Timeout | Run time exceeds limit | Optimize SQL, add resources, or adjust timeout |
| Data anomaly | Succeeds but result is empty or shows abnormal variance | Check filter conditions, partitions, and data quality |

A diagnostic report should clearly state which category, not just restate the raw error.

### Provide Evidence

A good diagnostic report should list evidence:

- Error summary
- Failure phase: semantic analysis, permission check, execution phase, scheduling phase
- Relevant SQL snippets
- Tables, fields, and VCluster involved
- Run instance and execution instance
- Upstream/downstream dependency state
- Whether data was already written

For example, "table not found" errors typically occur at the semantic analysis phase. SQL never enters actual execution and typically does not write to business data.

### Assess Impact Scope

After a task fails, assess the impact scope before running again.

Key checks:

- Whether the task is published
- Whether it was an ad-hoc execution
- Whether there are downstream tasks
- Whether partial data was already written
- Whether it affects business dashboards or data services
- Whether backfill is needed

If it was a read-only ad-hoc execution failure, business data and downstream tasks are typically unaffected. If it was a production scheduled task failure, check the downstream pipeline and data output timing.

### Decide Whether to Rerun

Do not treat rerunning as the default response.

Situations suited for rerunning:

- A temporary resource issue has recovered
- Upstream data has been backfilled
- Permissions or configuration has been fixed
- SQL has been corrected

Situations not suited for immediate rerunning:

- Table name, field name, or SQL logic still contains errors
- Permission issues are unresolved
- Upstream dependencies still have not succeeded
- The target table may have been partially written; idempotency must be confirmed first
- The failure was an expected test behavior

Recommended question:

> Please assess whether this failed task is suitable for rerunning. First state whether the root cause has been fixed, whether there was partial writing, whether downstream is affected, and whether rerunning would produce duplicate data. Do not rerun directly.

## Diagnostic Report Structure

Ask the Agent to output a fixed structure for easier team investigation and documentation:

```text
Task information:
- Task ID / name
- Run instance ID
- Execution instance ID
- Execution time
- VCluster

Current state:
- Success / failure / timeout / cancelled
- Ad-hoc execution / scheduled run
- Whether published

Root cause:
- Error type
- Failure phase
- Key evidence
- Confidence level

Impact scope:
- Whether data was written
- Whether downstream is affected
- Whether scheduling is affected
- Whether business output is affected

Handling recommendations:
- Whether rerun is recommended
- Fix steps
- Questions requiring manual confirmation
```

## Example: Table Not Found Error

If SQL references a nonexistent table, the Agent should classify this as a "table not found" error.

Example error:

```text
CZLH-42000: Semantic analysis exception: table or view not found
```

Diagnosis points:

- Error occurred at the semantic analysis phase
- SQL references a nonexistent table or incorrect catalog/schema
- If it's a read-only query, data was typically not written
- If the task is unpublished, the scheduling system is typically unaffected
- Rerunning is not recommended before fixing, as the same result will occur

Fix recommendations:

- Check whether the table name, catalog, and schema are correct
- Confirm whether an upstream task should have produced this table first
- If the table name changed, update the SQL and rerun
- If permissions prevent access, check roles and authorization

## Recommended Prompt Templates

### Query recent failures

> Please view the run history of task `{task_name}` in the last 24 hours. If there are failures or timeouts, list the run instance ID, execution instance ID, failure time, error summary, and recommended next steps. Do not rerun tasks; do not modify configuration.

### Diagnose a specific instance

> Please diagnose the failed run of task `{task_id}`. The scheduling instance ID is `{schedule_instance_id}` and the execution instance ID is `{execute_instance_id}`. Return run status, error summary, root cause judgment, evidence, impact scope, whether rerun is recommended, and fix recommendations. Do not publish, do not rerun, do not modify the task.

### Assess whether rerun is appropriate

> Please assess whether the failed instance of task `{task_id}` is suitable for rerunning. First check whether the root cause has been fixed, whether there was partial writing, whether downstream tasks are affected, and whether rerunning would produce duplicate data. Do not rerun directly.

### Diagnose why scheduling did not trigger

> Please check why task `{task_id}` did not trigger as scheduled. Check publish state, cron expression, next scheduled run time, dependencies, suspended state, and recent scheduling records. Do not modify configuration.

### Explain empty monitoring state

> Please explain why the current workspace has no run instances in the last 24 hours or 30 days. Distinguish between "no run history," "task not published," and "query time range is incorrect." Do not take any action.

### Generate an incident review

> Please compile this task failure into an incident review covering: symptom, root cause, impact scope, fix process, whether backfill is needed, and follow-up prevention measures.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
