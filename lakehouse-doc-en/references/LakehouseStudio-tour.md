# Lakehouse Studio Quick Tour

This document helps you quickly understand the core features offered by Lakehouse Studio. In Lakehouse Studio, you can perform data analysis and engineering tasks, monitor queries, data loading/synchronization, data transformation, and workflow activities, explore your Lakehouse objects, and manage your Lakehouse, including managing costs and adding users and roles.

> You can use this document to quickly understand Studio's features. We also strongly recommend referring to the [Getting Started Guide](lakehouse-studio-101.md) series to get started quickly.



^

## What You Can Do in Lakehouse Studio

* [Data Management](data.md), create and manage data lake/database objects such as databases, tables, dynamic tables, etc.
* [Compute Resource Management](computation.md), create and manage compute resources such as virtual clusters, job history, etc.
* [ELT Pipeline Development and Management](ide.md), create and manage data ELT pipeline objects such as data sources, pipeline definitions, tasks (extraction tasks, transformation tasks, etc.), workflows, alerts, etc. Tasks support the following types:
  * [Data Synchronization Tasks](data-integration.md), ingest data from databases/data warehouses/data lakes and other data sources into Lakehouse, and export data from Lakehouse to other data sources.
  * [SQL Tasks](task-develop.md), write SQL queries and code for data ingestion, discovery, cleaning, and transformation, leveraging auto-completion of database objects and SQL functions within worksheets.
  * [Python Tasks](python-task.md), build, test, and deploy SQLAlchemy/Zettapark Python worksheets.
  * [JDBC Tasks](jdbc_task.md), build, test, and deploy JDBC worksheets (manipulate data in data sources via JDBC connections).
* [Organize Tasks](task-develop.md), organize worksheets into task folders and [task groups](task_group.md).
* **Share Job Profiles**: Share job profiles with other users.
* **Data Profiling**: Visualize SQL worksheet results as data profiles.
* **Manage and Control Costs**: Manage and control costs.
* [Job History](web-job-history.md), view query history and data loading history.
* [Workflow DAG](task-instance-maintenance.md), view workflow graphs and run history.
* [Backfill Tasks](backfilling_data.md), debug and re-run task graphs.
* **Monitor Dynamic Tables**: Monitor dynamic table graphs and refresh status.
* [User/Role Management](account_user_management.md), manage and create Lakehouse users and roles.
* [Data Quality Management](data-quality.md), clean, optimize, and enhance massive datasets to increase their value density, thereby more effectively meeting business objectives.

For details on these and other executable tasks, please refer to [Lakehouse Studio: The Web Interface for Lakehouse](studio_manual.md).

## Explore and Manage Your Lakehouse Objects

You can explore and manage your data lake/database objects in Lakehouse Studio as follows:

* Use the data object explorer to explore data lakes/databases and objects, including tables, views, etc.
* Create objects such as schemas and tables.
* Search in the object explorer to browse database objects in your account.
* Preview the contents of database objects (such as tables) and view files uploaded to volumes.
* Load files into existing tables, or create tables from files, to get started with data in Lakehouse more quickly.

For more information, refer to the following documentation:

* [Search Data Objects via Data Asset Map](data_catalog.md)
* [Load Data Using the Lakehouse Studio Web Interface](upload_data.md)

## Data Synchronization Tasks

Data synchronization is a seamless data integration capability built into Lakehouse, enabling data movement between various data sources. It allows users to automatically execute synchronization tasks through a powerful scheduling system. With this feature, you can easily ingest data into Lakehouse, export processed data, or coordinate data between different data sources -- without writing any code. The entire process is as simple as navigating through a user-friendly wizard.

Depending on the data source, data format, loading method, and processing type (batch, streaming, or data transfer), there are multiple ways to load data into Lakehouse. Lakehouse provides various import methods, categorized by implementation approach, including: importing via user SDKs, importing via SQL commands, uploading data via clients, importing via third-party open-source tools, and importing via the Lakehouse Studio visual interface.

### Import Methods Overview



### Supported Data Sources



### Real-time Multi-Table Data Synchronization Tasks (CDC)

* Create a data source (Postgres)
* Create a real-time multi-table synchronization task from Postgres to Lakehouse
* Submit and run the task, then start the task
* Task monitoring and maintenance (start, stop, offline)



