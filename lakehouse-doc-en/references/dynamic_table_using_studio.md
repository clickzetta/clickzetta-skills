# Developing and Monitoring Dynamic Tables Using Studio
> ⚠️ **Note**: **[Preview Release] This feature is currently in an invitation-only preview stage. To request access, contact Singdata Technology through the official website.**

Lakehouse Studio provides an integrated web environment for data development, job run monitoring, and anomaly alert notifications. Using the Web-IDE, you can develop dynamic table models and submit them to the target environment for execution. Through the task operations module, you can monitor the running status of dynamic tables and start or pause them as needed. You can also use the monitoring and alert module to configure monitoring rules and alert notifications for dynamic tables, so you can detect task anomalies promptly.

## Developing and Deploying Dynamic Tables Using Web-IDE

The dynamic table development process in Web-IDE uses a visual wizard to guide you through writing the content needed to create a dynamic table — for example, the schema, the dynamic table name, the refresh interval, and the query logic. After you finish developing the dynamic table script and submit the task, the system creates the dynamic table at the target location based on the script content and automatically schedules it according to the refresh strategy, completing the deployment.

* Step 1: Create a new dynamic table task

In the Studio IDE development environment, create a new task and select "Dynamic Table" as the task type.

![](.topwrite/assets/image_1722413586664.png)

When creating the task, specify a task name and a save location for the task code.

![](.topwrite/assets/image_1722413608121.png =280)

* Step 2: Name the dynamic table and write its SELECT query

First, fill in the schema location where the dynamic table will be saved after submission, and enter the dynamic table name.

![](.topwrite/assets/image_1722413623690.png)

Next, write and test the dynamic table query in the SQL code area.

Write the SELECT statement for your data transformation in the SQL code area, and set the cluster name to use when running the SQL (this cluster will be used by default when the dynamic table runs its refresh tasks). You can also click the run button to test the SELECT statement and verify the logic is correct.

![](.topwrite/assets/image_1722413647339.png)

Finally, use the Explain button to validate the query syntax and save the dynamic table model definition.

Click the button to check the syntax of the SELECT query and verify that field names and data types are as expected. After confirming everything looks correct, click "OK and Continue" in the pop-up window. The system saves the dynamic table definition and exits the SQL code editing state.

![](.topwrite/assets/image_1722413661168.png)

* Step 3: Review and adjust the dynamic table configuration, then submit for deployment

After completing the SQL code and exiting SQL editing mode, you will see the default configuration, including basic information, runtime parameters, SQL code, fields, partitions, and bucketing settings.

![](.topwrite/assets/image_1722413674413.png)

Before submitting the dynamic table model to the Lakehouse data environment, review and update the following configuration items to meet your production requirements.

| Configuration Item | Default Value | Description | Example |
| ------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Dynamic Table Lifecycle | Permanent | Optional. Specify a data lifecycle for the dynamic table. | ![](.topwrite/assets/image_1722413761168.png) |
| Owner | Task script creator | Optional. Reassign the task owner. | |
| Dynamic Table Description | None | Optional. Add a comment for the dynamic table. | |
| Running Cluster | Cluster specified during IDE development | Optional. Select a different compute cluster to run the dynamic table refresh task, based on your deployment environment's cluster plan. | ![](.topwrite/assets/image_1722413783296.png) |
| Refresh Method | Manual refresh | Optional. ***For production use, automatic refresh is recommended.*** Supports scheduling intervals in minutes, hours, or days, with a minimum interval of 1 minute. | ![](.topwrite/assets/image_1722413797691.png) |
| Parameter Configuration | None | Optional. Advanced runtime parameters for the dynamic table. These are only needed in specific optimization scenarios (typically provided by the platform team for particular use cases) and do not need to be set by default. | ![](.topwrite/assets/image_1722413810954.png) |
| SQL Code | Last saved code | Optional. If you want to adjust the SQL code after saving, you can edit and save it again. | ![](.topwrite/assets/image_1722413830727.png) |
| Edit Fields | None | When editing fields, you can: set field comments; designate partition fields (supporting regular partitions and Transform partitions); set bucket fields and bucket count (default is 256 buckets when bucketing is enabled); and set sort fields (one or more fields, with a specified sort order). | ![](.topwrite/assets/image_1722413842446.png) |

* Step 4: Submit and deploy the dynamic table model to the target environment

After completing SQL development and dynamic table configuration, you can click "DDL Preview" to view the complete DDL definition of the dynamic table model.

![](.topwrite/assets/image_1722413857683.png)

Once you confirm it looks correct, click the "Submit" button on the right side of the dynamic table task. The system displays a diff comparing the current content with the last saved version:

![](.topwrite/assets/image_1722413868003.png)

After confirming the submission, the system executes the DDL commands in the Lakehouse target data environment to create the dynamic table object. Lakehouse will then automatically schedule and run the dynamic table according to its refresh strategy.

