# Data Supplementation Task

Data supplementation can be achieved by filling in historical or future data for a certain period, writing the data into the corresponding time partition. If there are scheduling parameters configured in the code, they will be automatically replaced with specific values based on the business time selected for data supplementation, and the corresponding time data will be written into the specified partition according to the business code logic.

## Usage Scenarios

When a new task is created and historical data needs to be processed, the data supplementation function can be used to select a certain period of history to execute the task.

When there is a problem with the data or the task is abnormal during a certain period, data supplementation can be used to regenerate instances for the abnormal historical data or tasks and execute them again, achieving the purpose of repairing historical data.

## Product Operation

###  Step One: Create a Data Supplementation Task

Click on the left navigation to Operations Monitoring -> Task Operations, select the Periodic Task tab. Then, choose any periodic task in management and click on the operation - Data Supplementation to enter the data supplementation operation interface.

Configure the corresponding operations for the data supplementation task.

Task Name: The system provides a default name, which is not currently supported for user input.

Select the task nodes included in the data supplementation task.

Include Current Node: Users can choose whether to check the current task to participate in data supplementation according to actual needs.

Include Downstream Nodes: Users can check the downstream tasks that need data supplementation according to actual needs, supporting three options: not choosing, choosing all, and customizing the range of selection.

Task Timing Time Range: When creating a data supplementation task, you can add multiple planned execution time ranges to address scenarios where you want to supplement data for multiple discontinuous periods. Currently, up to 4 planned execution time ranges are supported. Users are not allowed to select overlapping times.

Concurrency Settings: Indicates that when supplementing data for multiple periods in a row, if the concurrency is met, multiple instances of the period can run simultaneously, which can improve the efficiency of data supplementation, but will also consume more resources.

After enabling concurrent execution, the system will default to attach self-dependencies to task instances assigned to the same concurrency group.

###  Step Two: View Data Supplementation Tasks

Click on the left navigation to Operations Monitoring -> Task Operations, and select the Data Supplementation Task tab.

Basic Information: Includes concurrency grouping, target task ID, task name, workspace, whether to include downstream, status, execution order, task timing time range, submission time, submitter, etc.

Statistics Graph:

Global Statistical Information: You can see the total number of all times included in the current data supplementation task, and the execution status is given based on a daily granularity.

Granularity Effect Diagram: Provides statistical data in three granularities of year/month/day, and clicking on the statistical graph will link to the instance list below.

Year View: Hovering the mouse over the date will show the execution status of that day;

Month View: You can see the total number of instances to be executed on that day in the month view, and hovering over the calendar will show a summary of the execution status;

Day View: Supports switching between two granularities of day/1 hour, and you can see the average duration of instances under different aggregation granularities.

Instance Statistics List: By default, it displays information about all executed instances under the current data supplementation task according to the planned time. Clicking on it will jump to the instance execution details page to view dependency and other details.
