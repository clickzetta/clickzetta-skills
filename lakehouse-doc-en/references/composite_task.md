# Composite Task

A composite task is a special task type that supports encapsulating multiple periodic tasks (such as offline synchronization and SQL tasks) as an independent unit to achieve **unified scheduling configuration, parameter management, and operational control**, while establishing dependencies with other regular nodes. This task type is suited for business scenarios that require batch task flow management and unified scheduling cycle control — for example, incremental computation and cross-task coordination.

Comparing composite tasks with [task groups](task_group.md), the key differences are:

* A task group is a logical management concept that places multiple tasks in a group for unified display and orchestration. A composite task is a concrete task type entity, on equal footing with a regular SQL task. You can add a composite task as an element within a task group.
* From the outside, a composite task appears as a single unit, but internally it contains one or more subtask nodes (which can be SQL tasks, offline synchronization tasks, or other periodic scheduling task types).
* A composite task supports a unified scheduling time, and all internal subtask nodes run at the same frequency based on that schedule. This is especially useful for data processing pipelines where all task nodes have the same data freshness requirements. Task groups do not support scheduling time configuration.

## Quick Start: Creating a Composite Task

Creating a composite task is very similar to creating a regular periodic SQL task.

### Creation Entry Points

You can create a composite task through any of the following paths:

* Task Development: Task tab → New Task → Select "Composite Task"

  ![](.topwrite/assets/image_1752130018729.png =420)

* Task Group Details page: Inside a task group → Add New Task → Select "Composite Task"
  
  ![](.topwrite/assets/image_1752130033606.png =680)

* Workspace: Top navigation bar → New Task → Select "Composite Task"
  
  ![](.topwrite/assets/image_1752130048252.png =680)

### Basic Information

In the composite task creation dialog, fill in the required fields — same as for other regular SQL tasks:

* Task Name: Required.
* Folder: The folder to place the task in. Required.
* Task Group: Optionally assign the task to a task group by selecting a specific task group name.

  ![](.topwrite/assets/image_1752130064673.png =680)

## Core Feature Guide

### Subtask Management (Canvas Mode)

Composite tasks use a **canvas** (DAG diagram) to display subtask nodes and support the following operations:
![](.topwrite/assets/image_1752130101512.png =680)

#### Adding Subtasks

* **Entry point**: Canvas toolbar → "New Subtask" → Select a task type (only periodic tasks are supported: offline synchronization, SQL, etc.; **real-time tasks are not supported**). You can add a subtask by clicking the task type or dragging it onto the canvas.

  ![](.topwrite/assets/image_1752130110716.png =360)

* **Default state**: Newly added subtasks have no dependencies by default. You need to configure dependencies manually — either by drawing connections on the canvas or through the subtask detail configuration.

#### Editing Subtasks

* **How to edit**:
  * When you add a subtask node, the system automatically opens the subtask detail page so you can write code and configure scheduling settings.
  * Double-click a subtask → Opens the regular node editing page (reuses existing editing functionality).

* **Restrictions**: To ensure the composite task runs correctly after submission, subtasks cannot be saved in an incomplete state. All required fields (code, cluster, scheduling properties) must be filled in before saving. Make sure this information is complete and saved before exiting the subtask editor.

#### Dependency Orchestration

* **Configure in the subtask**: Click "Scheduling" on the subtask → Set upstream subtask dependencies under "Scheduling Dependencies".
* **Draw connections on the canvas**: On the composite task's DAG canvas, select a source node → Drag a connection to the target node → This establishes an "upstream → downstream" dependency. You can also remove dependencies by operating on the connection lines.

#### Canvas Tools

* **Auto layout**: Toolbar → "Auto Layout" → Optimizes the DAG display based on dependency relationships.
* **Zoom/Refresh**: Toolbar → "+" / "-" to adjust canvas size, or "Refresh" to reset the view.

### Scheduling Configuration (Global and Local)

The scheduling strategy for a composite task is managed through a combination of **global configuration** (at the composite task level) and **local configuration** (at the subtask level). Subtasks inherit the composite task's global configuration by default, but can also be configured individually. When a local configuration exists, it takes precedence. Key configuration items:

| Configuration Item | Global Configuration (Composite Task)                                    | Local Configuration (Subtask)                                                                        |
| ------------------ | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Scheduling Time    | Required; supports Cron expressions. Subtasks cannot set this independently. | None. Subtasks follow the composite task's global scheduling time and run at the same frequency.  |
| Instance Rerun     | Global setting (rerun count, interval). Subtasks inherit by default.     | Optional override of global settings (only supported for specific task types such as SQL).           |
| Task Priority      | Global setting (default value).                                          | Optional individual setting (overrides global; only supported for SQL nodes).                        |
| Self-dependency    | Global setting (controls composite task cycle dependency).               | None. Subtask self-dependency is indirectly achieved through the composite task's global self-dependency. |

**Example**: If the composite task global setting is "3 reruns with a 5-minute interval," and a subtask is individually configured with "5 reruns," that subtask will use "5 reruns with a 5-minute interval."

![](.topwrite/assets/image_1752130126629.png =680)

![](.topwrite/assets/image_1752130133390.png =680)

