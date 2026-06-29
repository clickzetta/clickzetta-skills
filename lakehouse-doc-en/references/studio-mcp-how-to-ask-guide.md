# Studio MCP Usage: Explore First, Then Execute

After completing the Studio-hosted MCP Server integration, the most common question users have is not "what is this tool called" but "how should I talk to the Agent to get things done correctly."

This document answers that question.

In Studio MCP, the more natural approach is not to memorize interface names, but to describe your goal in plain working language and let the Agent identify the objects, fill in the operation steps, and read back the results.

In other words, what you really need to know is not MCP's internal structure, but how to progressively clarify your task goal, object scope, and run constraints.

In many cases, you do not have all the information upfront. That is fine. The path that more closely matches real working patterns is:

* Ask exploratory questions first.
* Let the Agent help you converge on the right objects and scope.
* Then initiate creation, execution, publishing, or investigation.

This is more aligned with daily usage than requiring you to provide all information in a single complete request.

## Which Scenarios Call for Exploration First, and Which Can Go Straight to Execution

In practice, Studio MCP questions fall into roughly two categories.

Scenarios better suited to exploratory questions first are typically:

* You do not yet know which catalog, task, or table to use.
* You want to confirm whether an existing object can be reused.
* You do not know which configuration a task still needs before you can proceed.
* You want to investigate a run issue but do not know which instance to start from.

The more natural starting moves in these scenarios are:

* Show me which catalogs would be a good fit for this task.
* Check whether there are any existing tasks I can reuse.
* Check which configurations this task is still missing.
* Show me the most recent run status.

Scenarios where you can state the action directly in one go are typically:

* The catalog is confirmed and you are ready to create a new task.
* The task is confirmed and you are ready to save content.
* Parameter values and execution targets are confirmed and you are ready for a temporary execution.
* Task content and configuration are confirmed and you are ready to publish.

In these scenarios, go ahead and say directly:

* Create a SQL task named `Order Daily Report Validation` in the `MCP_Validation_20260612` catalog.
* Save the SQL I'm about to give you into that task.
* Run it once temporarily with `biz_date=2026-06-12`.
* If the execution result is normal, publish it.

Think of it as a simple principle:

* When objects are not yet clear, explore first.
* When objects are confirmed, execute directly.

## The More Natural Pattern Is Explore First, Then Execute

In real scenarios, many requests start with only a vague goal, such as:

* I want to build an order daily report task.
* I want to see if there are any existing tasks in this Workspace to reuse.
* I want to sync a table in, but I haven't decided where to put it.
* I want to investigate why a task failed, but I don't know the instance ID.

In these cases, the most effective approach is usually not to immediately make changes, but to let the Agent help you clarify the problem first.

For example, start like this:

* Check the `Temp Dev` catalog for any existing tasks related to an order daily report.
* Check which data sources and tables in the current Workspace are suitable for an order daily report.
* Check the most recent run status of this task and tell me whether it's worth investigating further.

Once the objects, scope, and context are clear, continue:

* Then create a new SQL task in that catalog.
* Then draft a SQL query based on that table.
* Then continue looking into the attempts and logs for that failed run.

This pattern is especially useful for these common situations:

* Many catalogs and tasks, and you are worried about picking the wrong object.
* You need to decide whether to reuse an existing task or create a new one.
* You don't yet know whether the issue is in configuration, scheduling, or the run result.
* You need to check the most recent run first before deciding whether to investigate deeply.

## Lead with the Task Goal

Once you have a reasonably clear direction, providing three pieces of information when prompting the Agent is usually enough to form a complete, actionable request:

* What you want to do
* Which object you want to operate on
* How far you want it to go

For example:

* Create a SQL task in the `Temp Dev` catalog
* Save this Python script into that task
* Change this task to run every day at 8 AM
* Run it once first and check for errors
* Show me why this task failed

This is more aligned with real workflows than referencing a tool name directly, and makes it easier for the Agent to continue down the task chain.

But you do not need to provide everything at once. If you are not sure about the object or scope, state the goal and let the Agent help narrow things down.

For example:

* I want to build an order daily report task — first check if there are existing tasks to reuse.
* I want to set this table up as a scheduled task — first help me decide whether SQL or Python is more suitable.

## What Information Helps Most After the Scope Has Narrowed

Once exploratory questions have narrowed things down, including the following information helps the Agent complete operations more reliably:

