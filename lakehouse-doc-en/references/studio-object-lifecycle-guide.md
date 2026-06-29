# Studio Object Relationships and Lifecycle

This document focuses on several groups of core concepts in Studio that are most commonly confused: workspaces, task directories, tasks, composite tasks, task groups, scheduling configurations, publishing, run instances, backfill instances, and data quality rules. Rather than describing how to click through menus, this document aims to help you build a stable object model first.

Understanding the relationships between these objects makes it much easier to judge what stage you are at during task development, scheduling and publishing, operations and monitoring, and quality governance — and helps reduce rework.

![](.topwrite/assets/34-studio-object-lifecycle.svg)

## Why This Document Matters

Many high-frequency misunderstandings in Studio come from not clearly distinguishing object layers — assuming that because a task was created it is already running, that saving a scheduling configuration means it has been published, that a successful composite task creation already has a complete DAG, or that having run monitoring means the task has actually executed. These questions almost always trace back to the object relationships not being fully understood.

## The Core Objects in Studio

You can think of Studio as having three layers of objects:

**Organization-layer objects:** Address "where objects live, what scope they belong to, and how they are organized." This includes workspaces, task directories, and task groups.

**Development and orchestration objects:** Address "what task I want to define, how the task is internally orchestrated, and how scheduling is configured." This includes regular tasks (SQL / Python / Shell / JDBC, etc.), composite tasks, subtask nodes within composite tasks, scheduling configurations, and publish status.

**Execution and governance objects:** Address "whether the task has actually run, what the result was, and what the quality and governance rules are." This includes run instances, backfill instances, job history, and DQC data quality rules.

## What Is a Workspace

A workspace is the collaboration and isolation boundary in Studio. Think of it as a project boundary, an environment boundary, and a team collaboration scope. Under a workspace, you have task directories, task objects, data sync objects, run monitoring scope, and quality governance information.

When you encounter situations like "why can't I find it," "why is the monitor empty," or "why is the object not here," confirming that you are in the correct workspace is usually the most efficient first step.

## What Is a Task Directory

A task directory is the organizational structure within the task tree, used to store task drafts and categorize tasks by project, business domain, environment, and lifecycle for easier searching, cleanup, and governance.

Task directories and task groups are two independent levels of objects that are easy to confuse. The difference is: a **task directory** is the path where task objects are stored (like a folder); a **task group** is a collection object that organizes tasks from a business or pipeline perspective.

## What Is a Task

A regular task is the most basic development object, including SQL tasks, Python tasks, Shell tasks, JDBC tasks, dynamic table tasks, and streaming SQL tasks. A task typically contains two types of content: **task content** (SQL / Python / Shell logic, etc.) and **task configuration** (parameters, scheduling, cluster, dependencies, etc.).

A task object existing does not mean the task is ready to run, nor does it mean it has entered the scheduling system.

## What Is a Composite Task

A composite task is the task object in Studio that carries DAG orchestration, distinct from regular tasks and task groups. Its role is to hold multiple subtask nodes within a parent object, configure the before/after relationships between nodes, and form a true DAG orchestration structure.

To check whether a composite task is properly configured, look at: whether nodes exist, whether node content has been completed, whether dependency edges have been established, and whether the DAG matches expectations.

## What Are Subtasks in a Composite Task

Subtasks are the execution nodes inside a composite task. Common types include SQL, Python, Shell, JDBC, offline sync, branch task, virtual task, Databricks SQL, and Databricks Notebook.

A few things worth noting upfront: a subtask being in the DAG does not mean its content has been written; subtask content being written does not mean scheduling or run configuration is complete; whether subtasks actually form dependencies depends on the DAG edges.

## What Is a Task Group

A task group is an independent organization and governance object. Its role is to aggregate related tasks, view tasks from a collection perspective, and carry the organizational relationships of a set of tasks.

Distinguish three easily confused concepts: a **directory** is which path a task is stored at; a **task group** organizes tasks from a business or pipeline perspective; a **composite task** performs DAG orchestration within a single object.

## What Is a Scheduling Configuration

A scheduling configuration is a set of parameters written into the task metadata. Common fields include Cron, retry count, timeout, compute cluster, dependency relationships, and parameters.

The essence of a scheduling configuration is "the task now has run rules," but it needs to be kept separate from the following states: the task has been published, the task has entered the scheduling system, and the task has generated run instances. It is more accurate to think of "saving a scheduling configuration" as a metadata change rather than a run action.

## What Is Publish Status

