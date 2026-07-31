# Studio MCP: Working with Multi-Table Real-Time Sync Tasks

This document is for users who have already completed the MCP integration and want to use the Agent to create and configure multi-table real-time sync tasks. If you have not yet completed the integration, see the [Setup Guide](studio-mcp-setup-guide.md) first.

The Studio-hosted MCP Server supports a set of core structured operations for multi-table real-time sync tasks, including creating tasks, saving sync configuration, and moving a task to a submittable state.

These tasks are different from regular SQL, Shell, and Python tasks. They are not one-time batch tasks that run to completion — they are continuously running streaming sync tasks. Configuration, startup, and operations all differ accordingly.

## How to Prompt the Agent

In multi-table real-time sync scenarios, the most important thing is not to immediately ask the Agent to "start the sync directly." Clarify the source, target, sync objects, and current stage first.

If you have not fully confirmed which objects to sync, or are not sure whether a task already exists, explore first:

* Check the current catalog for any existing multi-table real-time sync tasks to reuse.
* Check whether this source data source is suitable for multi-table real-time sync.
* Show me what stage this task's configuration is currently at.

If the source, target, and sync objects are confirmed, execute directly:

* Create a multi-table real-time sync task to sync this source data source to the target.
* Save the source, target, and sync object configuration.
* After saving, tell me whether this task is ready to submit.

If you are already in the submit or operations stage:

* Show me whether this task is pending submission, submitted, or already running.
* Check the recent execution logs to see whether the task is stuck at startup, deployment, or the sync stage.

The more natural approach for this type of task is usually:

* Explore the task and configuration state first.
* Then save the structured configuration.
* Then return to the page to select the startup mode and continue operations monitoring.

## What MCP Is Well Suited to Handle

In multi-table real-time sync tasks, MCP is best suited for these structured actions:

* Creating a task object of type `281`
* Saving the source, target, and sync object configuration
* Moving the task to a submittable state

These actions are highly structured and well suited for Agent assistance.

## Understanding the Task Type

Multi-table real-time sync tasks correspond to `task_type=281`.

The goal of this task type is not to "run a SQL query once" or to "schedule one run per cron interval." Instead, it:

* Continuously receives changes from the source.
* Syncs changes to the target according to configuration.
* Is monitored long-term in the dedicated operations page.

Understanding this task type therefore focuses not on "how to run it once," but on:

* How to save the sync configuration correctly.
* How to submit and start the task.
* How to observe the run state in the dedicated operations page.

## Creating and Saving a Multi-Table Real-Time Sync Task with MCP

Typically, you create a `281` task first, then save the multi-table real-time sync configuration through MCP.

The configuration requires three types of information:

* Source data source
* Target data source
* Sync objects

In practice, both source and target should already be available data source objects in Studio. After saving, the task displays in Studio as a dedicated multi-table real-time sync configuration view rather than a regular code editor.

## Page Behavior After Saving

When the `281` task configuration is saved successfully, opening the task in Studio takes you to the dedicated configuration view.

The page typically shows:

* Source type
* Target type
* Sync mode
* Sync objects
* Table mapping
* Field inspection entry point

This means the configuration saved by MCP and the task object on the page share the same data, and both can view and modify each other.

## Submit Is Not the Same as Start

For a `281` task, submitting and starting are two different actions.

### Submit

Submitting moves the currently edited task from its editing state to an operable state. After submission, the task moves from "pending submission" to "submitted."

At the same time, an **Operations** entry point appears at the top of the IDE.

### Start

Starting actually launches the real-time sync task and puts it into a continuous run state. After submission, the next step is typically to go to the dedicated operations page and start the task — not to run it again as you would a regular batch task.

## What to Consider When Starting

When you click **Start** on the operations page, the page does not start the task silently. A startup dialog appears.

In the startup dialog, pay attention to these options:

* Startup mode
    * Stateless start
    * Resume from last saved state
    * Custom start position
* Whether to perform a full data sync before incremental sync

These options affect where the task begins receiving changes and whether a full load needs to happen first, so the startup semantics are noticeably different from a regular batch task.

## State Changes After Starting

After the task starts, the page state typically progresses through:

* Not running
* Starting
* Running

If the task has not immediately entered "Running" after starting, that does not mean failure — it may still be in the resource startup and job deployment stage.

## Structure of the Dedicated Operations Page

Multi-table real-time sync tasks have their own dedicated operations page rather than reusing the regular task instance page.

This page typically contains:

* `Task Details`
* `Execution Logs`
* `Operations Log`
* `Source Table Change Records`

The top of the page also shows action buttons corresponding to the current state, such as:

* Edit
* Start
* Stop

## What to Look for in Execution Logs

The `Execution Logs` are best for viewing the task startup and run-level progress.

After starting, this page typically shows startup and deployment-related information:

* Waiting for resources or Pod creation
* Task is ready
* Starting to prepare job content
* Starting to submit the job
* Deploying the job on the VCluster

If you want to confirm whether the task has truly started running, this page is usually more direct than just looking at the top-level status indicator.

## What to Look for in Operations Log

The `Operations Log` is best for answering "who performed which control action."

For example:

* Submit
* Start
* Stop

These records are closer to an operations audit perspective than a run-detail perspective.

## What to Look for in Task Details

`Task Details` is best for viewing the overall health and object-level state of this task.

The page typically provides:

* Task basic information
* Instance monitoring
* Total number of sync objects
* Sync state of each object
* Entry points for latency, throughput, failover, blocklist, and other metrics

This section is useful after the task starts, for determining:

* Whether the task has started actually processing objects
* Whether it is still only in the startup phase
* Whether object-level state has progressed from "not yet started" to syncing

## Understanding Source Table Change Records

`Source Table Change Records` is not a page that "always has content as soon as the task starts."

Whether records appear depends on whether CDC change events have actually occurred in the source database. If there are no new inserts, updates, or deletes in the source, no new records appearing here is expected behavior and should not be used to conclude that the task configuration failed.

## Recommended Usage Order

When combining MCP with the page, use the following order:

* Use MCP to create the `281` task.
* Use MCP to save the source, target, and sync object configuration.
* Return to the page to verify mappings and configuration placement.
* Submit the task in the page.
* Start the task from the dedicated operations page.
* Monitor state continuously in the execution logs, operations log, and task details.

This division of responsibilities is usually the clearest:

* MCP handles structured creation and saving.
* The page handles startup control, monitoring, and ongoing operations.

## When to Return to the Page First

For multi-table real-time sync tasks, the following scenarios are better handled in the page:

* When you need to inspect table mappings and field mappings
* When you need to select the startup mode
* When you need to monitor object-level state, logs, and metrics trends
* When you need to confirm source table change records

This information is oriented toward operations observation rather than single structured write actions.

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md) — What objects this MCP can cover
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — Complete development workflow for SQL/Shell/Python tasks
- [Studio MCP: Working with Data Integration Tasks](studio-mcp-integration-task-guide.md) — Data Integration task configuration and execution
- [Data Freshness and Multi-Table Real-Time Sync](multitable_realtime_sync_auto_adaptation.md) — Background concepts for multi-table real-time sync
- [Real-Time Sync Tasks](realtime_sync.md) — Operational configuration reference for multi-table real-time sync
