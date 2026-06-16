# Overview

Data synchronization is an efficient data integration service built into Singdata Lakehouse, supporting data synchronization between various data sources and creating automated synchronization tasks using the scheduling system. With the data synchronization feature, users can quickly import data into Lakehouse, export processed data, or synchronize data between different data sources without writing code, simply through a wizard-like operation.

^

## Basic Concepts

### Data Synchronization Task

A data synchronization task is a type of task used to collect data from a data source and write it to a target data source. Based on the timeliness of data synchronization, data synchronization tasks can be divided into offline synchronization tasks and real-time synchronization tasks. In Lakehouse Studio, data synchronization tasks are defined and scheduled through interface configuration without writing code.

Lakehouse Studio currently supports two main types of synchronization tasks: offline periodic synchronization and real-time synchronization. In the "Development -> Tasks" section, use the new button to select the appropriate task type as needed.

:-: ![](.topwrite/assets/image_1740136964041.png =600)

^

A data synchronization task includes the following core components:

1. Data Source: The data source for the synchronization task, including databases, file systems, SaaS/applications, Lakehouse space data sources, etc. Data sources are defined and managed by the data source.
2. Data Object: The data object under the data source that needs to be processed by the synchronization task, such as database tables, message queue topics, file system files, etc.
3. Object and Schema Mapping: Defines the mapping relationship between the source data object and the target data object and their schemas.
4. Data Target: The target data source where the data is written, including Lakehouse and other external data sources.
5. Task Settings: Rule settings that affect task execution, such as fault tolerance rules, concurrency settings, traffic control, etc.
6. Scheduling Configuration: Rules and strategies for task scheduling and execution.

### Data Source

A data source is an object that defines the connection information of an external service, including service address, authentication information, connection method, etc. Defined data sources can be used as data sources or data targets in data synchronization tasks. Data sources are located under the "Management -> Data Sources" function menu.

^

## Usage Example

### Example: Synchronize Data from MySQL Database to Lakehouse

Suppose you have a MySQL database containing customer order data. You want to synchronize this data to Lakehouse for data analysis and processing.

1. Create a new data synchronization task in Lakehouse.
2. Select the MySQL database as the data source and specify the corresponding data source connection information.
3. Select the database table to be synchronized as the data object.
4. Define the table structure and field mapping rules.
5. Select Lakehouse as the data target and specify the target table.
6. Configure task settings and scheduling configuration as needed.
7. Start the synchronization task, and the data will be synchronized from the MySQL database to Lakehouse according to the set rules.

Through the above example, you can see that the Lakehouse data synchronization feature can help you easily achieve data synchronization between different data sources without writing complex code. This will greatly improve data processing efficiency, allowing you to focus on data analysis and business decision-making.

^

For detailed guides on creating and configuring data synchronization tasks, please refer to the following help documents:

* [Offline Synchronization Tasks](batch_sync.md)
* [Real-time Synchronization Tasks](realtime_sync.md)
* [Multi-table Real-time Synchronization Tasks](multitable_realtime_sync.md)

^
