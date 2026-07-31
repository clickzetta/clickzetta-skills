# Studio MCP: Configuring Task Parameters and Scheduling

In Studio, many tasks are not "done" once the content is written. Before entering regular production runs, two layers of key information usually need to be added:

* What parameters does each run of this task need?
* What time and cadence should this task run on?

For SQL and Python tasks, these two layers of configuration directly determine whether a task can move from a one-time validation to a state that supports repeated execution, scheduled operation, and long-term maintenance.

The Studio-hosted MCP Server can bring this work into a continuous workflow. You can complete parameterization, non-cron configuration, schedule preview, and schedule saving in the Agent conversation without returning to the page to open configuration panels one by one.

## What This Document Addresses

This document is well suited for the following scenarios:

* You have already built a SQL or Python task and want to make it a repeatable task.
* You want the same task to support different business dates, different environments, or different filter conditions.
* You want the task to run automatically — daily, hourly, or on a fixed schedule — not just "run once now."
* You want to confirm that future trigger times match expectations before saving the schedule.

If you have already completed task creation and content saving, this document is usually the next step.

## How to Prompt the Agent

Parameters and scheduling configuration often appear together. State your requirements directly — "convert to a parameterized template," "preview before saving" — rather than presenting them as separate requests.

If you are not sure whether the task is missing parameters, basic execution configuration, or scheduling, explore first:

* Show me what configuration this task still needs to run automatically every day.
* Check whether this task is suitable for becoming a scheduled task.

If the gaps are clear, execute directly:

* Turn the `biz_date` in this SQL task into a parameter.
* Add the basic execution configuration.
* Change this task to run every day at 8 AM, and preview the next few trigger times before saving.

If your goal is to validate before deciding whether to add a recurring schedule:

* Convert this task to a parameterized template first.
* Run it once temporarily with `biz_date=2026-06-12`.
* If the result is normal, save the scheduling configuration.

This kind of phrasing helps the Agent distinguish:

* Which values should become parameters
* Which configuration items are just run controls
* Whether to save the schedule now or preview first

## Where Parameters and Scheduling Fit in the Task Lifecycle

From the perspective of a Studio task lifecycle, these steps usually come together:

* Create the task
* Save the task content
* Configure parameters
* Save basic execution configuration
* Preview the schedule
* Save the schedule configuration
* Temporary execution or publish

Parameters answer "what values does this run use." Scheduling answers "when does this task run automatically."

The two often appear together because scheduled tasks naturally need parameters, for example:

* Processing a business date each day
* Generating statistics for a monthly cycle
* Switching the same logic to different environments, database names, or filter conditions

## Which Tasks Are Better Suited for Parameterization

Task parameters are best used in the following situations:

* The code logic is stable but the run values change.
* The same task needs to run repeatedly on different dates.
* The same task needs to be reused across different environments or objects.
* You want to manage the task template and the current run values separately.

In a SQL task, a common form is:

```sql
SELECT *
FROM public.orders
WHERE biz_date = '${biz_date}';
```

In a Python task, parameters can be used as run inputs to the script rather than hardcoding dates, database names, or filter conditions in the code.

The value of doing this:

* The task itself is more stable.
* Switching inputs at run time is easier.
* The task is better suited for combining with scheduling.

## Parameter Configuration Is About Run Mode, Not Syntax

From a usage perspective, the most important aspect of parameter configuration is not "knowing how to write `${variable}`." It is clarifying three things:

* Which values are part of the task template
* Which values are inputs determined only at run time
* Whether these inputs are passed temporarily or hardened into scheduling configuration

For the Agent, this step is well suited for structured handling because it can simultaneously do a consistency check across task content and parameter definitions:

* Which parameters does the code reference?
* Are those parameters defined?
* Are they better written as fixed values, date values, or environment values?

## Non-Cron Configuration Is Also Part of Pre-Scheduling

Before a task enters a recurring run, in addition to parameters, a layer of basic execution configuration usually needs to be added.

This configuration typically includes:

* Retry count
* Retry interval
* Timeout
* Self-dependency
* Re-run strategy

These address the stability of the task as a runnable object — not whether the business logic itself is correct.

For a temporary task run only once, these settings can stay minimal. For a task that is intended to be retained and scheduled, add them after configuring the parameters.

## Why Preview the Schedule First

The most common failure point in scheduling configuration is not an expression that cannot be written — it is saving and then discovering the trigger times are not what you wanted.

The more reliable approach is:

* Generate or confirm the cron expression.
* Preview the trigger times for an upcoming period.
* Then save the scheduling configuration.

The value of this step is that it moves human confirmation before writing the configuration.

For Agent workflows, this is especially important, because what users really care about is often:

* What time does it trigger each day?
* Does it span midnight?
* Do holiday or schedule boundaries match expectations?

Rather than simply receiving a cron string.

## The Relationship Between Parameters, Scheduling, and Execution

A parameterized task typically has two usage patterns:

* Run temporarily with a specific set of parameter values to verify the logic.
* Then save the scheduling configuration so the task runs automatically on a fixed cadence.

These two patterns are not mutually exclusive. The more common order is:

* Write the task as a parameterized template first.
* Run it once with concrete parameters to verify it works.
* Then decide whether to save a recurring schedule.

This avoids premature publishing and ensures the schedule is built on a real successful run.

## How to Bring Parameters and Scheduling into Daily MCP Workflows

Bringing parameters and scheduling configuration into a daily MCP workflow typically follows this order:

* Read the current content and configuration of the target task.
* Identify which values are suitable for parameterization.
* Save the task parameters and basic execution configuration.
* Preview the schedule.
* Confirm, then save the scheduling configuration.
* Run a temporary execution if needed.

This approach is suitable for:

* Turning a temporary SQL task into a daily report task
* Turning a one-time Python script into a recurring processing task
* Refactoring a task with a hardcoded date into a repeatable execution template

## Practical Value

For Studio MCP, the value of parameters and scheduling capabilities is mainly in three areas:

* Moving a task from "can write, can run" to "can run repeatedly"
* Separating the task template from run inputs, reducing the cost of frequent code changes
* Moving schedule confirmation earlier, reducing the risk of misconfigured schedules entering production

This is also one of the most worthwhile sections to complete when a task is moving from temporary validation to regular production runs.

## Related Documents

- [Studio MCP: Working with SQL Tasks](studio-mcp-sql-task-guide.md) — SQL task creation, saving, and execution
- [Studio MCP: Working with Python Tasks](studio-mcp-python-task-guide.md) — Python task creation, saving, and execution
- [Task Parameters](task_param.md) — Studio task parameter capabilities
- [Task Parameter Syntax Reference](task_param_reference.md) — Parameter expressions and built-in time functions
- [Studio MCP: Publishing, Unpublishing, and Run Diagnosis](studio-mcp-release-and-diagnosis-guide.md) — Operations after a task enters the run stage
