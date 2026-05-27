# Connect and Use Lakehouse

Singdata Lakehouse provides you with various ways to connect and operate, including Lakehouse Studio, Lakehouse CLI, drivers and connectors, SDKs, etc. This document will detail how to use these tools and provide some practical usage examples.

## Lakehouse Studio: Lakehouse Development and Management Tool

Lakehouse Studio provides you with a complete set of data management tools, including data integration, development analysis, orchestration scheduling, monitoring and operation, data management, system management, etc. Multi-role users can collaborate on development and analysis under a unified user experience.

For details, see: [Studio User Guide](studio_manual.md)

### Usage Example

1. Log in to Lakehouse Studio.
2. Select the appropriate management tool from the left navigation bar.
3. Perform data integration, development analysis, and other operations as needed.

## Lakehouse CLI (Command Line Tool)

Lakehouse CLI is a command line tool provided by Lakehouse. After installation and configuration, you can use the Lakehouse CLI command line client tool to submit SQL commands.

## Drivers & Connectors & SDKs

Lakehouse supports various drivers and connectors, SDKs, making it convenient for you to access Lakehouse through different programming languages and tools.

* JDBC Driver: Access Lakehouse via JDBC connection.
* SQLAlchemy (Python ORM): Access Lakehouse via SQLAlchemy protocol.
* Flink Connector: Write data in real-time through the Connector.
* Java SDK: Access Lakehouse via Java SDK.
* Python SDK: Access Lakehouse via Python SDK.
* Catalog SDK: Through the Catalog SDK, open-source engines (such as Spark, Trino) can connect to Lakehouse metadata and access data.
* Zettapark: A programming interface compatible with PySpark.

## JDBC Address

In Lakehouse Studio, you can easily obtain the jdbc url connection address of the workspace.
![](.topwrite/assets/image_1739867082170.png)

### Operation Steps

1. Log in to Lakehouse Studio.
2. Select "Workspace" from the left navigation bar.
3. In the workspace details page, find "JDBC URL" and copy it.

## Ecosystem Tools

For details, see: [Using Open Source Tools to Connect to Lakehouse](eco_integration/sqlworkbench-j-lakehouse.md)
