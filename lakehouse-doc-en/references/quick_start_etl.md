# Getting Started: How to Quickly Configure, Orchestrate, and Schedule ETL Pipelines

## Applicable Scenarios

One of the main tasks of a data warehouse engineer is building an offline data warehouse, i.e., creating and maintaining periodically scheduled ETL pipelines. This document provides an overview of how to configure and orchestrate ETL tasks based on Lakehouse Studio and configure scheduling properties so that the entire ETL pipeline can be scheduled and run periodically according to dependencies.

## Prerequisite Reading

Before reading this guide, it is recommended to complete reading and understanding the following documents:

* [Lakehouse Product Introduction](datalake_overview.md)
* [Key Concepts](key-concepts.md)
* [Lakehouse Studio Quick Tour](lakehouse-studio-101.md)

## Operation Guide

In [Getting Started: How to Quickly Create a Sync Task to Import Data](quick_start_batch_sync_data.md), we already created a data sync task. This document will demonstrate, by example, how to create a SQL processing task and make it depend on the data sync task, thereby building an ETL pipeline, and configure scheduling to run periodically.

### Usage Notes

Users with `workspace_admin` or `workspace_dev` role permissions are required to use the features of task development, submission and publishing, and operations center.

### Creating a SQL Task

1. Use the operation entry to create a SQL task.


2. In the task creation dialog, name the task "SQL_DWS_Aggregation" and create a dedicated folder named "Data Processing".



3. After the SQL task is created, as shown below, you can write specific SQL code in the editor area.



4. Previously, through the data sync task, MySQL data has been synced to the test_json table in Lakehouse. In the SQL task, perform aggregation processing based on this table's data, such as summing the c2_tinyint_column and c3_smallint_column fields respectively. Navigate to the "Data" tab, locate the target table test_json, and click "Data Query" in the action bar. This will automatically insert a SELECT code template into the editor, as shown below, helping to improve code writing efficiency.


5. Modify the above code template to the desired processing logic, then save. This is just for demonstration purposes, simplified processing, and the aggregation results are not written to a new table.



   ```SQL
        SELECT   SUM(c2_tinyint_column),         
                 SUM(c3_smallint_column),
        FROM     test_json;
   ```

### Task Orchestration and Scheduling Configuration

After completing the creation of the sync task and SQL task, to build a complete offline periodic ETL pipeline, you also need to configure scheduling timing and task dependencies.

1. Open the sync task and click the "Schedule" button on the page to open the scheduling configuration.



2. Configure Scheduling Time: Configure to schedule daily, run multiple times, once every hour, as shown below. Use "Preview Schedule Time" to view the specific scheduled times corresponding to the configuration.



3. Configure Instance Information: The main thing to configure here is "Instance Rerun Mode". Since this task does not have data idempotency issues when rerunning, it can be rerun. Therefore select "Can be rerun regardless of success or failure". Other properties can use default values.



4. Configure Scheduling Dependencies: The sync task is the first task in the pipeline and has no upstream dependencies, so leave this blank.



5. Configure Task Output: Task output is used to describe which table this task writes to, so that downstream tasks consuming this table can intelligently identify the corresponding upstream task. Click the "Smart Parse" button, and the system will automatically resolve the current task's output table through the task configuration and backfill it into the configuration.



6. After completing the above scheduling configuration, click the "OK" button at the bottom right of the page to save the configuration. Return to the task page, and as shown below, the "Submit" button will become clickable.



7. Click the "Submit" button, verify the information again in the popup dialog, then click OK. The sync task will be submitted to the production environment for periodic scheduled execution.



8. Switch to the SQL task, and click the "Schedule" button on the page to open the scheduling configuration. The properties to configure are the same as for the sync task, i.e.:

      1. Configure to schedule multiple times per day, once every hour.
      2. Configure the rerun property as "Can be rerun regardless of success or failure".
      3. Pay special attention to configuring the SQL task's dependency on the sync task. Click the "Smart Parse" button on the page to automatically identify the sync task that the SQL task depends on and backfill it automatically; you can also add it manually.


9. Similarly, after the SQL task's scheduling configuration is complete, click the "OK" button at the bottom right of the page to save the configuration. Return to the task page, and click the "Submit" button to also submit the SQL task for scheduled execution.



10. Enter "Task Operations" to view the actual results. There are two ways to enter:

    * Method 1: Through the left navigation Operations Monitoring > Task Operations

    * Method 2: Click the "Operations" button directly on the task to go directly to the task's details page in the Operations Center. This method is recommended.



11. View the task details, as shown below. As expected, the SQL task depends on the sync task:



12. Click the "Task Instances" tab to see the list of specific instances corresponding to the task. Instances have been generated according to the configured scheduled time (only instances after the task submission time are generated):



13. Click an instance ID to enter the instance details page for viewing. When the scheduled time arrives, the upstream sync task instance runs first. After it runs successfully, the downstream SQL task instance starts running. Two conditions must be simultaneously met for an instance to be triggered to run (necessary and sufficient conditions): the instance's own scheduled time has arrived, AND the upstream instance is in a successful state.



14. At this point, a complete ETL pipeline has been orchestrated, built, and submitted for periodic scheduling and execution.

## Limitations

* Permission Control: Users with `workspace_admin` or `workspace_dev` role permissions are required to use the features of task development, submission and publishing, and the operations center.

## Related Documents

* You can read the [Task Development](ide.md) help document to learn in detail how to perform task development and scheduling configuration. The [Task Group](task_group.md) feature provides a visual way to orchestrate ETL pipelines, which is more intuitive and recommended.
* You can read the [Task and Instance Operations](task-instance-maintenance.md) help document to learn in detail how to perform various operations on tasks and instances.

## Next Steps

* None for now.

^