Publish status describes whether a task has entered the scheduling system and is in a state where the scheduling system can trigger it. It is a different layer from draft status and configured status.

The typical progression of a task is: has a draft object → has task content → has a scheduling configuration → is published → has generated run instances. Keeping these stages separate makes it much easier to identify which step a task is still missing.

## What Is a Run Instance

A run instance is "one actual execution" — it is the run record after a task has been executed, not the task definition itself. An instance typically carries run status, start and end time, error information, log entry points, and upstream/downstream impact analysis entry points.

Three non-equivalencies to remember: task exists ≠ has instances; published ≠ already has instances; empty monitor ≠ system anomaly. In a new workspace, a test workspace, or when only a draft has been created but not yet published or run, having no instances is a normal result.

## What Is a Backfill Instance

A backfill instance is a run instance triggered for a historical time range or historical data window. Regular instances typically come from normal scheduling triggers; backfill instances typically come from manually running a historical range. "Has backfill records" and "task is running normally day-to-day" should be understood separately.

## What Is Job History

Job history takes a lower-level execution perspective and answers: did this compute job actually run, how many resources did it use, how long did it take, did it error. Task instances are closer to the task and scheduling perspective; job history is closer to the underlying compute execution perspective. The two are related but are not the same object.

## What Are DQC Data Quality Rules

DQC rules are governance metadata objects. Their role is to define quality check rules for a table or data type. They are a different layer of object from business data and task instances.

Note: creating a DQC rule ≠ modifying business table data; creating a DQC rule ≠ the rule has run; having a quality rule ≠ there are already run results. Whether and when the rule runs depends on the specific trigger method and run pipeline.

## What a Task Goes Through from Creation to Running

The rough lifecycle of a task in Studio: select the correct workspace → create a task draft in a task directory → write task content → save → configure scheduling, parameters, dependencies, and cluster → publish to the scheduling system → generate run instances → view status, logs, and alerts in monitoring.

For composite tasks, the additional steps are: create the composite task object, add subtask nodes, write each subtask's content, and maintain DAG dependency edges. If governance objects are involved, you also need to create or adjust DQC rules and review the rule metadata.

## Which Actions Are Read-Only and Which Are Changes

**Read-only exploration:** Viewing task configuration, run history, monitoring, logs, DQC rules, etc. These operations generally do not change the environment and are suitable to have the Agent check the current state for you first.

**Metadata changes:** Creating a draft task, creating a composite task, creating a new task group, saving a scheduling configuration, creating a DQC rule, etc. These do not necessarily write business data immediately but will change Studio or governance objects.

**High-impact changes:** Publishing a task, unpublishing, re-running, backfilling, deleting a task, deleting dependencies, modifying the scheduling cycle, etc. These affect runs, costs, upstream/downstream pipelines, or production results, and are better suited to confirming the scope of impact before executing.

## Most Easily Confused Concept Pairs

| Concept Pair | Difference |
| --- | --- |
| Task directory vs. task group | A directory is a storage path; a task group is a business collection object |
| Composite task vs. task group | A composite task does DAG orchestration; a task group does organizational aggregation |
| Draft vs. scheduling configuration | A draft means the object and content exist; a scheduling configuration means run rules have been written into metadata |
| Scheduling configuration vs. publishing | A scheduling configuration means the task has run rules; publishing means it has entered the scheduling system |
| Task vs. instance | A task is a definition; an instance is one execution |
| DQC rule vs. DQC execution result | A rule is a governance object; an execution result is the output after the rule is triggered |

## Recommended Learning Order

If you are systematically learning Studio for the first time, build your understanding in this order: workspace → task directory → regular task → composite task and subtasks → task group → scheduling configuration → publish status → run instances and backfill instances → DQC rules.

Going back to read "task development," "task scheduling," "operations monitoring," and "data quality" documents after this will feel more coherent.

## Related Documentation

* [Studio](studio_manual.md)
* [Studio Overview](studio_overview.md)
* [Workspaces](worksheet.md)
* [Task Development Concepts](task_development.md)
* [Task Development and Scheduling](task-develop.md)
* [Composite Tasks](composite_task.md)
* [Task Groups](task_group.md)
* [Task Scheduling and Instance Execution](f6fc6447ee.md)
* [Task Scheduling Dependencies](task_scheduling_dependency.md)
* [Task and Instance Operations](task-instance-maintenance.md)
* [Backfilling Tasks](backfilling_data.md)
* [Data Quality](data-quality.md)
