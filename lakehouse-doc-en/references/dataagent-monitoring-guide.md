# Data Engineering Agent Run Monitoring Guide

This guide explains how to use the Data Engineering Agent to view task run monitoring information, with a focus on run instances, failed instances, backfill tasks, and how to interpret an empty monitoring view.

## What to Look at First

Run monitoring is not just about "are there failures." It should answer the following questions:

* Have there been any run instances recently
* Are run results successful, failed, or timed out
* Are there any backfill tasks
* Are there instances where logs, upstream/downstream details, or re-run options can be explored further

## Empty Monitoring Is a Common Scenario

In new workspaces, test workspaces, or workspaces where only drafts have been created but nothing has run, run monitoring may be completely empty.

Common symptoms:

* No run instances in the last 24 hours
* No run instances in the last 30 days
* No failed instances
* No backfill tasks

These results should first be interpreted as "no run history exists," not as a system error.

## Recommended Check Order

1. First query the last 24 hours
2. If empty, query the last 30 days
3. If still empty, assess:
   Whether the current workspace is only a development workspace
   Whether tasks were only created as drafts but never executed
   Whether tasks were never published to the scheduling system

## Suggested Prompts

View the last 24 hours:

> Please only perform read-only operations: view the task run monitoring information for the current workspace over the last 24 hours. Return the most recently run tasks/instances, status distribution, whether there are failed instances, whether there are backfill tasks, and what details can be explored further. Do not re-run, terminate, mark success or failure, or create backfill tasks.

Expand to the last 30 days:

> Please expand the monitoring range to the last 30 days and check whether any task run instances, failed instances, scheduled instances, or backfill tasks exist. If still empty, considering the current workspace and query time range, explain whether it is more likely that there is no run history or that further investigation is still needed. Do not perform any operations.

Explain empty state:

> Please explain why the current workspace has no run instances in the last 24 hours or 30 days. Distinguish between "no run history," "task not published," and "incorrect query time range." Do not perform any operations.

## What to Look at When Instances Exist

If instances exist in monitoring, continue to check:

* Instance ID
* Task ID / task name
* Status
* Run time
* Error summary
* Whether logs can be explored further
* Whether upstream/downstream dependencies can be explored further
* Whether re-run or backfill entry points exist

Suggested prompt:

> Please view the run status of task `{task_name}` over the last 24 hours. If there are failures or timeouts, list the run instance ID, execution instance ID, failure time, error summary, and recommended next steps. Do not re-run or modify the configuration.

## How to View Backfill Tasks

Backfill tasks are not available in every workspace. If monitoring returns "no backfill tasks," interpret it as:

* No backfill was created within the current time range
* Or the current workspace has simply not entered the backfill phase

This does not mean the backfill capability is unavailable.

## A Fact That Monitoring Docs Must Emphasize

In actual operations, it is entirely possible to have no run records, no failed instances, and no backfill tasks in the last 24 hours or last 30 days. This is a normal result, and is especially common in test workspaces and newly created workspaces.

Therefore, run monitoring documentation must cover "empty state explanation" — not only "what to investigate when a failed instance exists."

## Related Guides

* [Data Engineering Agent](dataagent.md)
* [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
* [Scheduling and Release Guide](dataagent-scheduling-and-release-guide.md)
* [Common Prompt Examples](dataagent-prompt-examples.md)
