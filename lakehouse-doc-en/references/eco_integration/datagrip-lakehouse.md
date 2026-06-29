# DataGrip Connects to Singdata Lakehouse

This document will guide you on how to use the database management tool DataGrip to connect to Singdata Lakehouse for efficient data management operations.

## Background Information

DataGrip is a powerful commercial database management tool designed to meet the specific needs of professional SQL developers. It supports multiple databases, including Singdata Lakehouse. For more information about DataGrip, please visit the [official website](https://www.jetbrains.com/datagrip/).

## Prerequisites

Before starting, please ensure you meet the following conditions:

1. Successfully activated the Lakehouse service.
2. Downloaded the JDBC driver for Lakehouse. Please refer to the [official documentation](../version-update) to obtain the driver.
3. Downloaded and installed DataGrip.

## Step 1: Add Singdata Lakehouse Driver

1. Open DataGrip and enter the main interface.
2. Click "New Project" to create a new project. In the new project interface, click "Driver" and select the "+" button to add a new driver. Name the driver Lakehouse.

## Step 2: Connect to Singdata Lakehouse Using DataGrip

1. In the "Data Sources" window, select the Lakehouse data source you just created.
2. Click the "Test Connection" button to ensure the connection is normal. If the connection fails, please check your Lakehouse service and JDBC driver settings.
3. Click the "OK" button to complete the data source configuration.
4. From the Lakehouse service homepage, copy the JDBC connection string. The format is: `jdbc:clickzetta://<instance>.<region>.api.singdata.com/<workspace>?virtualcluster=<vcluster>&schema=<schema>`.

## Step 3: Manage Singdata Lakehouse Using DataGrip

1. In the "Database" panel on the left side of DataGrip, you can see all the schemas and tables.

2. Right-click any schema or table and select "SQL Script" to open the SQL editor.
3. In the SQL editor, you can write and execute SQL queries. For example, you can execute the following query to get the first 10 rows of a table:

```sql
SELECT * FROM your_table LIMIT 10; -- Get the first 10 rows of the table
```
```sql
SELECT * FROM your_table_name LIMIT 10;
```
4. After executing the query, the results will be displayed in the "Results" panel below. You can sort, filter, and export the results.

# Frequently Asked Questions
Due to different versions of DataGrip having various changes, some versions may send SQL with quotes in the schema when previewing tables. You can bypass this by editing the data source and adding the following to the startup script in the options, and checking Single session mode.
```
set  cz.sql.double.quoted.identifiers=true;
```