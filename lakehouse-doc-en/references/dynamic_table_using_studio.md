# Develop Monitoring Dynamic Tables Using Studio
**[Preview Release] This feature is currently in an invitation-only preview stage. If you would like to try it, please contact Singdata Technology through the contact information on the official website.**
Lakehouse Studio provides an integrated web work environment for data development, job run monitoring, and anomaly alert notifications. Using the Web-IDE, you can develop dynamic table models and submit them to the target environment for execution; monitor the running status of dynamic tables through the task operation and maintenance module, or start and stop operations as needed; at the same time, you can use the monitoring and alert module to configure monitoring rules and alert notifications for dynamic tables to promptly detect task anomalies.

## Develop and Deploy Dynamic Tables Using Web-IDE

The development process of dynamic tables in Web-IDE is assisted by a visual wizard to help users write the necessary content to create dynamic tables. For example: the schema where the dynamic table is located, the name of the dynamic table, the refresh cycle, the query logic of the dynamic table, etc. After completing the development of the dynamic table script, when executing the task "submit", the system will create the dynamic table at the target location based on the script content, and the refresh strategy configuration of the dynamic table will be automatically scheduled, thereby achieving the deployment and launch of the dynamic table task.

* Step 1: Create a new dynamic table task

You can add a "dynamic table" type task by creating a new task in the Studio IDE development environment.
![](.topwrite/assets/create_dt_task.png)

Specify the task name and save location for the task code when creating a new task.
![](.topwrite/assets/studio_dt_02_naming.png =280)

* Step 2: Name the dynamic table and write the SELECT query statement for the dynamic table

First, fill in the schema location where the dynamic table will be saved after submission and the name of the dynamic table.
![](.topwrite/assets/3_naming_dt.png)

Next, write and test the query statement for the dynamic table in the SQL code area.

Write the SELECT statement for processing and transformation in the SQL code area, set the name of the cluster to run the SQL (when the dynamic table is deployed and running, this cluster will be used by default to run the refresh task), and you can also test run the SELECT statement using the run button to ensure the correctness of the processing logic.
![](.topwrite/assets/4_dev_dt.png)

Finally, verify the syntax correctness of the query statement through the Explain button and save the model definition of the dynamic table.

Click the button to check the syntax correctness of the SELECT query, check whether the field names and data types meet expectations. After confirming correctness, click the "OK and Continue" button in the pop-up window, the system will save the definition of the dynamic table and exit the SQL code editing state.
![](.topwrite/assets/5_verify_schema.png)

* Step 3: Modify and adjust the dynamic table configuration and submit for deployment

After completing the development of the dynamic table SQL code and exiting the SQL editing mode, you will see the default configuration including basic information of the dynamic table, running parameters, SQL code, dynamic table fields, dynamic table partitions, and buckets.
![](.topwrite/assets/6_dt_config.png)

Before submitting the dynamic table model definition for deployment to the Lakehouse data environment, you need to check and modify the following configuration information according to business needs to meet production requirements. The following are the configuration items supported for adjustment and modification by the dynamic table, please configure as needed.

| Configuration Item | Default Value | Configuration Description                                                                                                                                    | Example                                        |
| ------------------ | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Dynamic Table Lifecycle | Permanent       | Optional. You can choose to specify the data lifecycle of the dynamic table.                                                                                 | ![](.topwrite/assets/7_dt_lifecycle.png) |
| Person in Charge | Task Script Creator | Optional. Can adjust the overall person in charge of the task. | |
| Dynamic Table Description | None | Optional. Add comments for the dynamic table. | |
| Running Cluster | Cluster name specified during IDE development | Optional. Based on the cluster planning of the deployment environment, you can choose other computing clusters to run the dynamic table refresh task. | ![](.topwrite/assets/8_dt_vc.png) |
| Refresh Method | Manual Refresh | Optional. ***It is recommended to choose the automatic refresh method in production.*** Currently supports scheduling strategies set at intervals of minutes, hours, or days, with a minimum scheduling interval of 1 minute. | ![](.topwrite/assets/9_dt_vc.png) |
| Parameter Configuration | None | Optional. Advanced parameter settings for dynamic table operation, only needed in specific optimization scenarios (usually provided by the platform for specific scenarios), no need to set by default. | ![](.topwrite/assets/10_dt_para.png) |
| SQL Code | Last saved code content | Optional. When you want to adjust the SQL code after saving, you can modify and save it through the edit mode. | ![](.topwrite/assets/11_dt_code.png) |
| Edit Fields | None | When editing fields, you can set: * Field comments. Add comments to fields, set partition fields. Add specific fields as partition fields, supporting regular partition fields, Transform partitions, set dynamic table bucket fields and quantities. Add specific fields as bucket fields and set the number of buckets. After enabling bucket settings, the default number of buckets is 256, set sorting fields. You can specify one or more fields as sorting fields and specify the sorting method. | ![](.topwrite/assets/12_dt_field.png) |

