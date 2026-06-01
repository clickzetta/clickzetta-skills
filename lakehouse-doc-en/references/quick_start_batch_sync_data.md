# Getting Started: How to Quickly Create a Sync Task to Import Data

## Applicable Scenarios

If your data is stored on systems such as databases or object storage and needs to be imported into Lakehouse for processing and analysis, this document is suitable for you. If you need to import data from local files, you can directly refer to [How to Quickly Upload and Import Local Data](quick_start_upload_data.md), which is more convenient.

## Prerequisite Reading

Before reading this guide, it is recommended to first read and understand the following documents:

* [Lakehouse Product Introduction](what_is_clickzetta_lakehouse.md)
* [Key Concepts](key_concepts.md)
* [Lakehouse Studio Quick Tour](lakehousestudiotour.md)
* [Data Sync Feature Overview](data-integration-intro.md)
* [Data Source Management and Configuration Guide](config-datasource.md)

## Operation Guide

You can use the "Sync Task" feature provided by Lakehouse Studio to sync data from databases, object storage, and other systems into Lakehouse. This document uses MySQL as the source for demonstration.

### Usage Notes

* Sync tasks pull data from the source and depend on the network reachability of the source data source. It is recommended to use data sources with public network access for feature experience. In complex network scenarios, such as syncing data from databases within a VPC, network connectivity must be established. Refer to [Syncing RDS Data via PrivateLink through VPC (Alibaba Cloud)](studiodi_privatelinkvpc_fromrds.md) for detailed information.
* Users with `workspace_admin` or `workspace_dev` role permissions are required to use the "Sync Task" feature.

### Steps

1. As shown below, click the button to enter the Lakehouse service instance:

   ![](.topwrite/assets/image_1748337538227.png)

2. Navigate to the "Development" page:

   ![](.topwrite/assets/image_1748337566571.png)

3. In the folder area of the left directory tree, click the + (New) button, and select the "Batch Sync" task type from the menu:

   ![](.topwrite/assets/image_1748337579720.png)

4. In the dialog, enter the task name (you can create a folder, not required), and click "OK".

   ![](.topwrite/assets/image_1748337590537.png)

5. You can see the newly created sync task on the page, as shown below:

   ![](.topwrite/assets/image_1748337598616.png)

6. Start configuring the required information for the sync task. The core is to configure the source and target information.
   Note: You need to understand the concept of "Data Source" here. A "Data Source" is an object that defines external service connection information, including service address, authentication information, connection method, etc. A defined data source can be used as a data source or data target in data sync tasks.

7. The source configuration is shown below. Click "+" to quickly bring up the interface for creating a new data source:

   ![](.topwrite/assets/image_1748337608071.png)

8. Select the type of data source to import. In this example, MySQL is selected. Click "Next" to enter the detailed configuration page. The "Usage Instructions" in the upper right corner provides a detailed configuration guide, as shown below. Ensure that the filled-in JDBC connection address, username, and password are correct. The serverTimezone configuration item refers to the timezone where the database is located, which will affect the values of date and time fields after syncing to the target. Please select correctly based on the actual situation.

   ![](.topwrite/assets/image_1748337616322.png)

9. After completing the required information configuration for the data source, you can click the "Connectivity Test" button to test whether the data source is reachable. A successful connection test is shown below. If the connection fails, please check the network and whether the configuration information is accurate. After the test passes, click "OK" in the lower right corner to save.

   ![](.topwrite/assets/image_1748337623157.png)

10. After creating the data source, return to the sync task configuration page, select this data source as the source (if it does not display automatically, please reopen the task), and select the namespace (i.e., database) and data object (i.e., table). Other configuration items can be left empty.

    ![](.topwrite/assets/image_1748337630413.png)

11. After completing the source configuration, proceed to configure the target, as shown below:

    ![](.topwrite/assets/image_1748337636870.png)

    1) Select the Lakehouse data source type

    2) Select the built-in quick_start workspace (analogous to a database).

    3) Select the public namespace (i.e., schema)

    4) Data object: Click the + button to quickly create a new target Lakehouse table. In the dialog, verify the table name and schema information, then click "OK" to complete the table creation.

    ![](.topwrite/assets/image_1748337664468.png)

    5) Select "Overwrite" as the data write mode, meaning the target table will be truncated before syncing data from the source.

12. After completing the above steps, the field mapping relationship between the source table and target table will be automatically displayed in the "Field Mapping Configuration" (default is same-name mapping). The default approach is fine here, no modification needed.

    ![](.topwrite/assets/image_1748337679341.png)

13. For other configuration items, such as sync rule configuration and advanced configuration, use the default values.

    ![](.topwrite/assets/image_1748337686553.png)

14. Click the "Save" button above the task configuration area to save all task configurations.

    ![](.topwrite/assets/image_1748337694348.png)

15. Click the "Run" button in the upper right corner to run a test and trigger data sync (use the default value for the cluster option).

    ![](.topwrite/assets/image_1748337705970.png)

16. In the "Run History" area at the bottom right of the page, you can view the task's running status.

    Note: If you want to test sync speed, it is recommended to use a table with a relatively large data volume to reduce the impact of task startup time.

    ![](.topwrite/assets/image_1748337713243.png)

17. At this point, a sync task has been created and run, importing MySQL data into Lakehouse. You can now perform subsequent analysis and processing based on the imported data.

## Related Documents

* You can read the [Data Sync | Documentation Directory](data-integration.md) document to understand the complete usage guide for data sync tasks.
* You can read the [Comprehensive Guide to Ingesting Data into Lakehouse](a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md) to fully understand the various ways to import data into Lakehouse.

## Next Steps

* After completing data upload, you can refer to the guide [How to Quickly Run a SQL Query](quick_start_sql_query.md) to query and analyze the data imported into the table.

^
