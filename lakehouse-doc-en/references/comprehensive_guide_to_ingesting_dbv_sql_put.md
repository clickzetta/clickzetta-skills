# A Complete Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Using Database Client DBV/SQLWorkbench to PUT Files

#### Overview

The PUT command is a utility in Lakehouse SQL used to upload local files from the client host to the data lake Volume object in Lakehouse. With this command, users can easily transfer local files to the cloud, enabling quick data migration and synchronization. To execute the PUT command, you can use the sqlline tool or a database management tool.

#### Use Cases

* Upload local files to the data lake Volume object.
* Quickly migrate and synchronize local and cloud data.

#### Implementation Steps

##### Download and Install DBV

This guide uses [DbVisualizer Free Edition](https://www.dbvis.com/) as the example database management tool. Skip this step if already installed.

Download the [JDBC Driver](jdbc-driver.md) for Singdata Lakehouse to your local machine.

Install the Lakehouse JDBC Driver in DBV.

##### Create a New Database in DBV

Establish a connection with Singdata Lakehouse.

##### Create and Run a New SQL Script
```SQL
PUT 'data/lift_tickets_data.csv.zip' TO volume ingest_demo  FILE 'gz/lift_tickets_data_put.csv.zip';SHOW  VOLUME DIRECTORY ingest_demo;
```
##### :-: ![](.topwrite/assets/image_1736215162253.png =531)

##### Check PUT Result
```SQL
SHOW  VOLUME DIRECTORY ingest_demo;
```
#### Data

[SQL PUT Command](put.md)

[JDBC Driver](jdbc-driver.md)

[Database Management Tool](data-mamager-tool.md)