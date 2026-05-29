# Getting Started: How to Quickly Upload and Import Local Data

## Applicable Scenarios

Lakehouse provides an integrated engine to support data processing, transformation, and analysis, using SQL as the development language. This document provides an overview of how to quickly write and run a SQL statement for data query and analysis through the task development feature module of Lakehouse Studio.

## Prerequisite Reading

Before reading this guide, it is recommended to complete reading and understanding the following documents:

* [Lakehouse Product Introduction](what_is_clickzetta_lakehouse.md)
* [Key Concepts](Key_Concepts.md)
* [Lakehouse Studio Quick Tour](LakehouseStudioTour.md)

## Operation Guide

You can add data to Lakehouse tables through the "Data Upload" feature available on the Lakehouse Studio interface.

### Usage Notes

* Suitable for relatively small (no larger than 2GB) local files (CSV, TXT, Parquet, Avro, ORC) to be uploaded directly to Singdata Lakehouse tables. No programming required, the simplest approach.
* Currently only supports uploading one file at a time.
* The data upload feature currently does not support parsing fields of the struct, map, and array data types within files.
* Users with `workspace_admin`, `workspace_dev`, or `workspace_analyst` role permissions are required to use the data upload feature.

### Steps

1. Log into your Singdata Studio account

2. You can click "Upload Data" in any of the following locations:

   * Instance Homepage
     ![](.topwrite/assets/image_1747999086635.png)
   * Development -> Data Tree
     ![](.topwrite/assets/image_1749035410382.png)
   * Data Asset Map
     ![](.topwrite/assets/image_1749035355497.png)
   * Data Asset Map -> Data Management
     ![](.topwrite/assets/image_1749035495163.png)

3. After clicking, the following dialog will appear. You can add local files by dragging and dropping, or by clicking to browse files on the local system. Only one file can be added at a time, and the size must not exceed 2GiB. You can use this sample file to try uploading: :attachment[walmart.csv]{src=".topwrite/assets/walmart.csv" size="363.73 kB"}.

   ![](.topwrite/assets/image_1749035813956.png =380)

4. Schema: Choose to create the table under a certain schema.

5. Select Table: Choose "New Table" and enter the new table name in the field behind.

6. Cluster: The available cluster under the workspace where the current schema is located.

7. Data Import Mode: Supports append write and truncate-then-write modes for importing data into the new table.

8. After confirming all information, click "Next". The system will automatically parse the field information from the uploaded file, as shown below.
   ![](.topwrite/assets/image_1749035692218.png =380)

9. Check and determine whether the automatically parsed field names and field types meet expectations. After confirming correctness, click "Confirm" to complete the table creation and data upload.
   * If you find issues with field parsing, you can modify the **File Properties** configuration items to re-trigger automatic parsing of field names, field types, etc. Or you can manually modify field names or field types.
   * Note: Modified field types may not match the system's parsing, potentially causing upload failure.

## Related Documents

* You can read the [Upload Data Using the Data Upload Feature](upload_data.md) help document to learn more about data upload methods, such as uploading data to existing tables.
* You can read the [Comprehensive Guide to Ingesting Data into Lakehouse](a_comprehensive_guide_to_ingesting_data_into_clickzetta_lakehouse.md) to learn more ways to import data into Lakehouse.

## Next Steps

* After completing data upload, you can refer to the guide [How to Quickly Run a SQL Query](quick_start_sql_query.md) to query and analyze the data in the table.

^