* **Object type**: SQL task, Python task, offline sync task, catalog, data source
* **Object name**: task name, catalog name, data source name, table name
* **Scope information**: Workspace, Schema, source table, target table
* **Action goal**: create, modify, execute, publish, unpublish, investigate
* **Run constraints**: business date, cron schedule, whether to preview first, whether to do a temporary execution first

For example, instead of:

* Help me create a task.

Say:

* Create a SQL task named `Order Daily Report Validation` in the `Temp Dev` catalog.

The clearer the object, the more likely the Agent will locate it correctly in one shot.

If you cannot provide everything yet, state the most critical part first and let the Agent help fill in the context.

For example:

* I want to build an order daily report — first find the relevant tables and existing tasks.
* I want to get this task running — first check what's missing: parameters, scheduling, or publishing.

## Prompts That Sound More Like Working Language

The following phrasings tend to be more reliable than "help me do something," because they specify a clear action goal.

### Surveying the Environment and Objects

Suitable phrasing:

* Show me all the data sources in the current Workspace.
* Show me which Schemas and Tables are under the `aliyun_mysql` data source.
* List the existing tasks in the `Temp Dev` catalog.

These questions are good starting points when entering a Workspace. Their purpose is not to immediately change an object, but to let the Agent map out the current environment first.

If you do not yet know what to build or change, these exploratory questions are often the best first move.

### Creating a New SQL Task

Suitable phrasing:

* Create a SQL task named `Order Daily Report Validation` in the `Temp Dev` catalog.
* Save the SQL I'm about to give you into that task.
* Read back the task details to confirm the content was saved.

If you are not sure whether a new task is needed, ask first:

* Check if there is an existing order daily report SQL task in the current catalog to reuse.
* If not, create a new one.

This approach is more reliable than creating a new task immediately, especially when the catalog has many tasks.

### Creating a New Python Task

Suitable phrasing:

* Create a Python task named `Order Cleaning Script Validation` in the `Temp Dev` catalog.
* Write a script to query `public.orders` using the Python Connector and save it to the task.
* Write a script draft using the ZettaPark DataFrame API to aggregate order data by day and save it to the task.

If the task involves Python, it helps to specify the technical path — Python Connector or ZettaPark — so the Agent can align with the target implementation.

If you have not yet decided which path to take, ask first:

* I want to build an order data cleaning task — help me decide whether SQL or Python is more suitable.

### Configuring Parameters and Scheduling

Suitable phrasing:

* Turn the `biz_date` in this SQL into a parameter.
* Add the basic execution configuration for this task.
* Change this task to run every day at 8 AM.
* Preview the next few trigger times before saving.

If you don't know what's missing, ask first:

* Show me what configuration this task still needs to run automatically every day.

This kind of question is closer to how real usage works, because many users don't know at first whether the issue is in parameters, basic execution configuration, or the schedule itself.

### Temporary Execution and Publishing

Suitable phrasing:

* Run this task once temporarily with `biz_date=2026-06-12`.
* If the execution succeeds, publish it.
* Don't publish yet — first show me whether the run result is normal.

This makes it clear to the Agent whether you care more about validation first or going live directly.

If you are not sure whether publishing conditions are met, ask first:

* Check whether this task is ready to publish and what confirmation steps are still needed.

### Investigating a Run

Suitable phrasing:

* Show me why this task just failed.
* Start by looking at the task instance, attempts, and logs.
* Help me determine whether it's a SQL error, a run environment issue, or a configuration problem.

This is more effective than saying "help me investigate," because it specifies the investigation entry point and the kind of judgment you want.

If you don't know which instance to start from, ask first:

* Show me the most recent run status of this task — if there are failures, continue investigating.

This is more aligned with how a user typically enters an investigation scenario for the first time than jumping straight to a specific instance.

## Good Prompts Say "Do This First, Then That"

Many Studio scenarios are inherently multi-step. If you already know the ordering requirements, state them directly.

For example:

* Create the task first, then save the SQL, then run it once temporarily.
* Preview the schedule first — if it looks right, then save the cron configuration.
* Check dependencies first, then decide whether it's safe to unpublish this scheduled task.

The value of this approach is that it reduces the Agent's guessing space at key decision points.

If you don't yet know the full sequence, work through it incrementally:

* Show me the current status first.
* Then tell me what the better next step is.
* After I confirm, continue.