* Step 4: Submit and deploy the dynamic table model to the target environment

After completing SQL development and dynamic table configuration, you can view the complete DDL definition of the dynamic table model through "DDL Preview".

![](.topwrite/assets/13_dt_ddl_preview.png)

After confirming that it meets expectations, you can click the "Submit" button on the right side of the dynamic table task, and the system will pop up a comparison with the last saved code version:

![](.topwrite/assets/14_dt_submit.png)

After confirming the submission, your model development content will finally be executed and the dynamic table data object will be created in the Lakehouse target data environment through DDL commands. The Lakehouse system will automatically schedule execution according to the refresh strategy of the dynamic table.

## Monitor Dynamic Table Refresh and Manage Task Start/Stop

### Dynamic Table Monitoring List
By successfully submitting and deploying dynamic table tasks through the Studio Web-IDE, you can view the running status of dynamic tables on the "Dynamic Table" TAB page under the "Task Operations" menu in "Operations Monitoring". Currently, **the operations module only supports managing tasks created by creating new dynamic table nodes through the Web-IDE, and does not support viewing dynamic tables manually created using SQL commands directly (you can still monitor dynamic table refresh tasks through SHOW DYNAMIC TABLE REFRESH HISTORY for these objects**).

Below is the information provided on the dynamic table operations monitoring list page.
![](.topwrite/assets/15_operation_dt_list.png)


**List Header Meanings**

* Task Name: The task name specified when the user creates a new dynamic table node
* Dynamic Table Name: The name of the dynamic table
* Task Status: The scheduling status of the dynamic table. Scheduling statuses include normal scheduling, paused, and unscheduled
* Schema: The schema of the dynamic table
* Action Buttons: Supports pausing scheduling, manual refresh, and offline operations for the dynamic table. Note that the offline operation means the dynamic table will be deleted

**Filter Options**

* Supports searching by task name, filtering by scheduling status, and filtering by dynamic table schema
* More filter options support filtering by owner and dynamic table creation time

Clicking on the specified dynamic table task name allows you to view the upstream dependencies of the dynamic table, helping you better understand the data flow and the interactions between tasks. Additionally, you can view the refresh history of the dynamic table to track the execution status of tasks and see if incremental refreshes have been performed.

### Specified Dynamic Table Task Execution Details

#### Task Details

* You can view the upstream dependencies of the dynamic table. Currently, only upstream can be viewed, downstream cannot be viewed. Click to expand upstream
* Top edit button, jump to data development for editing
* Top pause button, pause the scheduling of the dynamic table
* Top manual refresh button, manually trigger the dynamic table to execute the refresh command
* Top offline button, offline operation means the dynamic table will be deleted
![](.topwrite/assets/16_DT_Task_Detail.png)

#### Node Code

View the creation statement of the dynamic table.

![](.topwrite/assets/17_DT_Task_Code.png)

#### Operation Log

Records the operation audit events during the lifecycle of the dynamic table task from deployment to offline. Includes task submission online, pause scheduling, resume scheduling, manual refresh, offline, etc.

![](.topwrite/assets/18_DT_Operation_Log.png)

#### Refresh History

The refresh history provides real-time dynamic table refresh execution history. Based on the refresh history, you can view the success status of refresh tasks and key processing metrics.

**List Header Meanings**

* Start Time: The start time of each dynamic table refresh execution
* Refresh Duration: The time taken to execute the dynamic table refresh
* Job Status: The execution status of the dynamic table
* Job ID: The task ID of the dynamic table execution, you can jump to the job details through the ID to view the execution plan of the dynamic table
* Added Rows: The number of rows added by incremental refresh
* Deleted Rows: The number of rows deleted by incremental refresh, such as data deleted from the base table
* Dependent Tables: The tables that the dynamic table depends on during refresh

**Filter Options**

* Supports searching by job ID
* Supports filtering by duration, job status, execution time, and cluster
![](.topwrite/assets/19_dt_refresh_his.png)

# Monitoring Alerts

**Monitoring alerts only support monitoring tasks created through new dynamic nodes and cannot view dynamic tables submitted through ordinary SQL scripts or SQL command lines**.

* Supports dynamic table refresh timeout alerts by configuring runtime monitoring for dynamic table refresh timeouts

  * Workspace: For tasks created and submitted through **dynamic table nodes** in the entire workspace
  * Task Name: Monitor a single dynamic table node
  * Owner: Monitor dynamic tables owned by the specified owner

* Supports dynamic table refresh failure alerts

  * Checks the number of dynamic table refresh failures at a specified time, and triggers an alert if the threshold is reached


## Constraints and Limitations

Studio currently only supports monitoring and configuring alerts for dynamic tables developed and deployed through the Web-IDE in the "Operations Monitoring" module. It does not support visual monitoring and alert notifications for dynamic tables created directly through the CREATE DYNAMIC TABLE SQL statement.