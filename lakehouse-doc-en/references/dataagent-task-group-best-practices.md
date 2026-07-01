# Data Engineering Agent Task Group and Composite Task Best Practices

This guide summarizes recommended practices for task groups, composite tasks, subtask orchestration, and dependency maintenance in the Data Engineering Agent, based on actual product operations. It focuses on the high-frequency questions: when to use a task group, when to use a composite task, and how to maintain dependencies.

## Explore First, Then Build the DAG

In task group and composite task scenarios, the most common inefficiency is immediately having the Agent create nodes and connect dependencies before confirming what the current objects actually are.

A more stable sequence is:

- Confirm whether the current object is a task group, composite task, or existing subtask
- Confirm whether the current directory has existing orchestration objects that can be reused
- Confirm whether the DAG is empty, how many nodes exist, and how many edges exist
- Then decide whether to add nodes, delete edges, or rebuild dependencies

This type of scenario is especially suited to an exploratory start — if the object is misidentified, subsequent orchestration actions easily end up in the wrong place.

## Distinguish Between Three Object Types First

In Studio, multi-task orchestration involves at least three types of objects: task groups, composite tasks, and subtasks within composite tasks. They serve different purposes.

**Task groups** are more of an organizational and governance object. Task groups are created separately in the **Task Groups** tab — the creation dialog has only one field: **task group name**. This means a task group itself is not an SQL/Python/Shell/Flow task type but an independent organizational and governance object used to collect and view a set of related tasks.

**Composite tasks** are the actual task objects that host DAG orchestration, accessible via **Other → Composite Task**. The creation dialog includes three fields: **task name**, **folder**, and **task group**. A composite task itself is an orchestration object that lives in the task directory. It can exist independently or be used in combination with task group relationships.

**Subtasks** are the execution nodes within a composite task. After adding one, the system opens the corresponding subtask editor and requires the user to provide code, parameters, scheduling, and other content — they are not merely canvas blocks. Common types include SQL, Python, Shell, JDBC, offline sync, branch task, virtual task, Databricks SQL, and Databricks Notebook.

## When to Use a Task Group vs. a Composite Task

Recommended selection criteria:

| Scenario | Recommended object |
|---|---|
| Group a set of tasks by theme, project, or pipeline for unified management and viewing | Task group |
| Define a clear execution order and dependency relationships between multiple steps | Composite task |
| Host specific execution logic within an orchestrated pipeline | Subtask inside a composite task |

Simply put: task groups lean toward "organization and governance"; composite tasks lean toward "orchestration and execution." If you only need to store and find tasks, use directories first — no need to build a composite task from the start. If you already have clearly defined pre- and post-step flows that require an actual DAG, use a composite task.

## Important Notes When Creating Composite Tasks

**The folder must truly be selected.** In the composite task creation form, the **folder** field is not complete just because a tree node appears highlighted. In practice, only by clicking the actual text or content area of a specific folder node will the form truly recognize that directory. Otherwise, even if the tree area shows a selected style, an error may still occur:

```text
Folder cannot be empty
```

Do not click only on empty areas of the tree; do not assume selection based on node highlight alone. When creation fails, first check whether the folder field was truly bound.

**`Task group = Yes` does not mean "create a task group."** In the composite task creation dialog, **task group** may default to `No`. Switching to `Yes` causes the interface to display "Please select a task group" — this expresses whether the current composite task needs to be attached to an existing task group, not that the composite task itself is being created as a task group. To actually create a new task group, go to the **Task Groups** tab and create one separately.

## Correct Workflow for Subtask Orchestration

**Create nodes first, then fill in content.** When adding an SQL subtask inside a composite task, the actual flow is: click `SQL` in the canvas sidebar → enter subtask name → after creation, open the subtask editor → write SQL → save subtask content → return to the parent composite task to continue orchestration. Adding a subtask to the DAG only completes "node object creation." Whether the SQL/Python/Shell code is written is a separate layer of work; a prompt appears if you exit without saving subtask content.

**Do not mistake "node is visible" for "task is fully configured."** Even if a node appears in the DAG, the subtask code may be unsaved, the subtask scheduling config may be empty, subtask parameters may be unconfigured, and composite task dependencies may not yet be established. Composite task sign-off cannot rely solely on "there are two boxes in the canvas."

## How to Maintain Dependencies

