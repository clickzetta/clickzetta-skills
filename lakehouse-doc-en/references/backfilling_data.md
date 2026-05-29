# Backfilling Data

Backfilling data can be done by supplementing historical or future data for a period of time, writing the data to the corresponding time partition. If scheduling parameters are configured in the code, they will be automatically replaced with specific values based on the business time selected for data backfilling, and the corresponding time data will be written to the specified partition in combination with the business code. The specific partition written to and the code logic executed are related to the code defined in the task.

## Function Usage Scenarios

* When a new task is created and you want to process historical data, you can use the data backfilling function to select a historical time period to execute the task;
* If there is a problem with the data or the task is abnormal during a certain period, you can use data backfilling to regenerate and execute instances of the historical abnormal data or task to achieve the purpose of repairing historical data.

## Product Operation

### Step 1: Create a Backfilling Data Task

1. Click on the left navigation **Operations Monitoring -> Task Operations**, **select the Periodic Task** Tab. Choose any of the periodic tasks under management, click on Operation - Data Supplement, and enter the data supplement operation interface.
2. Configure the corresponding operations for the data supplement task

* Task Name: System default name, user input is not supported for now

* Select the task nodes included in the data supplement task

  * Include current node: Users can choose whether to check the current task to participate in the data supplement based on actual needs.
  * Include downstream nodes: Users can check the **downstream task links** that need data backfilling based on actual needs. It supports three options: no selection, select all, and custom selection range.

* Task scheduling time range: When creating a data supplement task, it supports adding multiple planned execution time ranges to solve the scenario of wanting to supplement multiple non-continuous times. Currently, it supports adding up to 4 planned execution time ranges. Users are not allowed to select overlapping times.

* Concurrency settings: Indicates that when supplementing data for multiple consecutive periods, if the concurrency number is met, multiple period instances can run simultaneously, which can improve the efficiency of data backfilling but will also consume more resources.

  * After enabling concurrent execution, the system will by default attach self-dependency to task instances allocated within the same concurrency group.

### Step 2: View the Backfilling Data Task

1. Click on the left navigation **Operations Monitoring -> Task Operations**, **select the Data Supplement Task** Tab.

2. Basic Information: Includes concurrency group, target task ID, task name, workspace, whether it includes downstream, status, execution order, task scheduling time range, submission time, submitter, etc.

3. Statistics Chart:

* Global Statistics: You can see the total number of all times included in the current data supplement task and give the execution status based on the day granularity.

* Effect Chart by Granularity: Provides data statistics at year/month/day granularity. Clicking on the statistics chart will link to the instance list below.

  * **Year View**: Hovering over the date shows the execution status of that day;

  * **Month View**: You can see the total number of instances to be executed on that day in the month view, and hovering over the calendar shows the execution status summary;

  * **Day View**: Supports switching between day/1-hour granularity, showing the average execution time of instances under different aggregation granularities.

4. Instance Statistics List: By default, it displays the information of all execution instances under the current data supplement task according to the planned time. Clicking can jump to the instance execution details page to view dependency relationships and other details.

^
