# Studio MCP: Publishing, Unpublishing, and Run Diagnosis

After task development is complete, what truly affects the day-to-day production experience is usually not "can content be written" — it is these questions:

* When is it appropriate to publish?
* After publishing, how do you confirm the task has entered the scheduling system?
* When a task run has an anomaly, where do you look first?
* When do you need to unpublish a task?

The Studio-hosted MCP Server can cover the key actions in this workflow. You can have the Agent participate in pre-publish confirmation, temporary execution, task instance reading, attempt log investigation, and scheduled task unpublishing.

This means MCP is not just a task-development entry point — it can continue into the run stage after a task goes live.

## What This Document Addresses

This document is well suited for the following scenarios:

* You have completed SQL, Python, or offline sync task development and are ready to enter the run stage.
* You want to understand the difference between "run once temporarily" and "officially publish."
* You want the Agent to do a first-round investigation after a failure.
* You want the Agent to help confirm whether a scheduled task is suitable for unpublishing.

If your task is no longer in edit state and is ready for actual use, this document is usually the next step.

## How to Prompt the Agent

Publishing, unpublishing, and run investigation each have clear stages. State "what to do first, then what" when prompting.

If you are not sure whether the task meets publishing conditions, or do not know which run to start from, explore first:

* Check whether this task is ready to publish and what confirmation steps are still needed.
* Show me the most recent run status of this task — if there are failures, continue investigating.

If the object for validation, publishing, unpublishing, or investigation is confirmed, execute directly:

* Run this task once temporarily with `biz_date=2026-06-12` — if the result is normal, publish it.
* Don't publish yet — read back the task instance details and run state first.
* Show me why this task failed in its most recent run — start by looking at the task instance, attempts, and logs.

If you are preparing to stop a scheduled task:

* First check whether this task has any downstream dependencies.
* If there are no obvious dependencies, unpublish it.

The value of this kind of prompting is that it helps the Agent clearly distinguish:

* Whether you want to validate a run or officially go live
* Whether you want to investigate first and then decide how to handle it
* Whether you want to unpublish directly or check the dependency impact first

## Distinguish Three Actions

In Studio, these three actions are easily confused but serve different purposes:

* **Temporary execution**: Run once now to confirm whether this execution succeeds.
* **Publish the task**: Bring the task into the official scheduling system.
* **Unpublish the task**: Remove an already-published scheduled task from the scheduling system.

Understanding the distinction matters.

Temporary execution is better for the development phase and pre-publish validation. Publishing is better for moving a confirmed task into regular production. Unpublishing is better for stopping a task that is no longer needed or needs adjustment.

## Why Run Temporarily Before Publishing

From a task governance perspective, publishing is not "the first run." A more reliable approach is:

* Task content is saved.
* Parameters and execution configuration are confirmed.
* Schedule times have been previewed.
* Run the task temporarily once.
* Then decide whether to publish.

This lets you confirm:

* Whether the logic can run through successfully
* Whether the current parameters are correct
* Whether the current run environment and VCluster are available
* Whether execution duration is roughly as expected

This step is important for both SQL and Python tasks. For offline sync tasks, it is equally appropriate to run once first to check that read and write behave as expected.

## What Publishing Solves

The core role of publishing is not simply changing a status — it is bringing the task into formal scheduling-object management.

After publishing, users typically care about:

* Whether the task has generated a scheduled task ID
* Whether it is currently live
* What cron expression it uses
* What the default execution VCluster is
* Who published it and when

Publishing answers: "Has this task entered the official production scheduling system?" — not "Did this run succeed?"

## What to Check First After a Temporary Execution

For SQL, Python, or offline sync tasks, the most important things to read back first after a temporary execution are typically:

* `task_instance_id`
* Execution state
* Execution start and end time
* VCluster or run environment used
* Link to the instance details

For load tasks, also check:

* Records read
* Records written
* Dirty data state

The value of this step is that the Agent can first clarify "did this run actually start" before deciding whether to go into detailed log investigation.

## What Attempts and Logs Each Tell You

Task instance details answer "what happened in this run overall." Attempts and logs answer "how the run executed internally."

The natural investigation order is:

* Check the task instance state and time information first.
* Check whether attempts were generated.
* Then review the execution logs based on the attempts.

Logs are best for confirming:

* The actual SQL or script context that was executed
* Whether the Lakehouse job was submitted
* How long the SQL engine or execution engine took
* Whether the failure occurred at compile, connect, execute, or result-write stage

For many day-to-day tasks, this is enough to complete a first-round diagnosis.

## When to Unpublish

Unpublishing is typically appropriate in these situations:

* The task has been replaced by a newer version.
* The scheduled task is temporarily no longer needed.
* Upstream dependencies changed and scheduling must pause before adjustments.
* The task has an obvious risk and should not continue to trigger automatically.

From a governance perspective, unpublishing is not deletion. It is closer to switching the task from "continue running automatically" to "paused from live state."

This is friendlier for preserving history objects, configurations, and audit trails.

## Downstream Dependencies Determine How to Unpublish

For scheduled tasks, there is a critical distinction before unpublishing:

* The task has no downstream dependencies.
* The task has downstream dependencies, and you want to handle them together.

If downstream dependencies exist and you only handle the current task while ignoring downstream, the subsequent scheduling chain can enter an inconsistent state.

Therefore, before unpublishing, confirm with dependency-query capabilities:

* Whether the current task is an upstream node in a chain
* Whether downstream tasks also need to be evaluated and handled

This is also a structured check that MCP is especially well suited to do first.

## How to Bring This into Daily MCP Workflows

Bringing publishing, unpublishing, and diagnosis into a daily MCP workflow typically follows this order:

* Read the task configuration and current publish state.
* Run a temporary execution before publishing.
* Read back task instances, attempts, and logs.
* Confirm there are no obvious issues, then publish.
* When decommissioning, check dependencies first, then decide how to unpublish.

This approach is especially well suited for:

* Pre-publish self-checks
* Day-to-day failure investigation
* Scheduled task decommissioning and modification

## Practical Value

For Studio MCP, the value of publishing, unpublishing, and run diagnosis capabilities is mainly in three areas:

* Moving tasks from development state into the go-live and operations stage
* Having the Agent handle the first round of run confirmation and the first round of anomaly investigation
* Reviewing dependency relationships and impact scope before decommissioning a task

This extends the Agent's role from "generating task content" to "participating in task run management."

## Related Documents

- [Studio MCP: Working with SQL Tasks](studio-mcp-sql-task-guide.md) — SQL task creation and execution
- [Studio MCP: Working with Python Tasks](studio-mcp-python-task-guide.md) — Python task creation and execution
- [Studio MCP: Working with Offline Sync Tasks](studio-mcp-offline-integration-task-guide.md) — Offline sync task run reading
- [Studio MCP: Configuring Task Parameters and Scheduling](studio-mcp-parameters-and-scheduling-guide.md) — Configuration workflow before a task enters recurring execution
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — Studio MCP task workflow overview