In a composite task, the pre/post-order relationship is not a hidden form field — it is an actual DAG edge on the canvas. Dependencies are a real, persistently saved orchestration structure. When you switch tabs and come back, dependency edges are still there.

Recommended sequence: create the composite task object first, then create all needed subtask nodes, fill in minimal content for each subtask, and finally configure dependency edges. This stabilizes the node set first, then adjusts the DAG structure — less rework, and easier to confirm which nodes are missing content and which are just not yet connected.

Dependency edges can be deleted and recreated. After deletion, the DAG edge count drops to 0; after recreation, a new edge is generated. This means composite task dependencies are not a one-time fixed configuration — they can be continuously maintained. Reordering nodes, splitting branches, merging steps, and replacing upstream/downstream are all normal draft-phase operations.

## Recommended Combination of Task Groups and Composite Tasks

A stable approach: use task groups to organize a category of tasks or a business pipeline, use composite tasks to host the process within that needs a clear execution order, and use subtasks to host the specific execution logic for each step.

For example:
- Task group: Marketing Daily Summary
- Composite task: Marketing Daily Summary Main Pipeline
- Subtasks: Detail Cleaning SQL, Aggregation SQL, Result Validation SQL

This gives clear organizational hierarchy, clear orchestration boundaries, and easier governance, publishing, and troubleshooting later.

## Common Misunderstandings

**Treating a task group as a composite task**: task groups are not aliases for composite tasks. Task groups lean toward being organizational objects; composite tasks lean toward DAG orchestration objects.

**Treating a composite task as "just a shell"**: a composite task is not a pure container. Once you enter DAG configuration with subtasks and dependencies, it becomes a real execution orchestration structure.

**Only checking "creation succeeded" without checking actual DAG state**: a composite task being created successfully does not mean subtasks are created, subtask content is complete, or dependencies are bound. You must return to the task tree and canvas to check the actual structure.

**Rushing to schedule and publish**: the most common problem in the draft phase is not "can it be published" but rather disorganized node names, incomplete subtask content, wrong dependencies, and wrong node types. A more stable order is to get the DAG structure right first, then fill in code and parameters, and finally address scheduling and publishing.

## Recommended Working Habits

**Use dedicated directories for testing.** Put composite task drafts and task group drafts in clearly labeled test or temp development directories to avoid mixing them with formal pipelines.

**Node names should reflect the step's role.** Names like "order_detail_cleaning," "order_daily_aggregation," and "result_validation" are far more readable than `step1`, `step2` when reviewing a DAG later.

**Complete the minimum viable loop first, then expand.** Build the smallest verifiable loop first: 2 nodes, 1 dependency edge, each node with minimal executable content. Confirm this minimal pipeline is correct, then add branches, sync steps, and quality checks.

**Re-review the DAG after every dependency change.** After adjusting dependencies, recheck the current node count, current edge count, which node comes first, which comes last, and whether any other edges were accidentally deleted. For multi-node DAGs, this step is critical.

## Recommended Agent Prompts

**Create a composite task draft:**
> Please create a composite task draft named `{composite_task_name}` under directory `{directory}`. Do not execute; do not publish. After creation, return the task ID, directory, and current DAG node count.

**Explore the current orchestration state first:**
> Please first check which composite tasks, task groups, and existing nodes are currently under `{directory or task name}`. Return the object list and DAG state only; do not execute, do not publish, do not modify configuration.

**Add nodes to a composite task:**
> Please add two SQL subtasks to composite task `{task_name or ID}`. Only create the nodes with a minimal SQL draft; do not execute, do not publish. After completion, return the node names and count.

**Configure dependencies:**
> In composite task `{task_name or ID}`, set `{node_A}` as a prerequisite of `{node_B}`. After completion, return the current dependency edge list; do not execute, do not publish.

**Review the DAG:**
> Please check the actual DAG for composite task `{task_name or ID}`. Return node count, node names, node types, and dependency edges. Explicitly state whether the DAG is empty.

**Delete a dependency:**
> Please delete the dependency edge from `{node_A}` to `{node_B}` in composite task `{task_name or ID}`. After deletion, return the current dependency edge list; do not execute, do not publish.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Task Group and Composite Task Guide](dataagent-task-group-guide.md)
- [Task Development Guide](dataagent-task-development-guide.md)
- [Scheduling and Publishing Guide](dataagent-scheduling-and-release-guide.md)
- [Safe Operation Guide](dataagent-safe-operation-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
