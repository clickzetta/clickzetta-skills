# How to Get the Agent to Operate Studio More Accurately

This document is for users who have already started using the Agent in Studio. It focuses on one very practical question: **how to describe what you need so the Agent can more easily understand your goal, reduce unintended actions, and land results in the right place.**

This document does not walk through how to click specific features. Instead, it summarizes common ways to phrase requests and key review points when collaborating with the Agent in Studio.

## Why This Document Exists

Many problems in Studio do not originate from the execution action itself — they come from the target, object boundaries, or expected state not being specified upfront. Common situations include: tasks created in the wrong directory, drafts created when the user expected a published state, composite task objects created but the DAG left incomplete, rules created but the user assumed they had already run, the Agent returning "done" while the user actually cared about the object ID, path, dependencies, or publish status. If this information is clarified from the start, collaboration usually goes more smoothly.

## Start by Describing the Goal as "Object + Action + Boundary"

A common approach when working with the Agent is to clearly state what the object is, what action to take, what not to do, and what to return when done. You can follow this structure:

> Please perform `{action}` on `{object}`. Constraints: `{actions not to take}`. When done, please return: `{information I want to confirm}`.

For example:

> Please create a SQL task draft named `{task name}` under `{directory}`. Do not execute, do not publish, do not write any data. When done, please return the task ID, task path, and current task status.

This style tends to reduce ambiguity because it puts the object, action, boundary, and expected return together in one place.

## What Information Is Worth Stating Upfront

**Target workspace.** If you switch between multiple workspaces, it helps to specify which one you are currently working in — for example, "please check in the current workspace..." or "please first confirm whether the current workspace is `{workspace name}` before continuing...". This reduces situations where the object exists but the current scope is wrong.

**Task directory.** In Studio, most task objects are part of the task tree, so directory information is usually important. If you are creating a task, composite task, or test object, it is usually worth specifying the target directory, whether it already exists, and whether creating a new directory is allowed — for example, "please create this under `Test Tasks/Temp Dev`, not the default directory."

**Object name or ID.** If the object already exists, provide the task ID, task group ID, rule ID, or an unambiguous task name. When names are similar, IDs are more reliable. If you only have the name, you can ask the Agent to do a read-only confirmation first — for example, "please first do a read-only confirmation of the task ID, directory, and current status for task `{task name}`, then continue."

**Whether you want a draft, a saved configuration, or a published state.** The most common source of confusion in Studio is the distinction between: creating a draft, saving a scheduling configuration, publishing to the scheduling system, manual execution, and backfilling. If you do not specify, you and the Agent may have different understandings of what "done" means. It usually helps to state the expected state explicitly — for example, "only create a draft," "only save the configuration," "do not publish yet," "do not execute immediately," "read-only check only."

## How to Describe Different Object Types

**Regular tasks.** Typically you would state the task type, directory, whether to only create a draft, whether to write code, whether to execute, and whether to publish. For example:

> Please create a SQL task draft named `{task name}` under `{directory}` and write an initial SQL. Do not execute, do not publish. When done, please return the task ID, path, and SQL type assessment.

**Composite tasks.** Composite tasks have one more layer than regular tasks — beyond the object itself, you also need to care about nodes and dependencies. A common approach is to break things into separate steps: first create the composite task object, then create the nodes, then configure the dependencies, and finally return the DAG structure. For example:

> Please create a composite task draft named `{task name}` under `{directory}`. Then add two SQL subtask nodes and make the second node depend on the first. Do not execute, do not publish. When done, please return the composite task ID, node list, and dependency edges.

**Task groups.** Task groups and composite tasks are not the same object. If you want a task group, state it directly:

> Please create a new task group named `{task group name}`. Do not create a composite task, do not publish, do not execute. When done, please return the task group ID and a current content overview.

**DQC rules.** For DQC rules, it helps to be explicit about the target object, rule type, trigger method, whether this is just a test rule, and whether to execute. For example:

> Please create a test DQC rule for `{schema}.{table}`. Do not trigger execution, do not link to the production pipeline. When done, please return the rule ID, rule type, trigger method, and check target.

## Four Boundaries Worth Stating Upfront

