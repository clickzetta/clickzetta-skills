# Studio MCP Task Development and Run Diagnosis Guide

The value of the Studio-hosted MCP Server is not just "connecting the Lakehouse to an LLM." It lets the Agent directly participate in Studio task development, task execution, and run investigation.

This capability supports a complete workflow:

* Create a catalog
* Create a task
* Write task content
* Read task configuration
* Save execution configuration
* Publish the task
* Run the task temporarily
* Query task instances
* Query attempts
* Query execution logs

This document mainly answers: "After connecting, what can the Agent specifically do in Studio?"

## How to Prompt the Agent

If you use Studio MCP as a work entry point, the most reliable prompting style is to describe your goal in plain working language rather than starting from a specific feature.

For example:

* Show me all the data sources and task catalogs in the current Workspace.
* Create a SQL task in the `Temp Dev` catalog and save the content I'm about to give you.
* Run it once first, then read back the task instance, attempts, and logs.

If your goal is to continue to the run stage, include the full chain:

* Save content first, then add basic configuration, then run once temporarily.
* If the result is normal, publish it.

This prompting style lets the Agent follow the "develop, execute, read back, investigate" task chain more naturally.

## Check the Environment and Objects First

Before making changes to any task, have the Agent confirm which objects are currently available.

Common starting points:

* View which data sources the current Workspace has
* View which Schemas are under a data source
* View which Tables are in a Schema
* View which catalogs and tasks are currently in Studio

This step is suitable for:

* Environment confirmation
* Metadata survey
* Finding the target task, target catalog, and target data object

## Task Development Workflow

### Create a Catalog

If you want to keep new experimental tasks, temporary tasks, or auto-generated tasks separate from existing catalogs, create a catalog first.

Through MCP, the Agent can create a new catalog under a specified parent catalog, giving the Agent's new objects a clear home and reducing the risk of mixing test tasks with production tasks.

### Create a Task

The Agent can create a task directly under a catalog. Supported task types include not just SQL, but also Shell, Python, JDBC, Data Integration, composite tasks, and more.

After creation, the result includes a `studio_url` that you can use to open the task directly in Studio.

### Save Task Content

After a task is created, it is just an empty shell. The next step is to write the actual content.

For non-integration tasks such as SQL, Shell, Python, and JDBC, content can be saved directly through MCP, for example:

```sql
SELECT 1 AS mcp_validation_result;
```

After saving, read back the task details to confirm the content has been persisted.

### Read Task Details

Task details are one of the most important read-back entry points in development state. Through task details, you can typically confirm:

* Task ID
* Task name
* Catalog
* Task type
* Current content
* Edit state
* Studio link to open the task

When a task is first created, the edit state is the initial state. After content is saved, the edit state changes — confirming that the Agent has actually progressed the task object's state.

## Task Configuration Workflow

### Read Configuration First, Then Decide How to Change It

For existing tasks, have the Agent read the configuration first rather than overwriting directly.

A task's scheduling, retry, dependency, VCluster, Schema, and timeout settings may already carry business semantics. Read first, then change — this avoids accidentally clearing existing configuration.

### Newly Created Tasks Start with Sparse Configuration

When you read configuration for a new SQL task, you will see many fields are empty, such as:

* cron
* retry
* timeout
* execute vc
* schema

This means a new task does not automatically populate a full set of execution configuration. If you want it to be publishable, schedulable, and repeatable, you typically need to add configuration.

### Save Non-Cron Configuration

For a minimum runnable task, the common non-cron configuration to add includes:

* Retry count
* Retry interval
* Timeout
* Self-dependency
* Re-run strategy

These can be saved through MCP separately, without returning to the page and opening configuration panels manually.

## Publishing and Execution

Two actions need to be clearly distinguished here — they serve different purposes.

### Publish a Task

`publish_task` corresponds to bringing the task into the scheduling system. It is closer to "making this task live as a formal scheduling object."

After publishing, the scheduling details show:

* Scheduling task ID
* Whether it is currently live
* Cron expression
* Default execution VCluster
* Validity period
* Publisher and publish time

This step answers: "Has this task entered formal scheduling management?"

### Run a Task Temporarily

`execute_task` corresponds to a one-time temporary execution. It is closer to "run this once now to see the result and state."

This step is well suited for:

* Verifying whether the SQL can execute
* Checking whether the run environment is correct
* Running a quick self-check before publishing
* Reproducing one execution during investigation

After execution, you get a `task_instance_id`, execution state, execution duration, and task run details.

## Run Diagnosis Workflow

This is one of the most valuable sections of Studio MCP, because it can chain together "what was executed" and "why it was executed that way."

### Query Task Instances

After a successful temporary execution, read task instance details using the `task_instance_id`. This typically shows:

* Execution start time
* Execution end time
* Task run state
* Executor
* VCluster used
* Page link to navigate to the instance

### Query Attempts

A single task run may produce one or more attempts. Attempts are suited for tracking:

* Retries
* Re-launches
* Execution records within a single run

### Query Execution Logs

This is one of the most direct diagnosis entry points. Reading attempt logs through MCP shows:

* Context information at execution time
* The actual SQL that was executed
* Lakehouse job ID
* SQL engine duration
* Total execution duration

For simple SQL tasks, this is already enough to complete a minimal run diagnosis. For more complex tasks, this is also an important entry point for further failure-cause investigation.

## How to Use These Capabilities

The recommended approach for Studio MCP is:

* Have the Agent survey catalogs, tasks, and metadata first.
* Have the Agent generate or modify a version of the task content first.
* Have the Agent save basic configuration and run a temporary execution for validation first.
* Have the Agent pull back task instances, attempts, and logs to narrow down the investigation scope first.

Then return to the page for:

* Graphical confirmation
* More complex scheduling-dependency adjustments
* Human review before final publish

This combination is usually more reliable than having the Agent "completely replace the page" — and more aligned with how Studio actually works.

## Continue Reading

If you have not yet completed the integration, see:

* [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md)

If you are already connected and want to bring these capabilities into daily development and operations, continue in two directions:

* More complex task types, such as Data Integration, composite tasks, and CDC multi-table real-time sync
* A more systematic approach, see [Studio MCP Best Practices](studio-mcp-best-practices.md)

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP Capabilities Overview](studio-mcp-capabilities-overview.md) — What objects this MCP can cover
- [Studio MCP: Working with Multi-Table Real-Time Sync Tasks](studio-mcp-cdc-realtime-sync-guide.md) — Real-time sync task configuration and operations
- [Studio MCP: Working with Data Integration Tasks](studio-mcp-integration-task-guide.md) — Data Integration task configuration and execution
- [Studio MCP Best Practices](studio-mcp-best-practices.md) — Day-to-day usage principles
