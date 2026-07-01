# Data Engineering Agent Safe Operation Guide

The Data Engineering Agent can help you explore data, generate tasks, configure scheduling, publish jobs, and diagnose failures. Different operations have different impacts on the environment. Before using it, distinguish between operation types, and confirm the object, scope, and consequences before high-impact operations.

The core principle of safe use is: explore first, then generate a plan; create a draft first, then confirm execution; check impact first, then publish or re-run.

## Operation Risk Levels

| Level | Operation type | Does it change the environment? | Usage recommendation |
| --- | --- | --- | --- |
| Low risk | View table structure, sample data, task configuration, run history | No | Can be used as the first step for the Agent to understand context |
| Medium risk | Create Studio draft tasks, modify task content, save schedule configuration | Yes | Confirm the task name, directory, SQL type, and configuration content |
| High risk | Run write SQL, publish schedules, re-run, backfill, take offline, delete | Yes | Must check the scope of impact and request confirmation |

Read-only SQL itself does not write data, but creating Studio draft tasks modifies the task tree. Saving schedule configuration does not enter the scheduling system, but publishing a task will cause it to trigger on schedule. Confirm each of these actions separately.

Even metadata changes that do not write Lakehouse data should not be left at just "creation successful." After creating a task, composite task, DQC rule, or saving schedule configuration, continue to verify that the object was created in the correct location, correct directory, and with the correct configuration.

## Read-Only Exploration

Read-only exploration is used to give the Agent context, including:

* Viewing table structure and field types
* Viewing a small amount of sample data
* Viewing task directories and task configurations
* Viewing run history and error summaries
* Viewing available catalog, schema, and VCluster

Suggested prompt:

> Please first do read-only exploration only. View the table structure and a small amount of sample data for `{schema}.{table}`. Explain the field meanings and possible modeling approaches. Do not create tasks, write to tables, or modify configurations.

Read-only exploration should come before all complex operations. Do not create production tasks before understanding the table structure, field meanings, and task directories.

## Creating Draft Tasks

Creating a draft task adds a new task to the Studio task tree, so it is an environment change. However, it does not automatically execute SQL or enter the scheduling system.

Before creating, confirm:

* Task name
* Task directory
* Task type
* Whether the SQL is read-only, CREATE TABLE, INSERT, or OVERWRITE
* Whether a target table will be created
* Whether scheduling will be configured
* Whether it will be published

Suggested prompt:

> Please create a SQL draft task named `{task_name}` in the Studio task directory `{task directory}`. Only create a draft — do not run SQL, create target tables, or publish schedules. Before creating, state the task name, task directory, SQL type, and scope of impact, then request my confirmation.

If the target directory has not yet been created, create it in Studio first, then ask the Agent to create the task draft. Do not let the task end up in a default directory.

If a composite task or multi-node task is being created, also verify after creation:

* Whether nodes actually exist in the DAG
* Whether dependency edges have been established
* Whether node content has actually been written inside the composite task

Do not treat "object created successfully" and "node dependencies configured" as the same thing.

## Running Tasks

Before running a task, determine whether the task code will change data.

| SQL type | Impact |
| --- | --- |
| `SELECT` | Typically only reads data |
| `CREATE TABLE AS SELECT` | Creates the target table |
| `INSERT INTO` | Appends to the target table |
| `INSERT OVERWRITE` | May overwrite the target table or partition |
| `DELETE` / `UPDATE` | Modifies existing data |

Suggested prompt:

> Please explain whether running this task will only read data, or whether it will create, insert, update, delete, or overwrite any tables. Base the assessment on the SQL content; do not run the task.

Only ask the Agent to run the task after confirming the scope of impact.

## Saving Schedules and Publishing Tasks

Saving a schedule configuration and publishing a task are two different actions.

| Action | Meaning | Does it enter the scheduling system? | Will it run on schedule? |
| --- | --- | --- | --- |
| Save schedule configuration | Saves Cron, retry, timeout, dependency parameters | No | No |
| Publish task | Submits the task to the scheduling system | Yes | Yes |
| Cancel publishing | Removes the task from the scheduling system | No | No |

Before publishing, confirm:

* Cron expression
* VCluster
* Retry count and interval
* Timeout
* Upstream/downstream dependencies
* Whether it will run immediately
* Next scheduled run time
* How to pause or cancel publishing

Suggested prompt:

> Please prepare to publish task `{task_id}` to the scheduling system. Before publishing, state the task name, task directory, SQL type, Cron, retry, timeout, VCluster, dependencies, whether it will run immediately after publishing, the next scheduled run time, and how to cancel publishing. Request my confirmation first; do not publish directly.

## Creating DQC Rules Also Requires Verification

Creating DQC rules typically does not write business data, but it does modify governance metadata, so it is still an environment change.

After creation, verify:

* Rule type, for example `table_count`, null check, deduplication, or custom SQL
* Whether the check target is correct
* Whether the threshold is correct
* Whether the strong/weak blocking level matches expectations
* Whether the trigger method is correct, for example manual REST trigger or schedule integration

If it is only a test rule, use an obvious test name and delete it after validation.

## Re-Run, Backfill, and Delete

Re-run, backfill, and delete can all affect business data or downstream tasks — do not execute these directly.

Before executing, check:

* Whether the root cause has been fixed
* Whether partial data was written
* Whether duplicate data would be created
* Whether downstream tasks have dependencies
* Whether publishing needs to be cancelled first
* Whether run records or audit evidence need to be preserved

Suggested prompt:

> I am about to perform `{operation}` on `{object}`. Please first check whether it has been published, whether it has downstream dependencies, whether it has run history, and whether it may affect business outputs. Return the scope of impact first; do not execute the operation.

## Safe Prompt Templates

### Read-only exploration

> Please only do read-only exploration. View the structure, configuration, or run status of `{object}`. Do not create tasks, run SQL, or modify configurations.

### Create a draft

> Please create a draft task, but do not run it, publish it, or configure scheduling. Before creating, state the task name, directory, SQL type, and scope of impact, then request my confirmation.

### Pre-run confirmation

> Please check whether this SQL will write to, overwrite, delete, or modify any data when run. Only return the assessment and risks; do not execute.

### Pre-publish confirmation

> Please check whether task `{task_id}` is ready to publish. Focus on SQL type, target table, schedule configuration, dependencies, VCluster, retry, timeout, and downstream impact. Do not publish.

### Pre-re-run confirmation

> Please assess whether task `{task_id}` is suitable for re-running. First check whether the root cause has been fixed, whether there was partial data written, whether downstream tasks are affected, and whether re-running would produce duplicate data. Do not re-run directly.

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Task Development Guide](dataagent-task-development-guide.md)
* [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
* [DQC Data Quality Rules Guide](dataagent-dqc-guide.md)
* [Scheduling and Release Guide](dataagent-scheduling-and-release-guide.md)
* [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
* [Common Prompt Examples](dataagent-prompt-examples.md)
