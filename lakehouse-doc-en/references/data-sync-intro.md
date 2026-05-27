# Overview

Data Sync is a built-in data integration service in Singdata Lakehouse. It supports synchronizing data between various data sources and forming automated synchronization tasks with the help of the scheduling system. With data sync, you can quickly import data from various data sources into Lakehouse, export processed data backflow, or simply synchronize data between different data sources without writing code and through a wizard-like method.

![](.topwrite/assets/image_1726021734991.png)

^

## Basic Concepts

* Data Sync Task
  A data sync task is a task type that implements data collection from the data source and writes it to the target data source. According to the timeliness of data synchronization, it is divided into offline synchronization tasks and real-time synchronization tasks. In Clickzetta Lakehouse, data synchronization tasks do not require code writing, and task definition and scheduling configuration can be achieved through interface configuration.
  A data synchronization task includes the following core objects:
  * Data Source: The data source of the synchronization task, including databases, file systems, SaaS applications, Lakehouse space data sources, etc., defined and managed by the data source
  * Data Object: The data object that needs to be processed under the data source of the synchronization task. Including database tables, message queue Topics, file system files, etc.
  * Object and Schema Mapping: Mapping of source data objects and target data objects and their Schema
  * Data Target: The target data source for writing data, including Lakehouse and other external data sources
  * Task Settings: Rule settings that affect task operation, including fault tolerance rules, concurrency settings, traffic control, etc.
  * Scheduling Configuration: The rules and strategies for task scheduling and operation
* Data Source:
  An object defining external service connection information. Including service address, authentication information, connection method, etc. The defined data source can be used as a data source or data target in data synchronization tasks.

^
