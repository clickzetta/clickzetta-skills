# Studio MCP: Working with Data Integration Tasks

This document is for users who have already completed the MCP integration and want to use the Agent to create and configure Data Integration tasks. If you have not yet completed the integration, see the [Setup Guide](studio-mcp-setup-guide.md) first.

Data Integration tasks correspond to `task_type=10`. They are well suited for one-time-run data-movement scenarios — for example, syncing single-table data from external sources such as MySQL, PostgreSQL, SQL Server, or MongoDB into the Lakehouse, or completing a one-time structured sync between different data sources.

Unlike SQL, Shell, and Python tasks, Data Integration tasks are not centered around a code editor. They are centered around source, target, field mapping, and sync rules. They are therefore well suited for having the Agent handle structured creation and configuration, while the user confirms mappings, run results, and instance state on the page.

## What MCP Is Well Suited to Handle

In Data Integration tasks, MCP is best suited for these structured actions:

* Creating a task object of type `10`
* Specifying the source data source, source table, and target table
* Saving the Data Integration configuration
* Getting the task into a form that can be run directly from the page

These actions are highly structured and well suited for Agent assistance.

## How to Prompt the Agent

In Data Integration task scenarios, the most important thing is to clarify the source, target, and current step.

If the source table, target table, catalog location, or existing task status is not yet clear, explore first:

* Show me which data sources in the current Workspace are suitable for this sync.
* Check whether the table I need to sync is in `aliyun_mysql`.
* Check the current catalog for any existing Data Integration tasks to reuse.

If the source, target, and intent are confirmed, execute directly:

* Create a Data Integration task to sync `<source data source>.<source table>` to `<target data source>.<target table>`.
* Save this task to the `Temp Dev` catalog.
* After saving, let me confirm the source and target configuration before deciding whether to run it.

If you are already at the run-confirmation stage:

* Show me how many records this run read and wrote.
* If there is dirty data, include that too.

The more natural approach is usually not to ask the Agent to complete the full sync workflow at once, but to confirm the objects and configuration placement first, then proceed to running and result confirmation.

## Understanding the Task Type

The focus of a Data Integration task is not writing a script — it is configuring the sync relationship. You typically need to confirm four types of information:

* Source data source
* Source table
* Target data source
* Target table

The page then handles additional configuration:

* Field mapping
* Write mode
* Filter conditions
* Shard key
* Sync rules

Understanding this task type therefore focuses not on "what content the task contains," but on "where data comes from, where it goes, how fields are mapped, and what rules govern the run."

## Creating and Saving a Data Integration Task with MCP

Typically, you create a `10` task first, then save the Data Integration configuration through MCP.

The configuration requires at minimum:

* Source data source name
* Source Schema or Database
* Source table name
* Source data source type
* Target data source name
* Target Schema
* Target table name
* Target data source type

Both the source and target data sources should already be available data source objects in Studio. After saving, the task displays in Studio as a dedicated Data Integration configuration view rather than a regular code editor.

## Key Checks Before and After Saving

Saving a Data Integration task configuration is not just writing a set of parameters to the task object.

During the save process, the more critical checks typically include:

* Whether the source table exists
* Whether the target table already exists or is ready
* Whether this configuration forms a valid Data Integration task definition

If the source table name, Schema, or data source name is incorrect, the save step may fail. Errors of this type typically mean you need to go back and verify the source object itself first — not suspect the run environment.

## Page Behavior After Saving

When a Data Integration task configuration is saved successfully, opening the task in Studio takes you to the dedicated Data Integration configuration view.

The page typically shows:

* `Source and Target Configuration`
* `Field Mapping Configuration`
* `Sync Rules Configuration`

This means the configuration saved by MCP and the task object on the page share the same data, and both can view and modify each other.

## What to Confirm in Source and Target Configuration

`Source and Target Configuration` is the right place to confirm whether a sync relationship has been configured correctly.

The page typically shows:

* Source data source type and name
* Source Database
* Source Table
* Target data source type and name
* Target Schema
* Target Table
* Write mode
* Filter conditions
* Shard key

For a Data Integration task, this view best answers: "Which table does this task sync, from where to where?"

## What to Confirm in Field Mapping Configuration

`Field Mapping Configuration` is the right place to confirm the mapping between source fields and target fields.

The page typically lists:

* Source field name
* Source field type
* Target field name
* Field mapping relationship

This section is important because the correctness of a Data Integration task is not just "can it run," but also "are the fields aligned and are the types mapped correctly."

