# Composite Task

A composite task is a special task type that enables **unified scheduling configuration, parameter management, and operational control** by encapsulating multiple periodic tasks (such as offline synchronization and SQL tasks) as an independent unit, while establishing dependencies with other regular nodes. This task type is suitable for business scenarios that require batch task flow management and unified scheduling cycle control (such as incremental computation and cross-task coordination). When comparing composite tasks with [task groups](https://claude.ai/chat/task_group.md), the following core differences exist:

* Task groups are a logical management concept that allows multiple tasks to be placed within a group for unified display and orchestration. Composite tasks are task type entities that exist at the same level as regular SQL tasks. Composite tasks can be added as elements within task groups.
* From an external perspective, a composite task appears as a single entity, but internally it contains one or more subtask nodes (these subtasks can be various periodic scheduling tasks such as SQL tasks, offline synchronization tasks, etc.).
* Composite tasks support unified scheduling time configuration, with all internal subtask nodes scheduled at the same frequency based on this scheduling time. This is particularly suitable for data processing pipelines where all task nodes have identical data freshness and consistency requirements. Task groups do not support scheduling time property configuration.

## Quick Start: Creating a Composite Task

The creation process for composite tasks is very similar to that of regular periodic SQL tasks.

### Creation Entry Points

Composite tasks can be created through the following paths:

* Task Development: Task Tab → New Task → Select "Composite Task"

  ![](.topwrite/assets/image_1759992445081.png =337)

* Task Group Details Page: Within Task Group → Add New Task → Select "Composite Task"

  ![](.topwrite/assets/image_1759992517831.png =680)

* Workspace: Top Navigation Bar → New Task → Select "Composite Task"

  ![](.topwrite/assets/image_1759992544546.png =680)

### Basic Information Configuration

In the composite task creation dialog, similar to other regular SQL tasks, fill in the required information:

* Task Name: Required.

* Folder: The folder where the task will be placed; must be under a folder. Required.

* Task Group: Whether to place it in a task group; if needed, select the specific task group name. Placement in a task group is not mandatory.

## Core Feature Operations Guide

### Subtask Management (Canvas Mode)

Composite tasks currently use a **canvas** (DAG diagram) to display subtask nodes and support the following operations:

![](.topwrite/assets/image_1759992832265.png =680)

#### Adding Subtasks

* **Entry Point**: Canvas Toolbar → "New Subtask" → Select Task Type (only periodic tasks are supported: offline synchronization, SQL, etc.; **real-time tasks are not supported**). Subtasks can be added to the composite task by clicking on the task type or dragging and dropping.
  ![](.topwrite/assets/image_1759992919223.png =500)

* **Default State**: Newly added subtasks have no dependencies by default and require manual dependency configuration (through canvas connections or subtask detail configuration).

#### Editing Subtasks

* **Method**: When adding a subtask node, the system defaults to entering the subtask's detail page for convenient code writing and scheduling configuration.

  * Double-click on a subtask → Enter the regular node editing page (reuses existing editing functionality)

* **Restrictions**: To ensure proper execution after composite task submission, subtasks do not support independent saving of incomplete work. All required attributes (such as code, cluster, scheduling properties) must be filled in before saving. When exiting subtask editing, ensure this information is complete and properly saved.

#### Dependency Orchestration

* **Configuration Within Subtasks**: Click on "Scheduling" in the subtask → Set upstream subtask dependencies in "Scheduling Dependencies".
* **Canvas Connections**: On the composite task's DAG canvas, select the source node → Drag a connection to the target node → Establish "upstream→downstream" dependency. Dependency relationships can also be removed by operating on the connection lines.

#### Canvas Tools

* **Auto Layout**: Toolbar → "Auto Layout" → Optimize DAG display according to dependency relationships
* **Zoom/Refresh**: Toolbar → "+/-" to adjust canvas size, or "Refresh" to reset view

### Scheduling Configuration (Global and Local Combined)

The scheduling strategy for composite tasks is managed through the coordination of **global configuration** (composite task level) and **local configuration** (subtask level). The overall approach is that subtasks inherit the composite task's global configuration by default, but also support individual local configuration. When local configuration exists, it takes precedence. Key configuration items are as follows:

| Configuration Item | Global Configuration (Composite Task)                                   | Local Configuration (Subtask)                                                                       |
| ------------------ | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Scheduling Time    | Required, supports Cron expressions (subtasks cannot set independently) | None (subtasks follow the composite task's global scheduling time for synchronous execution)        |
| Instance Rerun     | Global setting (rerun count, interval), subtasks inherit by default     | Optional override of global settings (only supported for specific task types such as SQL)           |
| Task Priority      | Global setting (default value)                                          | Optional individual setting (overrides global, only supported for SQL nodes)                        |
| Self-dependency    | Global setting (controls composite task cycle dependency)               | None (subtask self-dependency is indirectly achieved through composite task global self-dependency) |

**Example**: If the composite task global setting is "3 reruns with 5-minute intervals," a subtask can individually configure "5 reruns," resulting in the actual configuration of "5 reruns with 5-minute intervals" for that subtask.

### Parameter Management (Composite Task → Subtask Propagation)

#### Defining Parameters

* **Entry Point**: Composite Task Details Page → Click "Parameters" → Add parameters in the dialog (e.g., `composite_task_param`):

  ![](.topwrite/assets/image_1759993247775.png =480)

  ![](.topwrite/assets/image_1759993224632.png =680)

* **Scope**: Valid only within the current composite task; parameters are isolated between different composite tasks.

#### Referencing Parameters

In the subtask's parameter configuration, if the parameter name matches a parameter name defined in the composite task, the system automatically recognizes it and prompts for source selection. To use the globally defined composite task parameter, select "Composite Task" as the value source; otherwise, select "Task".

![](.topwrite/assets/image_1759993327944.png =680)

In subtask code, parameters can be referenced using `${parameter_name}`. **Example** (SQL subtask):

```
SELECT * FROM user_log WHERE dt = '${composite_task_param}'
```

## Advanced Operations: Saving and Submitting

### Saving Composite Tasks

* Composite tasks currently do not support global unified saving of subtask nodes. Please operate on individual subtasks to ensure code, scheduling configuration, and other information are saved before submitting the composite task.

### Submitting Composite Tasks

* **Purpose**: Enables submission of the composite task and all internal subtasks to the production environment for periodic scheduled execution, generating a corresponding "submission version".

* **Entry Point**: Composite Task Details Page → "Submit"

## Operations and Monitoring

### Composite Task Operations

Composite tasks are displayed in the operations center alongside other periodic tasks and support similar operations such as pause, backfill, and offline.
![](.topwrite/assets/image_1759994080395.png =680)

| Operation     | Description                                                                                                                                                                      |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pause/Resume  | After pausing, the composite task and subtasks stop scheduling; after resuming, execution continues according to current configuration                                           |
| Data Backfill | Select time range → Composite task generates backfill instances as a whole according to scheduling rules (including all subtask instances)                                       |
| Offline       | After going offline, the task no longer schedules; check for downstream dependencies (cannot go offline if downstream exists; use offline with downstream functionality instead) |

### Composite Task Instance Operations

In the Instance Operations tab, composite task instances can be viewed alongside other periodic task instances, with support for operations such as rerun and mark as failed, as shown below:
![](.topwrite/assets/image_1759994024456.png =680)

#### Status Monitoring

* **Overall Status**: Composite task instance status is comprehensively determined by subtask statuses, with the following states: Not Started (all subtasks not started), Running (any subtask running), Succeeded (all subtasks succeeded), Failed (at least one subtask failed)
* **Drill-down View**: Click on Instance ID → Enter subtask instance DAG page to view runtime details for each subtask (including logs and status)

#### Instance Operations

| Operation                | Supported States                      | Behavior Description                                                                                                                              |
| ------------------------ | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Rerun                    | Any terminal state (failed/succeeded) | Reruns entire composite task; subtasks generate new instances according to their respective rerun rules (partial subtask selection not supported) |
| Mark Success/Mark Failed | Not Started/Terminal State            | Forces composite task and all subtask instance statuses to change to succeeded/failed                                                             |
| Terminate                | Running                               | Terminates all running/not started subtask instances, setting status to failed                                                                    |

### Composite Task Monitoring and Alerting

In monitoring and alerting, composite tasks are categorized under periodic scheduling tasks. Existing monitoring items such as "Task Instance Execution Failure" and "Periodic Task Instance Completion Time" apply to them as well. Similar to regular SQL periodic tasks, monitoring rules can be configured to monitor their execution status and duration.
![](.topwrite/assets/image_1759994186179.png =680)

### Composite Task Triggered Quality Rule Validation

When configuring data quality rules, composite tasks can be selected as the scheduling trigger object in the rule execution trigger method, as shown below. Specific subtasks can be selected for triggering; if "Subtask" is left blank, the trigger occurs after the entire composite task execution completes.
![](.topwrite/assets/image_1759994260695.png =680)

## Important Considerations

1. **Type Restrictions**: Subtasks within composite tasks only support periodic tasks (offline synchronization, SQL, etc.); real-time tasks (multi-table real-time synchronization, Continuous Jobs, etc.) cannot be added.
2. **Parameter Scope**: Composite task parameters are only visible internally and cannot be used by other composite tasks. For cross-composite task parameter sharing, use task group parameters or similar mechanisms.
3. **Version Management**: Composite tasks only support "submission versions" (no saved versions) and do not currently support version rollback.
4. **Task Dependencies**: Within task groups, composite tasks exist as complete entities; internal subtasks cannot be added individually to the task group. Dependency relationships exist between the composite task as a whole and other tasks. Internal subtasks of a composite task cannot depend on other tasks, nor can they be depended upon by other tasks.

^