### Parameter Management (Composite Task → Subtask Propagation)

#### Defining Parameters

* **Entry point**: Composite task detail page → Click "Parameters" → Add parameters in the dialog (e.g., `composite_task_param`):

  ![](.topwrite/assets/image_1752130143435.png =680)

  ![](.topwrite/assets/image_1752130151838.png =680)

* **Scope**: Parameters are only valid within the current composite task. Parameters are isolated between different composite tasks.

#### Referencing Parameters

In a subtask's parameter configuration, if the parameter name matches a parameter defined in the composite task, the system automatically recognizes it and prompts you to select the value source. To use the globally defined composite task parameter, select "Composite Task" as the value source; otherwise, select "Task".

![](.topwrite/assets/image_1752130161305.png =680)

In subtask code, you can reference parameters using `${parameter_name}`. **Example** (SQL subtask):

```
SELECT * FROM user_log WHERE dt = '${composite_task_param}'  
```

## Advanced Operations: Saving and Submitting

### Saving a Composite Task

* Composite tasks do not currently support saving all subtask nodes at once. Save each subtask individually to ensure its code, scheduling configuration, and other settings are saved. Then submit the composite task.

### Submitting a Composite Task

* **Purpose**: Submits the composite task and all its internal subtasks to the production environment for periodic scheduled execution, generating a corresponding "submission version."

* **Entry point**: Composite task detail page → "Submit."

  ![](.topwrite/assets/image_1752130174992.png =680)

## Operations and Monitoring

### Composite Task Operations

Composite tasks appear in the Operations Center alongside other periodic tasks and support similar operations such as pause, data backfill, and offline.

![](.topwrite/assets/image_1752130184652.png =680)

| Operation      | Description                                                                                                                                                                                    |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pause/Resume   | After pausing, the composite task and its subtasks stop scheduling. After resuming, execution continues according to the current configuration.                                                |
| Data Backfill  | Select a time range → The composite task generates backfill instances as a whole according to scheduling rules (including all subtask instances).                                               |
| Offline        | After going offline, the task no longer schedules. Check for downstream dependencies — if any exist, you cannot go offline directly and must use the "Offline (including downstream)" feature. |

### Composite Task Instance Operations

In the Instance Operations tab, composite task instances are listed alongside other periodic task instances and support operations such as rerun and mark as success/failure, as shown below:

![](.topwrite/assets/image_1752130199325.png =680)

#### Status Monitoring

* **Overall status**: The composite task instance status is determined by the combined status of its subtasks:
  * Not Started: all subtasks have not started
  * Running: at least one subtask is running
  * Succeeded: all subtasks succeeded
  * Failed: at least one subtask failed
* **Drill-down view**: Click the instance ID → Opens the subtask instance DAG page to view runtime details for each subtask (including logs and status).

#### Instance Operations

| Operation              | Supported States                      | Behavior                                                                                                                                          |
| ---------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rerun                  | Any terminal state (failed/succeeded) | Reruns the entire composite task. Subtasks generate new instances according to their respective rerun rules. Partial subtask selection is not supported. |
| Mark Success/Failure   | Not Started / Terminal state          | Forces the composite task and all subtask instance statuses to change to succeeded or failed.                                                     |
| Terminate              | Running                               | Terminates all running or not-started subtask instances and sets their status to failed.                                                          |

### Monitoring and Alerts

In monitoring and alerts, composite tasks are categorized under periodic scheduling tasks. Existing monitoring items such as "Task Instance Execution Failure" and "Periodic Task Instance Completion Time" apply to composite tasks as well. You can configure monitoring rules for composite tasks the same way you would for regular SQL periodic tasks.

![](.topwrite/assets/image_1752131374833.png =680)

### Triggering Data Quality Rule Checks

When configuring data quality rules, you can select a composite task as the scheduling trigger in the rule execution trigger settings, as shown below. You can select a specific subtask to trigger the check; if "Subtask" is left blank, the check is triggered after the entire composite task completes.

![](.topwrite/assets/image_1752131279717.png =680)

## Notes

1. **Type restrictions**: Subtasks within a composite task only support periodic tasks (offline synchronization, SQL, etc.). Real-time tasks (multi-table real-time synchronization, Continuous Jobs, etc.) cannot be added.
2. **Parameter scope**: Composite task parameters are only visible within the composite task and cannot be used by other composite tasks. To share parameters across composite tasks, use task group parameters or similar mechanisms.
3. **Version management**: Composite tasks only support "submission versions" (no saved versions) and do not currently support version rollback.
4. **Task dependencies**: Within a task group, a composite task exists as a whole unit. Internal subtasks cannot be added individually to the task group, and dependencies are between the composite task as a whole and other tasks. Internal subtasks of a composite task cannot depend on other tasks in the task group, nor can they be depended upon by other tasks in the task group.

---

## Related Documentation

- [Task Parameters](task_param.md) — Concepts and configuration for composite task parameters
- [Task Parameter Syntax Reference](task_param_reference.md) — Full syntax for time expressions and built-in parameters
- [Task Group](task_group.md) — Using task group parameters to share parameters across composite tasks
- [Task Development and Scheduling](task-develop.md) — Development and scheduling configuration for SQL subtasks