**No execution:** If you only need the Agent to help prepare objects or check configurations, write "do not execute," "do not run manually," "do not backfill," "do not re-run."

**No publishing:** If you are only doing drafting or debugging, explicitly write "do not publish," "do not enter the scheduling system."

**Do not modify production objects:** If you are working in a test environment, test directory, or on test objects, state it clearly — "test only," "do not link to the production pipeline," "do not affect other tasks."

**Confirm before executing:** For high-impact operations, a common pattern is: "Before taking action, please describe which objects will be modified and what the scope of impact is, and ask for my confirmation." These actions include publishing, unpublishing, deleting tasks, deleting dependencies, backfilling, re-running, and modifying scheduling cycles.

## What to Ask the Agent to Return When Done

Often, what actually helps you verify whether the result is correct is not the words "done" but structured information — commonly: object ID, object name, directory or path, current status, whether it is published, node list, dependency edges, rule ID, trigger method, and whether a run instance was created. For example:

> When done, please return the task ID, directory, whether it is published, and whether a run instance was produced.

Or:

> When done, please return the composite task ID, node names, node types, and dependency edges.

## Why a Second Review Is Still Needed

In Studio, "object created successfully" is usually just the first step. In many scenarios, you would add one more read-only review: is the task really in the correct directory, is the composite task DAG empty, has the subtask content been written, do the dependency edges exist, was the rule actually created, and does an empty monitor mean normal or abnormal? For example:

> After creation, please do a read-only review and return the actual object state. Do not continue modifying anything.

## High-Impact Operations Are Commonly Handled in Two Rounds

First round — impact analysis only. For example:

> Please do a read-only analysis first: if task `{task_id}` is published now, which objects will be affected, is the current configuration complete, and what should I watch for after publishing? Do not publish.

Second round — confirm execution. For example:

> Confirmed, please proceed with publishing. When done, please return the publish status and next-step recommendations.

This split keeps understanding and execution separate, makes it easier to catch misunderstandings early, and makes reviews easier in production environments.

## When Uncertain, Have the Agent Check First

If the current state of an object is not yet clear, it is usually better to have the Agent do a read-only query first rather than make changes immediately — for example, check whether the task is already published, check whether there is already a task with the same name in the current directory, check whether a DQC rule already exists, check whether there have been any recent run instances, check what is currently in the task group. These upfront confirmations often reduce rework later.

## A Common Set of Prompting Habits

If you want the Agent to operate Studio more reliably, the following information tends to be useful: state the workspace first, then the object name or ID, specify the target directory, clarify whether this is a draft, configuration, publish, or run, specify what not to do, ask for structured results, and request a second review when needed.

## Reference Templates

**Create a task draft:**
> Please create a `{SQL / Python / Shell}` task draft named `{task name}` under `{directory}`. Do not execute, do not publish. When done, please return the task ID, task path, and current status.

**Create a composite task and complete the DAG:**
> Please create a composite task draft named `{task name}` under `{directory}`. Then add `{node list}` and configure `{dependency relationships}`. Do not execute, do not publish. When done, please return the composite task ID, node list, and dependency edges.

**Save configuration without publishing:**
> Please save the scheduling configuration for task `{task_id}`, but do not publish yet. When done, please return the Cron, retry, timeout, VCluster, and current publish status.

**Confirm before high-impact operations:**
> Please first do a read-only analysis of which objects will be affected by `{publish / delete / backfill / re-run / modify dependencies}`, and ask for my confirmation. Do not execute.

**Create a DQC test rule:**
> Please create a test DQC rule for `{schema}.{table}` named `{rule_name}`. Do not trigger execution, do not link to the production pipeline. When done, please return the rule ID, rule type, check target, and trigger method.

## Related Documentation

* [Studio](studio_manual.md)
* [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md)
* [Data Engineering Agent](dataagent.md)
* [Data Analytics Agent](datagpt_introduction.md)
* [Task Development and Scheduling](task-develop.md)
* [Composite Tasks](composite_task.md)
* [Task Groups](task_group.md)
* [Task Scheduling Dependencies](task_scheduling_dependency.md)
* [Task and Instance Operations](task-instance-maintenance.md)
