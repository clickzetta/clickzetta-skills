# Task Development Overview

The task development module is a visual development page provided by Singdata Lakehouse for developers. In this module, you can organize and orchestrate tasks, develop task logic, configure scheduling, run tests, and submit and publish tasks.

## Development Concepts

| **Concept** | **Definition** |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Task | Simple node: a single, concrete task type, such as SQL or Python. |
| | Complex workflow node: a group of nodes composed of multiple individual nodes, such as a composite node. Parameters and scheduling configuration for complex workflow nodes are managed centrally. |
| Task Group | A task group is a virtual management concept provided by Singdata Lakehouse. You can add tasks to a task group for centralized management, including visual drag-and-drop dependency orchestration, task group parameter configuration, batch scheduling setup, and batch submission. **Note**: If you need to manage a group of tasks using a DAG-style drag interface, or copy and refactor a batch of task pipelines, the task group feature is recommended. |

## Dependencies: Node-level Dependencies

Dependencies are attached to nodes. Whether a node is a simple node or a complex workflow node, each acts as an independent dependency point.

**Note**: Regardless of whether you create task nodes directly under "Tasks" or manage them within a task group, dependencies always exist at the task node level — that is, dependencies are between nodes. There is no concept of dependencies between task groups.

^

## Scenario Overview

- You can create various task nodes directly under "Tasks" and establish dependencies between nodes through the scheduling dependency settings in the scheduling configuration.
- You can also create new nodes or add existing nodes under a "Task Group" to organize and orchestrate a batch of tasks, including configuring task group-level parameters and visually dragging to set dependencies between tasks.

| **Development approach** | **Target users** | **Scenario advantages** | **Limitations and differences** |
| -------- | ---------------------- | ---------------------------------------- | --------------------------------------------------------------- |
| Create tasks directly | Teams with relatively innovative business needs or those who prefer a fast, lightweight pace. | No need to build complex business relationships — just set up node dependencies and get the pipeline running quickly. Ideal for fast-moving scenarios. | Does not support batch operations, such as bulk modification of task scheduling times or compute clusters. |
| Manage tasks within a task group | Mature, standardized data warehouse teams that organize work around business domains. | Manage a related batch of task nodes by business scenario, with support for visual drag-and-drop dependency configuration. | Real-time tasks are not currently supported in task groups. A task node can only belong to one task group. Task group parameters only take effect after the task group is submitted. |

^

### Glossary

#### Task Group

A task group is a virtual management concept provided by Singdata Lakehouse. You can add tasks to a task group for centralized management, including visual drag-and-drop dependency orchestration, task group parameter configuration, batch scheduling setup, and batch submission.

- **Note**: If you need to manage a group of tasks using a DAG-style drag interface, or copy and refactor a batch of task pipelines, the task group feature is recommended. For more details, see [Task Group](task_group.md).

#### Task

Singdata Lakehouse provides several types of task nodes, including real-time multi-table sync, offline sync, real-time sync, SQL development, Python, Shell, virtual nodes, and more. Choose the appropriate task type based on your business needs.

#### Parameters

- **Task group parameters**: Parameters created within a task group, used for global management of tasks inside that group.
- **Scheduling parameters**: Parameters used during scheduled task execution.
- **Temporary parameters**: Parameters used during ad-hoc task execution.

#### Scheduling Configuration

- Currently, only periodic scheduling is supported.
- **Dependency method**: Interval dependency — the system determines whether upstream and downstream task instances overlap by comparing their start and end time ranges. For more on dependency relationships, see [Task Scheduling Dependencies](task_scheduling_dependency.md).
