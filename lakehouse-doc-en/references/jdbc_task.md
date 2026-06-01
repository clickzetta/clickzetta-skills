# JDBC Task

JDBC script is an important type of task node in data development. They allow you to write SQL code to connect to data sources that support the JDBC protocol, enabling operations such as data addition, deletion, modification, and querying. This document will provide you with detailed operational guidelines and usage examples to help you use JDBC scripts more efficiently.

## Operation Guide

1. **Create a New Task**: In the data development interface, click the new task button to enter the task configuration page.

2. **Select Task Type**: On the task configuration page, select "JDBC Script" as the task type.

![](.topwrite/assets/image_1740140364174.png =492)

3. **Configure Data Source**: On the task configuration page, select an existing data source or create a new data source. After selecting the data source, you also need to select the specific database under that data source.

   ![Select Data Source and Database](.topwrite/assets/image_1740140399164.png =640)

4. **Write SQL Script**: In the SQL editing area, write the SQL statements you need to execute. You can write multiple SQL statements, and they will be executed sequentially in the order they are written.

5. **Run Task**: Click the "Run" button to execute the SQL script you have written. The execution results will be displayed in the result display area below.

   ![Run JDBC Task](.topwrite/assets/image_1740140413752.png)

6. **Task Scheduling**: Like SQL tasks, you can directly implement periodic scheduling and operations of Python tasks and achieve workflow orchestration with other tasks by setting task dependencies.

## Supported Data Sources and Versions

Currently, JDBC tasks support the following data sources and their corresponding versions:

| Data Source | Version |
| ----------- | ------- |
| MySQL       | 5.1.49  |
| Hive        | 3.1.2   |
| ClickHouse  | 0.26    |

## Practical Guide

[Connecting to MindsDB via JDBC Node for Data Analysis Based on ML and LLM](jdbc_mindsdb_ml_llm.md)