## Monitoring Dynamic Table Refreshes and Managing Task Start/Stop

### Dynamic Table Monitoring List

Dynamic table tasks successfully submitted through the Studio Web-IDE can be viewed on the "Dynamic Table" tab under "Task Operations" in the "Operations Monitoring" section. Note that **the operations module only supports managing tasks created through the Web-IDE dynamic table node. It does not support viewing dynamic tables created manually with SQL commands (for those objects, you can still monitor refresh tasks using `SHOW DYNAMIC TABLE REFRESH HISTORY`)**.

The following information is available on the dynamic table operations monitoring list page.

![](.topwrite/assets/image_1722416553405.png)

**Column Descriptions**

* Task Name: The task name specified when the dynamic table node was created
* Dynamic Table Name: The name of the dynamic table
* Task Status: The scheduling status of the dynamic table. Statuses include: normally scheduled, paused, and no schedule set
* Schema: The schema of the dynamic table
* Action Buttons: Supports pausing scheduling, manual refresh, and taking the dynamic table offline. Note that taking a table offline will delete the dynamic table

**Filter Options**

* Search by task name, filter by scheduling status, or filter by dynamic table schema
* The "More Filters" panel supports filtering by owner and dynamic table creation time

Clicking a dynamic table task name lets you view its upstream dependencies, helping you understand data flow and how tasks interact. You can also view the refresh history to track execution status and see whether incremental refreshes were performed.

### Dynamic Table Task Execution Details

#### Task Details

* View the upstream dependencies of the dynamic table. Currently only upstream dependencies are shown; downstream is not available. Click to expand the upstream view.
* The Edit button at the top navigates to the data development view for editing.
* The Pause button at the top pauses the dynamic table's scheduling.
* The Manual Refresh button at the top manually triggers a refresh of the dynamic table.
* The Offline button at the top takes the dynamic table offline, which deletes it.

![](.topwrite/assets/image_1722416571859.png)

#### Node Code

View the creation statement for the dynamic table.

![](.topwrite/assets/image_1722416583152.png)

#### Operation Log

Records the operation audit events throughout the dynamic table task lifecycle, from deployment to going offline. This includes task submission, pause scheduling, resume scheduling, manual refresh, and offline operations.

![](.topwrite/assets/image_1722416592033.png)

#### Refresh History

The refresh history provides a real-time record of dynamic table refresh executions. From the refresh history, you can view the success status of each refresh and key processing metrics.

**Column Descriptions**

* Start Time: The start time of each dynamic table refresh execution
* Refresh Duration: The time taken to complete the refresh
* Job Status: The execution status of the dynamic table
* Job ID: The job ID for the dynamic table execution. Click the ID to navigate to the job details and view the execution plan.
* Rows Added: The number of rows added by the incremental refresh
* Rows Deleted: The number of rows deleted during the incremental refresh, for example when data is deleted from a base table
* Dependent Tables: The tables the dynamic table depended on during the refresh

**Filter Options**

* Search by job ID
* Filter by duration, job status, execution time, and cluster

![](.topwrite/assets/image_1722416609512.png)

# Monitoring Alerts

**Monitoring alerts only support tasks created through the dynamic table node. Dynamic tables submitted via ordinary SQL scripts or the SQL command line cannot be monitored here.**

* Supports refresh timeout alerts by configuring a runtime duration threshold to detect when a dynamic table refresh takes too long

  * Workspace: Monitors all tasks in the entire workspace that were **created through a dynamic table node** and have been submitted.
  * Task Name: Monitors a single dynamic table node.
  * Owner: Monitors dynamic tables assigned to a specific owner.

* Supports refresh failure alerts

  * Checks the number of dynamic table refresh failures at a specified time. If the count reaches the configured threshold, an alert is triggered.

![](.topwrite/assets/image_1722416626731.png)

# Relationship Between Studio Dynamic Table Tasks and Dynamic Table Objects

Studio's development module provides a task type called "Dynamic Table," which supports developing, operating, and monitoring dynamic table tasks. When you submit a dynamic table task in the "Development" module, the system simultaneously creates the corresponding Lakehouse dynamic table object based on the code definition. When you take a dynamic table task offline in the "Operations" module, the system automatically deletes the corresponding Lakehouse dynamic table object.

> ⚠️ **Note**: When creating a dynamic table using a dynamic table task in the Studio development module, the system checks whether a Lakehouse dynamic table object with the same name already exists at the target location. If one is found, the creation will fail with a duplicate name error. In this case, either rename the new dynamic table task or manually delete the existing Lakehouse dynamic table object before creating the Studio dynamic table task.

# Constraints and Limitations

The Studio monitoring and alert module does not support configuring alerts for dynamic tables created directly with the `CREATE DYNAMIC TABLE` statement. To use Studio monitoring alerts for a dynamic table, create and submit it through the "Dynamic Table" task type in the Web-IDE development module.