If there are many fields or field names are similar, letting MCP complete the basic configuration and then returning to the page for manual confirmation is usually more reliable.

## What to Confirm in Sync Rules Configuration

`Sync Rules Configuration` is better suited for supplementary run-behavior settings.

Depending on the source and target, you typically care about:

* Whether the write mode matches expectations
* Whether filter conditions are needed
* Whether a shard key should be used to improve sync efficiency
* Whether there are dirty data handling options

This section is closer to task run semantics than object definition semantics, so it is also better suited for final confirmation on the page.

## Running the Task

After a Data Integration task is saved, you can run it directly from the IDE page.

The difference from a regular code task is:

* The main page is not a script editor.
* The run action is initiated directly based on the current integration configuration.
* Run results are displayed directly in the bottom area of the IDE.

This task type is closer to "run a sync once after configuration is complete" than to "save a script and then explain the script logic."

## Page Feedback After Running

After initiating a run from the IDE, an instance area typically appears at the bottom of the page to display feedback for the current run.

Common information includes:

* `Run Result`
* `Run Time`
* `Total Duration`
* `Records Written`
* `Records Read`
* `Dirty Records Read`
* `Dirty Records Written`
* `Logs`
* `Instance Operations`

This means that run feedback for a Data Integration task is embedded directly in the IDE page — no need to jump to a separate operations page as the first step.

## Going from the IDE to Instance Operations

If you need to view instance details further, go to `Instance Operations` from the bottom area of the IDE.

After entering, you are taken to the standard task instance operations page. Common entry points on this page include:

* `Instance Details`
* `Script Content`
* `Execution Logs`
* `Operations Log`
* `Terminate`
* `Refresh`

This link is valuable because it connects "starting a sync from the IDE" with "going to the standard instance operations page for further investigation."

## What to Look for in Instance Details

`Instance Details` is best for viewing the basic facts about this run.

The page typically provides:

* Instance ID
* Instance type
* Task name
* Task ID
* Workspace
* VCluster
* Owner
* Instance state
* Scheduled time
* Run time
* End time
* Total duration

This section is best for answering: "Was this run actually initiated, in which environment did it run, and what is the current state?"

## What to Look for in Execution Logs and Operations Log

`Execution Logs` are best for viewing the sync execution process itself. The `Operations Log` is best for answering "who performed which control action."

If the run result does not match expectations, the typical judgment order is:

* Check whether the instance state shows a successful completion.
* Check whether the records read and written match expectations.
* Check whether dirty records appeared on read or write.
* Then check the execution logs to confirm the specific execution process.

## Difference Between Data Integration Tasks and Multi-Table Real-Time Sync Tasks

Neither is centered around a code editor, but the run models differ.

Data Integration tasks are closer to a one-time-run task:

* Configuration can be run directly after saving.
* Run results are displayed directly at the bottom of the IDE.
* Follow-up goes to the regular task instance operations page.

Multi-table real-time sync tasks are closer to a continuously running task:

* Configuration must be submitted before running.
* The startup mode is selected separately.
* Follow-up goes to the dedicated real-time sync operations page.

The most common misunderstanding when users conflate these two task types is: "Why can one task run directly after saving while the other needs to be submitted first, then started?"

## Recommended Usage Order

When combining MCP with the page, use the following order:

* Use MCP to create the `10` task.
* Use MCP to save the source, target, and target table configuration.
* Return to the page to confirm source and target configuration and field mapping.
* Run the task directly from the IDE.
* Check the run result, records read/written, and dirty data in the bottom area.
* If needed, go to the instance operations page to continue viewing instance details, execution logs, and operations log.

This division of responsibilities is usually the clearest:

* MCP handles structured creation and configuration.
* The page handles mapping confirmation, run feedback, and instance observation.

## When to Return to the Page First

For Data Integration tasks, the following scenarios are better handled in the page:

* When you need to check whether field mappings are correct
* When you need to confirm the write mode
* When you need to check records read/written and dirty data
* When you need to go from the IDE to the instance operations page for further investigation

This information is oriented toward execution observation rather than single structured write actions.

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md) — What objects this MCP can cover
- [Studio MCP Task Development and Run Diagnosis Guide](studio-mcp-task-development-and-diagnosis-guide.md) — Complete development workflow for SQL/Shell/Python tasks
- [Studio MCP: Working with Multi-Table Real-Time Sync Tasks](studio-mcp-cdc-realtime-sync-guide.md) — CDC task configuration and operations
- [Studio MCP Best Practices](studio-mcp-best-practices.md) — Day-to-day usage principles
