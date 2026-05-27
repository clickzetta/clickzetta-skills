# Task Group Management

## Concept

A task group is a virtual business management group used within the development module to manage a list of tasks. You can use task groups to organize and arrange a series of tasks, including adding/creating task nodes, creating dependencies between task nodes, configuring task group parameters, and performing unified batch submission operations.

This article introduces how to create, edit, submit task groups, and the ability to copy task groups.

## Usage Restrictions

1. Only periodic tasks can be added/created within a task group, real-time tasks are not supported for now.

2. Task group parameters can only be used after being submitted and published, and the custom variable values configured by the task group parameters can participate in execution.

For example, if the task group parameter is aaa=2023, and the task uses this parameter, but the task group is not submitted. Then, when the task is executed periodically, the instance parameter will be displayed as empty.

3. A node task can only belong to one task group.

4. Downstream link copying: Only all nodes in the workspace can be copied. If the downstream link has task nodes from other workspaces, they will not be copied.

## Application Scenarios

### Scenario 1: Batch Copy of Tasks and Dependency Management

When you need to batch copy a group of tasks with dependencies and create new dependencies in the new tasks, you can use the task group copy function to achieve this.

![](.topwrite/assets/image_1740369112650.png =700)

Add the task group that needs to copy new dependencies to Task Group 1. After copying Task Group 1, Task Group 2 will include:

1. Batch copy of all tasks in Task Group 1.
2. Nodes with dependencies in Task Group 1 (such as nodes B, C, D, E, F) will maintain their original dependencies in Task Group 2.
3. Other nodes with dependencies in the task group but not belonging to the task group (such as nodes A, G) will maintain their original dependencies.

### Scenario 2: Task Link Transformation and Batch Modification of Custom Variables

When you need to transform any branch in the current task link and batch modify custom variables in the tasks, you can use the downstream link copy function combined with the task group function to achieve this.

![](.topwrite/assets/image_1740369139052.png =750)

On any node (the node can belong to a task group or be independent), click "Downstream Link Copy" to batch copy the node and all its downstream nodes.

## Creating a Task Group

Before creating a task group, you can plan and design a business process that meets your business needs based on your own business situation. The following are the detailed steps to create a task group.

1. Create a task group

**Method 1**: Click "Development" in the left navigation bar; hover over the +, and click "Task Group"

**Method 2**: Click "Workspace" in the left navigation bar; hover over the new button, and click "Task Group"

2. In the new task group dialog box, enter the task group name

3. Click OK

After creation:

* You can manage task nodes within the current task group, including creating/adding existing tasks to the task group
* After all tasks in the task group are developed, you can directly submit the task group to the production environment.

## Editing a Task Group

Users can design and manage task nodes and dependencies within the task group in both list and DAG modes.

1. Create/Add Nodes: Both modes support creating new task nodes in the task group or adding existing tasks to the task group.

* **DAG Mode**

  * Add Existing Tasks: Click "Add Existing Tasks" on the right, then drag tasks from the list to the DAG canvas area;
  * Add New Tasks: Under "Add New Tasks", drag any task node to the canvas area, and a creation pop-up window will appear. After entering the task name and directory, a new node will be successfully created in the task group.

In DAG mode, click "Added Tasks" at the bottom right to highlight the task node in the diagram.

* **List Mode**

  * Click the "Add" button at the top right of the list mode, and choose to add an existing task or a new task.

After successfully creating/adding a node, you need to enter the node's operation interface to edit the code.

2. Create Dependencies Between Tasks:

* In DAG mode: You can set node scheduling dependencies by dragging dependency lines. You can also manually edit node dependencies by entering the node's scheduling configuration interface.
* In list mode, the business process of newly created nodes can set node scheduling dependencies based on code lineage relationships.

3. Task Group Parameters: Global parameters under the task group will automatically apply to task nodes that reference the task group parameters after the task group is submitted to the production environment. Task nodes submitted before the task group parameters take effect need to be updated and submitted to reference the parameters.

* Click the "Parameters" tab in the task group operation area to enter the task group parameter configuration interface.
* Click the new button, and enter the parameter name and parameter value in the pop-up window. For details on built-in parameter values, see [Task Parameters](task_param.md)

How to use task group parameters after creation:

* Enter ${task group parameter name} in the SQL code of the task node, or enter the parameter name in the parameter configuration of the scheduling configuration;

* Select the task group parameter from the "Value Source" dropdown

After creating and referencing the task group parameter:

* After the task group is submitted to the production environment, the applied task nodes can use the parameter values of the task group parameters
* If the changed task group parameters need to take effect in the task node, the task node needs to be resubmitted

### Batch Submit Scheduling Time

You can use the function of batch editing scheduling time to batch modify the scheduling time of all (or selected) tasks in the task group. This reduces the operational cost of configuring each one individually. The specific operations are as follows:

1. Click Batch Edit Scheduling Time

* In DAG editing mode: When the mouse hovers over the batch button, select "Edit Scheduling Time"
* In list mode: After selecting the target tasks that need to be batch modified, click Edit Scheduling Time.

2. Batch Edit Scheduling Time
   Select the scheduling time for batch modification. The operation here is the same as the scheduling configuration in task scheduling. For specific operations, refer to [Task Development Scheduling](taskdevelop.md)

3. Confirm and submit the batch operation

## Submit Task Group

After the task group is edited and created, the task group needs to be submitted to the production environment before the tasks it manages can reference the parameter information within the task group. At the same time, the ability to batch submit task nodes is provided within the task group.

1. Click the submit button in the upper right corner to pop up the task group submission window, which also supports batch submission of the task list within the task group.

2. In DAG diagram mode, when the mouse hovers over the batch button, the batch submit tasks are displayed. This function only supports batch submission of tasks within the task group and will not submit the parameters and management information of the task group itself to the production environment.

## Related Issues

Q1: Why can't the submit button be clicked again after the task group is submitted

After the task group is submitted, if no changes have occurred, that is, before the status changes to the submitted with modifications status, it cannot be submitted again. If you need to batch submit the task information within the task group, you can submit it in two ways

Option 1: Directly operate the submission within the task

Option 2: In the DAG diagram mode of the task group, click Batch Submit Tasks under Batch Operations

Task group status change conditions:

* Add or delete tasks within the task group
* Add, delete, modify, or query task group parameters

^
