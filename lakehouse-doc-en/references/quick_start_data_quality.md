# Getting Started: How to Quickly Configure and Use Data Quality Rules

## Applicable Scenarios

Data quality rules are used to verify whether the quality of data objects meets requirements, such as data correctness, validity, and consistency, especially for tables produced by tasks serving production use. If you have configured an ETL pipeline, such as the [Getting Started: How to Quickly Configure, Orchestrate, and Schedule ETL Pipelines](quick_start_etl.md), and plan to add a data quality check, it is recommended to read this guide.

## Prerequisite Reading

Before reading this guide, it is recommended to complete reading and understanding the following documents:

* [Lakehouse Product Introduction](what_is_clickzetta_lakehouse.md)
* [Key Concepts](key_concepts.md)
* [Lakehouse Studio Quick Tour](lakehousestudiotour.md)

## Operation Guide

You can use the "Data Quality" feature provided by Lakehouse Studio to configure quality rules for checking. Checks are mainly performed based on data quality rules. Rules predefine the verification object, check logic, and expected results, and can be triggered to run in multiple ways. This example demonstrates how to configure a rule for a Lakehouse table field to verify that its value is not null.

### Usage Notes

* Users with `workspace_admin` or `workspace_dev` role permissions have access to the "Data Quality" feature.
* The "Data Quality" feature is currently primarily used to monitor Lakehouse data objects, such as Tables, Views, Volumes, Dynamic Tables, etc. For other data types such as MySQL, it is not currently supported.

### Steps

1. As shown below, click the button to enter the Lakehouse service instance:

   ![](.topwrite/assets/image_1748337538227.png)

2. Navigate to "Data" > "Data Quality" page:

   ![](.topwrite/assets/image_1749449999835.png)

3. On the "Quality Rules" tab, click the "Create Rule" button to open the page for creating a new quality rule. Please verify and ensure that the workspace in the upper right corner of the page is the workspace where the data table to be verified is located. If not, you can click to switch.
   ![](.topwrite/assets/image_1749450019542.png)

4. On the Create Rule page, the workspace value will be automatically set to the workspace selected in the previous step [1]. Select the data object to verify. In this example, select the `test_json` table where data was written by the sync task in the previous ETL pipeline for verification [2]. When a quality rule is executed, it is actually converted to a Lakehouse SQL statement for execution, so an execution cluster is required. For simplicity, it is recommended to directly select the default GP-type cluster `DEFAULT` [3].
   ![](.topwrite/assets/image_1749450038105.png)

5. Configure "Verification Method", "Trigger Method", and "Save" the rule.

   * Verification Method [4]: In this example, we plan to monitor whether the c1_id field in the test_json table has non-null values, so select "Single Metric Value Verification". "Metric Value Change Verification" compares two metrics and verifies the change value. The product has many built-in metric rules, ready to use out of the box. Here, select field null count, select the field name, and set the expected result to equal 0.

   * Trigger Method [5]: As the name implies, the product provides three methods: scheduled triggering, periodic task triggering, and manual triggering. Periodic task triggering is bound to the scheduling system and can trigger the execution of quality rules after the task scheduling instance completes running, enabling more timely verification. For production scenarios, this method is recommended. Especially the "Strong Blocking Scheduling" option can block the entire scheduling pipeline when a quality rule verification fails, preventing the spread of quality issues. When selecting this method, you need to choose the bound scheduling task (i.e., the task that produces this data table).

   * Other configuration items can keep default values or be left blank. Finally, click the "Save" [6] button to complete the creation of the quality rule.

   ![](.topwrite/assets/image_1749450069308.png)

6. After creation, you can see the newly added rule in the quality rule list page.
   ![](.topwrite/assets/image_1749450081238.png)

7. You can click the "Trial Run" button to test the configuration and verification of the quality rule. On the "Verification Results" tab, you can view the specific results, as shown below: the quality rule was triggered to run, the verification result matches expectations, and everything is normal.
   ![](.topwrite/assets/image_1749450092151.png)
   ![](.topwrite/assets/image_1749450096317.png)

8. Wait for the scheduled task's timing to arrive and observe the quality rule triggering.

   * In "Task Operations", you can view the triggering and running status of quality rules through the logs of periodic task instance execution.
     ![](.topwrite/assets/image_1749450116093.png)

   * In "Data Quality" > "Verification Results", you can see the newly added verification record, with the trigger method being "Periodic Task Triggered".
     ![](.topwrite/assets/image_1749450124984.png)

9. At this point, the configuration of quality rules and observation of verification execution have been completed. After completing the data quality rule configuration, if you need to promptly receive monitoring and alerting information when quality rule verification fails, you also need to configure monitoring. The specific operations are omitted here. For details, see the [Data Quality](dataquality.md) help document.

## Related Documents

* You can read the [Data Quality](dataquality.md) help document to understand the complete usage guide for the Data Quality module.

## Next Steps

* After completing quality rule configuration, you can refer to the guide [How to Quickly Configure and Use Monitoring and Alerting Rules](quick_start_monitoring_and_alerting.md) to configure monitoring rules and send alerts for quality rule verification results and task running status.

^
