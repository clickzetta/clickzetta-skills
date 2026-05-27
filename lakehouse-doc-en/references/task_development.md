# Task Development Overview

The task development module is a visual development page provided by Singdata lakehouse for developers. In this module, users can perform operations such as task organization and orchestration, task development, operation and maintenance scheduling configuration, running tests, and submitting releases.

This document introduces the relevant concepts of task development.

### Enter Task Development

Click on the left navigation bar Development; or Workspace -> New, click the top right corner to select the correct workspace, and enter the **Development** page.

### Concept Introduction

#### Task Group

A task group is a virtual management concept provided by Singdata lakehouse. Tasks can be added to the task group for centralized management, including visual drag-and-drop orchestration of dependencies, configuration of task group parameters, batch scheduling settings, batch submissions, and other operations.

* Note: If you need to manage a group of tasks using a DAG method or copy and modify a batch of links, it is recommended to use the task group function. For more information, refer to [Task Group](task_group.md)

#### Task

Singdata lakehouse encapsulates different types of task nodes, including real-time multi-table synchronization, offline synchronization, real-time synchronization, SQL development, Python, Shell, virtual nodes, etc. You can choose the appropriate task type for development based on business needs.

#### Parameters

* Task Group Parameters: Created within the task group and used for global management of tasks within the task group.
* Scheduling Parameters: Parameters used during task invocation.
* Temporary Parameters: Parameters used for temporary execution.

#### Scheduling Configuration:

* Currently, only periodic scheduling is supported.
* Dependency Method: Interval dependency, which uses the start and end time range of the downstream task instance to overlap with the start and end time range of the upstream instance. For more dependency relationships, refer to [Task Scheduling Dependencies](task_scheduling_dependency.md)

^