This is also the better approach for first-time users.

## When to State Constraints More Explicitly

In the following scenarios, provide the constraints more completely:

* Many catalogs, and you are worried about creating a task in the wrong place.
* Multiple tasks with the same or similar names exist.
* A specific business date, environment, or target table is required.
* You only want to view, not change anything.
* You only want to execute, not publish.

For example:

* First check the `Temp Dev` catalog for tasks with the same name — if one exists, don't create a new one.
* Only read the current configuration of this task — do not modify it.
* Run it temporarily first — do not publish.

When there are many objects, high stakes, or irreversible actions, this kind of constraint information significantly improves reliability.

## When the First Try Doesn't Work, How to Follow Up

Many Studio MCP operations are inherently chained, so an incomplete first result does not mean starting over. The more efficient approach is to follow up directly from the previous turn.

For example:

* Continue — add the `biz_date` parameter.
* Don't publish — read back the task instance details from this run.
* Keep investigating the logs — find out which layer the failure is in.
* That's the wrong catalog — move it to the `Temp Dev` catalog.

This kind of follow-up allows the Agent to continue from the current context without re-interpreting the entire task.

In practice, "explore first, then converge, then follow up" is usually more comfortable than writing a long, complete instruction from the start — and more suitable for most users.

## What Makes a Prompt More Likely to Get the Right Result

Reliably effective prompts tend to share a few traits:

* Describe the goal with business actions rather than just "do something."
* Provide the complete object name.
* State ordering requirements when they matter.
* Specify which actions to take and which to skip.

For example, once the target object is confirmed, instead of:

* Help me with this task.

Say:

* Read the current configuration of this SQL task, add the `biz_date` parameter, preview the daily 8 AM schedule, then save the configuration after I confirm it.

The first version requires the Agent to guess your goal. The second describes the task chain clearly enough to execute.

For most users, the more realistic path is not to get it right in one shot, but to:

* Ask an exploratory question first.
* Then add object and constraint details based on the Agent's response.
* Finally, carry out the action.

This is also the approach that more easily builds intuition through actual use.

## Ready-to-Use Prompt Templates

The following templates can be used directly with a name substitution.

### Explore First, Then Decide Whether to Execute

* Check the `<catalog name>` catalog for existing tasks to reuse — if none, create a new one.
* Check what configuration this task is still missing — I'll decide whether to continue modifying after you confirm.
* Check the most recent run status — if there are failures, continue investigating the logs.

### Create and Save a SQL Task

* Create a SQL task named `<task name>` in the `<catalog name>` catalog, then save the SQL I'm about to give you.

### Create and Save a Python Task

* Create a Python task named `<task name>` in the `<catalog name>` catalog using `Python Connector` / `ZettaPark DataFrame API`, then save the script I'm about to give you.

### Convert a Task into a Parameterized Template

* Turn the `biz_date` in this task into a parameter and add the basic execution configuration.

### Configure Scheduled Execution

* Change this task to run every day at 8 AM, and preview the next few trigger times before saving.

### Run Once, Then Decide Whether to Publish

* Run this task once temporarily with `biz_date=2026-06-12` — if the result is normal, publish it.

### Investigate a Failed Run

* Show me the cause of the most recent failed run for this task — start by looking at the task instance, attempts, and logs.

## The Core Principle of This Document

If you remember only one principle, make it this:

Start with an exploratory question, then progressively clarify the object, scope, and constraints.

For most users, this is more comfortable than writing one complete, long instruction from the start — and more aligned with how real usage actually works.

## Related Documents

- [Studio-Hosted MCP Server Setup Guide](studio-mcp-setup-guide.md) — How to complete the integration
- [Studio MCP: Working with SQL Tasks](studio-mcp-sql-task-guide.md) — SQL task scenarios
- [Studio MCP: Working with Python Tasks](studio-mcp-python-task-guide.md) — Python task scenarios
- [Studio MCP: Working with Offline Sync Tasks](studio-mcp-offline-integration-task-guide.md) — Offline sync task scenarios
- [Studio MCP: Configuring Task Parameters and Scheduling](studio-mcp-parameters-and-scheduling-guide.md) — Parameters and scheduling configuration
- [Studio MCP: Publishing, Unpublishing, and Run Diagnosis](studio-mcp-release-and-diagnosis-guide.md) — Go-live and investigation stages
