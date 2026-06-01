# Time Travel

The Time Travel feature allows you to access data at any point in time within a time window, just like time travel, including updated or deleted data, restoring deleted tables, or restoring expired tables. With Time Travel, you can easily view historical versions of data, providing a better understanding of the data change history.

![](.topwrite/assets/image_1739935647913.png)

As shown in the figure above, there was originally one piece of data in the table, and after operations such as insert, update, and delete, there are a total of four versions. When the specified version is between v0 and v1, Time Travel will return the data of v0. By specifying the version, you can view the historical version of the data.

## Operations Supported by the Time Travel Feature

* Use the undrop command to restore deleted tables
* Use the restore command to restore existing tables or dynamic tables to a specified version
* Query data that has been updated or deleted before in tables or dynamic tables
* View the version history of tables or dynamic tables
* Create table streams or use table\_changes to get changes in tables or dynamic tables

# Time Travel Retention Period Settings

The Time Travel retention period determines how long you can access past data. For example, if the Time Travel retention period is set to 7 days, you can access data from any point in time within the past 7 days. After 7 days, you will not be able to use Time Travel to access expired data, and the data will be physically deleted.
The default retention period for the historical state of Lakehouse tables is 1 day (24 hours), and you can query historical versions within 1 day through Time Travel.

If you need to retain historical versions for a longer period, you can set different data retention periods for each table to meet different business needs. The setting range for num is 0-90.
  * ```SQL
    ALTER TABLE tablename SET PROPERTIES ('data_retention_days'='num');
    ```
## Restore Deleted Objects

Please refer to the [Restore Deleted Data](undrop-table.md) document to learn how to use the undrop command to restore deleted tables.

## Restore Data to a Specified Version

Please refer to the [RESTORE Command](restore.md) document to learn how to use the restore command to restore existing tables or dynamic tables to a specified version.

## Query Historical Data

Please refer to the [TIME TRAVEL](timetravel.md) document to learn how to query data from tables or dynamic tables before they were updated or deleted.

## View Object Version History

Please refer to the [DESC HISTORY](desc-history.md) document to learn how to view the version history of tables or dynamic tables.

## Use table stream and table\_changes to Get Table Changes

* Please refer to the [Use TABLE CHANGES to Get Data Changes](table_changes.md) document to learn how to use table\_changes to get changes in tables or dynamic tables.
* Please refer to the [Use TABLE STREAM to Get Data Changes](tablestream_summary.md) document to learn how to use table stream to get changes in tables or dynamic tables.