# Studio MCP: The Offline-Sync-to-SQL ELT Workflow

Many teams using Studio MCP are not working on a standalone SQL task or a standalone offline sync task in isolation. They want to chain two steps into the shortest viable ELT path:

* Sync external data into the Lakehouse first.
* Then do SQL transformation on the sync result.
* Add parameters and scheduling as needed.
* Validate with an execution first, then decide whether to publish.

This document is organized around exactly that shortest path.

It does not try to cover all task types, all dependency relationships, or all go-live strategies. It answers a more practical question:

How do you use the Agent to move a single external table from "entering the Lakehouse" to "forming a runnable SQL task"?

## When This Document Applies

This document is well suited for the following high-frequency scenarios:

* You need to sync tables from MySQL, PostgreSQL, or other external sources into the Lakehouse first.
* After syncing, you want to run a cleaning, aggregation, or summarization operation on that table.
* You want to close the minimum loop on this workflow rather than building a complex orchestration right away.
* You want the Agent to handle structured actions such as object discovery, task creation, configuration saving, and execution validation.

If your goal is to work through the shortest ELT path first — rather than building a complex task system from the start — read this document first.

## What the Shortest Path Includes

From a task workflow perspective, this path typically has five steps:

* Confirm the source table, target table, and catalog location.
* Create and save the offline sync task.
* Create and save the SQL task based on the target table.
* Add parameters and scheduling as needed.
* Validate with a temporary execution first, then decide whether to publish.

The value of this chain is that it connects "get data in" with "process data downstream."

If you only sync without doing downstream SQL, the transformation value has not actually landed. If you only write SQL without stably syncing the upstream data, the SQL has no reliable input.

## Usage: Explore First, Then Execute

Not every step in this workflow calls for a direct instruction from the start.

The more natural approach is:

* When objects are not yet clear, explore first.
* When objects are confirmed, execute directly.

For example:

* When you don't know which table to sync or which catalog to use, have the Agent survey the objects first.
* Once the source table, target table, and catalog are confirmed, have the Agent create the sync task.
* Once the target table is in place, have the Agent create the SQL task based on it.

## Step 1: Narrow Down the Object Scope

This workflow is best started by confirming three types of objects:

* Source data source and source table
* Lakehouse target table
* Studio task catalog

If this information is not complete, ask first:

* Show me which tables in `aliyun_mysql` are suitable for this sync.
* Show me which catalogs are suitable for this experimental task.
* Check the current catalog for any existing offline sync tasks or SQL tasks to reuse.

The goal of this step is not to immediately create objects, but to avoid creating tasks in the wrong catalog, picking the wrong table, or creating duplicate tasks.

## Step 2: Create the Offline Sync Task

Once the source table, target table, and catalog location are confirmed, proceed to sync task creation.

At this point, say directly:

* Create an offline sync task to sync `<source data source>.<source table>` to the Lakehouse target table, and save it to the `<catalog name>` catalog.

If you want a quick minimum validation, add the goal:

* After saving, run it once — check whether the read and write are normal.

For this step, the Agent is best suited to:

* Creating the task object
* Saving the source and target configuration
* Triggering a run
* Reading back the records read, records written, and dirty data counts

When this step is complete, you have an upstream input table that has entered the Lakehouse.

## Step 3: Create the SQL Task Based on the Sync Result

Once the sync result is in the Lakehouse, the next step is usually not to immediately build complex orchestration, but to create a minimal SQL task that transforms that table into a result table, aggregation table, or validation query for downstream use.

At this point, say directly:

* Based on the target table that was just synced in, create a SQL task named `<task name>` in the `<catalog name>` catalog.
* Save the SQL I'm about to give you.
* After saving, read back the task details to confirm the content is in the task object.

If you have not yet decided what SQL to write, explore first:

* Based on this synced table, draft a SQL query suitable as a daily report aggregation.

The core of this step is not "having the Agent write SQL" — it is moving the synced data forward into a downstream processing task.

## Step 4: Add Parameters and Scheduling as Needed

If this SQL is just for temporary validation, running it once here is usually enough. If it is going into a repeated-run state, it is worth adding a layer of parameters and scheduling.

Common prompts:

* Turn the `biz_date` in this SQL task into a parameter.
* Add the basic execution configuration.
* Change this task to run every day at 8 AM, and preview the next few trigger times before saving.

If you don't know what's missing, explore first:

* Show me what configuration this SQL task still needs to run automatically every day.

The goal of this step is to move the SQL task from "a one-time script" to "a repeatable task template."

## Step 5: Validate First, Then Decide Whether to Publish

In this shortest path, publishing should not be the first step — it is usually the last step.

A reliable order is:

* Run the sync task temporarily first to check that data came in correctly.
* Then run the SQL task temporarily to check that the logic works.
* After confirming normal results, decide whether to publish the SQL task.

At this point, say directly:

* Run this SQL task once temporarily with `biz_date=2026-06-12`.
* If the result is normal, publish it.

If you are not sure whether publishing conditions are met, ask first:

* Check whether this task is ready to publish and what confirmation steps are still needed.

## Which Steps Are Best Suited for the Agent

From a practical perspective, the steps the Agent is best suited to handle are:

* Surveying catalogs, tasks, data sources, and tables
* Creating the offline sync task
* Saving sync configuration and triggering a run
* Creating the SQL task and saving content
* Adding parameters, basic execution configuration, and scheduling configuration
* Triggering a temporary execution and reading back the run result

Steps better handled with human confirmation on the page are typically:

* Detailed Data Integration confirmation when there are many field mappings
* Complex configuration items that require visual judgment
* Final human review before publishing

This is the most natural division of labor in this workflow:

* The Agent handles structured progression.
* The page handles visual confirmation and final verification.

## Practical Value of This Shortest ELT Path

This path is worth documenting as a scenario guide because it is closer to a user's real goal than separate docs on sync tasks or SQL tasks.

It answers not "how to configure a task type," but:

* How does an external table enter the Lakehouse?
* Once it's in, how do you quickly form a downstream processing task?
* When do you need parameters and scheduling?
* How do you validate first, then move to production?

For teams just starting to bring the Agent into Studio workflows, this is typically the easiest path to complete successfully — and the one most likely to build confidence.

## Related Documents

- [Studio MCP Usage: Explore First, Then Execute](studio-mcp-how-to-ask-guide.md) — Overall usage path for Studio MCP
- [Studio MCP: Working with Offline Sync Tasks](studio-mcp-offline-integration-task-guide.md) — Upstream data loading
- [Studio MCP: Working with SQL Tasks](studio-mcp-sql-task-guide.md) — Downstream SQL transformation
- [Studio MCP: Configuring Task Parameters and Scheduling](studio-mcp-parameters-and-scheduling-guide.md) — Parameters and scheduling configuration
- [Studio MCP: Publishing, Unpublishing, and Run Diagnosis](studio-mcp-release-and-diagnosis-guide.md) — Validation, publishing, and investigation