For details, refer to the following documentation:

* [Data Source Support](data-sources.md)
* [Data Source Management](config-datasource.md)
* [Batch Data Synchronization Tasks](batch_sync.md)
* [Multi-Table Real-time CDC (Change Data Capture) Synchronization Tasks](multitable_realtime_sync.md)
* [Real-time Data Synchronization from Kafka/AutoMQ](realtime_sync.md)

## Write SQL and SQLAlchemy/Python Code in Worksheets and Workflow Orchestration

Worksheets provide a simple way to write SQL jobs (DML and DDL), view results, and schedule them as tasks. With worksheets, you can:

* Run ad hoc queries and other DDL/DML operations.
* Write SQLAlchemy/Zettapark Python code in Python worksheets.
* View query history and results of executed queries.
* View multiple worksheets simultaneously, each with its own independent session.
* Export results of selected query statements while results are still available.
* Submit jobs and schedule them as tasks.

If you select Worksheets in the navigation menu, you will see the worksheet list and can select one to view and update worksheet content.



For details, refer to the following documentation:

* [Lakehouse Studio Task Development Overview](task_development.md)
* [Workflow Orchestration with Lakehouse Studio Task Development and Scheduling](task-develop.md)
* [Lakehouse Studio Task Groups](task_group.md)
* [Writing Python Code in Python Worksheets](python-task.md)

## Visualize Query Results as Data Profiles

When running queries in Lakehouse Studio, you can choose to visualize the data profile of the results.



## Share Data

Achieve collaboration by sharing data with users of other Lakehouse accounts. When sharing data, you can use the automatic delivery (or auto-fulfillment) feature to easily provide data within the same cloud region. As a data consumer, you can access datasets shared with your account, gaining real-time data insights without setting up data pipelines or writing any code.



For details, refer to the following documentation:

* [Lakehouse Data Sharing](data-sharing.md)

## Monitor Activities in Lakehouse Studio

### Monitor Query Activity Using Query History

You can monitor and view query details, explore the performance of executed queries, monitor data loading status and errors, view task graphs, and debug and re-run as needed. You can also monitor the refresh status of dynamic tables and view various tags and security policies created for maintaining data governance.



For details, refer to the following documentation:

* [Monitor Query Activity Using Query History](web-job-history.md)

### Monitor Workflow Tasks Using the Operations Center

The Operations Center provides management operations for tasks and instances. Workflow tasks managed by the Operations Center include manually triggered tasks, periodically scheduled tasks, and their corresponding instances, for centralized management.



Data backfilling involves supplementing historical or future data within a specific time period and writing it to the corresponding time partitions. If the code contains scheduling parameters, those parameters will be automatically filled with appropriate values based on the selected data backfill business time. Combined with business logic, this ensures that data for the corresponding time period is written to the specified partitions. The partition to write to and the code logic executed are determined by the task definitions in the code.



Monitoring functionality allows you to leverage built-in rules or custom configurations to keep a close watch on anomalies (such as task execution failures) and send alert notifications when needed.



For details, refer to the following documentation:

* [Task Instance Maintenance](task-instance-maintenance.md)
* [Data Backfilling](backfilling_data.md)
* [Monitoring and Alerting](monitoring_and_alerting.md)

## Perform Compute Resource Management and Manage Lakehouse Studio

These pages help you understand Lakehouse data usage, manage virtual clusters, monitor task queues in virtual clusters, manage users and roles, manage Lakehouse accounts, and more.

You can manage and monitor virtual clusters.



Access users and roles.



Perform cost management.



^

When you log in as a user with the **account administrator role**, you can view the account's usage records under the **Billing** feature in the Account Center (\<your\_account\_name>.[accounts.clickzetta.com/billing](http://accounts.clickzetta.com/billing)). You can also query detailed charges by SKU type (such as compute, storage, network, or specific SKU).

For details, refer to the following documentation:

* [Understanding Workspaces](workspace-introduction.md)
* [Managing Accounts](manage-accounts.md)
* [Managing Users](account_user_management.md)
* [Managing Service Instances](managing-instance.md)
* [User and Permission Management](authority-management.md)




^
