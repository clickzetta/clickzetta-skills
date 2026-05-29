# SQL Workbench/J Connects to Singdata Lakehouse

Singdata Lakehouse provides you with a convenient way to access and manage data in the Lakehouse through the database management tool SQL Workbench/J. This document will detail how to use SQL Workbench/J to connect to Singdata Lakehouse and provide some practical operation examples.

## Background Information

SQL Workbench/J is a free, cross-platform SQL query tool written in Java, suitable for all operating systems that provide a Java runtime environment.

## Prerequisites

Before starting, please ensure you meet the following conditions:

- Java 11 version is installed.
- Lakehouse service is activated.
- [Lakehouse JDBC driver](<../version-update.md>) is downloaded.
- [SQL Workbench/J](https://sql-workbench.eu/download-archive.html) is downloaded and installed. This document uses SQL Workbench/J Build 128 as an example.

## Step 1: Start SQL Workbench/J

1. To ensure SQL Workbench/J runs properly, add `JDK_JAVA_OPTIONS=--add-opens=java.base/java.nio=ALL-UNNAMED` to the environment variables. Note that you only need to modify this parameter if you are using Java 1.8 or lower. Since SQL Workbench/J Build 128 requires Java 11, this modification is necessary.
2. On Linux systems, start SQL Workbench/J by executing the `sh sqlwbconsole.sh` command. For Windows systems, simply click `SQLWorkbench64.exe` to start.

## Step 2: Add Singdata Lakehouse Driver

1. After starting SQL Workbench/J, the system will automatically pop up the "Select Connection Profile" dialog box. If it does not pop up, click the "Driver" menu and select "Manage Drivers".
2. In the "Manage Drivers" dialog box, click the "Add Driver" button in the lower left corner to create a new driver. Enter a custom driver name and upload the downloaded Singdata JDBC driver JAR package. After completion, click the "OK" button to complete the driver configuration. Note that after uploading the Lakehouse JDBC driver, configure the "Classname" as `com.clickzetta.client.jdbc.ClickZettaDriver`.

![Add Driver Interface](.topwrite/assets/image_1693482142270.png)

## Step 3: SQL Workbench/J Connects to Singdata Lakehouse

1. In the Profile configuration interface on the right side of the "Select Connection Profile" dialog box, select the newly created Singdata driver. Copy the JDBC connection string from the Lakehouse homepage.

![Select Driver Interface](.topwrite/assets/image_1693482159154.png)

![Lakehouse Homepage JDBC Address](.topwrite/assets/image_1693482172849.png)

2. In the "Connection" tab of the Profile configuration interface, paste the copied JDBC connection string. If necessary, you can also set other connection parameters in the "Advanced" tab, such as SSL, maximum connections, etc.

## Step 4: Use SQL Workbench/J to Manage Singdata Lakehouse

1. After a successful connection, you can view all schemas and tables in the left menu bar.

![View Schema and Table](.topwrite/assets/image_1693482182988.png)

2. In the SQL editor on the right, you can write and execute SQL queries. For example, try executing the following query to view the data of a specific table:
```sql
SELECT * FROM your_table_name LIMIT 10;
```
3. You can also use the import and export functions of SQL Workbench/J to import data from other data sources into Singdata Lakehouse, or export data to other data sources.

Through the above steps, you have successfully used SQL Workbench/J to connect and manage Singdata Lakehouse. If you have any questions or need further assistance, please feel free to contact our technical support team.