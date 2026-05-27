# Streaming SQL Task

【**Preview Release】 This feature is currently in an invitation-only preview phase. If access is required, please contact our technical support team for assistance**&#x20;

^

Streaming SQL is a new type of SQL scheduling mode introduced by the Lakehouse platform. It adopts a micro-batch processing mechanism, supporting second-level data refresh intervals, similar to the micro-batch execution method of Spark Streaming. Compared to traditional scheduled tasks, Streaming SQL can significantly reduce the overhead of submitting and compiling SQL because it converts the submitted SQL into a resident process that automatically triggers data execution and processing once the set time interval is reached. Streaming SQL is currently aimed at scenarios requiring higher data freshness and currently supports dt refresh and processing data containing table stream.

To better understand the advantages of Streaming SQL, we can compare it with the execution process of regular SQL:

**Regular SQL Execution Process**

* Syntax Parser (Parser): Lexical analysis, syntax analysis to parse SQL text into an abstract syntax tree (AST), semantic analysis, type inference, and checking. Produces Logical Plan.

* Query Optimizer (Optimizer): Transforms the plan through rules and finds the best plan based on the cost model.

  * RBO: Rule-Based Optimizer, optimizes based on the SQL statements issued by the user, mainly by changing the SQL, such as the execution order of SQL clauses. Common optimizations include predicate pushdown, field filtering pushdown, constant folding, index selection, join optimization, etc.
  * CBO: Cost-Based Optimizer, calculates the cost of each execution method based on collected statistics and selects the optimal execution method.
  * HBO: History-Based Optimizer, an optimizer based on historical data.

* Generate DAG Diagram: The DAG describes the specific mapping of the execution plan to the physical distributed cluster. Based on the execution plan, distributed execution reflects the materialization of the execution plan to the distributed system, with features such as concurrency, data transmission methods, ensuring orderliness and reliability.

* Executor reads data for computation.

**Streaming SQL Execution Process**

1. **First Submission and Physical Execution Plan Generation**:

   1. During the first submission of Streaming SQL, the system performs a complete compilation process, including syntax parsing, query optimization, and physical execution plan generation.
   2. The physical execution plan (DAG diagram) generated at this stage will be solidified for subsequent execution cycles.

2. **Subsequent Execution Optimization**:

   1. Once the physical execution plan is generated and solidified, subsequent execution cycles will mostly use this plan directly without recompilation.
   2. This means that each time data arrives, Streaming SQL can skip the time-consuming parsing and optimization steps and directly enter the execution phase.
   3. During execution, the optimizer will also monitor the amount of data to be processed each time. If the data volume changes significantly, making the execution plan suboptimal, the optimizer will regenerate and solidify the physical execution plan.

#### Comparison of Scheduled Tasks and Streaming SQL

* **Regular Scheduled Tasks**:

  * Each execution requires re-parsing and optimizing SQL, adding extra overhead.
  * The time interval usually needs to be set relatively large to reduce scheduling frequency and resource consumption.

* **Streaming SQL**:

  * By eliminating the repetitive compilation process, Streaming SQL can support smaller time intervals, achieving higher frequency data updates and processing.
  * This mode is particularly suitable for applications requiring real-time or near-real-time data processing.

# Applicable Scenarios for Streaming SQL

The introduction of Streaming SQL brings greater flexibility and real-time capabilities to data processing. In the DDL (Data Definition Language) definition of dynamic tables, the scheduling interval usually has a minimum value, such as one minute. This means that data updates and processing will have at least a one-minute delay. However, Streaming SQL, through its micro-batch processing mechanism, allows this interval to be shortened to seconds, achieving faster data response and processing.

* **Real-time Data Processing**: Streaming SQL can quickly respond to data changes, suitable for applications requiring real-time data processing and analysis.
* **High-frequency Data Updates**: For systems requiring frequent data updates, Streaming SQL can reduce the delay of each update, improving the real-time nature of data processing.

# Limitations of Streaming SQL

* Requires dynamic tables or SQL processing containing table stream. Regular SQL is not supported for now.
* Jobs must run on an analytical (ap) cluster.
* Currently, only the Lakehouse interface supports developing Streaming SQL. Only one DML SQL task can be processed in an SQL file.

# How to Use Streaming SQL

## Developing Streaming SQL Tasks

1. Create a new Streaming SQL node in Data Development.

2. Write SQL Tasks

The submitted SQL task can only contain one DML SQL statement. During the development phase, any SQL can be written without restrictions. However, during the startup phase, it will be checked whether the SQL conforms to Streaming SQL.

Streaming SQL Requirements

* Requires dynamic tables or SQL processing containing table stream.
* Jobs must run on an analytical (ap) cluster.
* Only one SQL task can be processed in an SQL file.

**Configure Processing Interval**

Click the configuration button to set the refresh interval, which determines how often the data is processed. The shortest interval currently is 1 second.

## Running Streaming SQL Tasks

* Clicking the submit button will submit the streaming SQL to the operations center

* Start the streaming SQL. Go to the operations center and click the start button. The streaming SQL will then run

## Streaming SQL Operations

* In the operations center interface, you can see the list of all streaming SQL in the current workspace.

* The running process of streaming SQL can be viewed through the job ID

## Streaming SQL Monitoring and Alerts

Monitoring and alerts support failure alerts for streaming SQL task execution

# Specific Use Case of Streaming SQL

## Using Streaming SQL with TABLE STREM

This case uses TABLE STREM to implement the first type of Slowly Changing Dimension (SCD) with overwrite updates. It also uses micro-batch processing of streaming SQL to ensure data freshness.

[Slowly Changing Dimension](https://developer.baidu.com/article/detail.html?id=371363) (SCD) is a method for handling data changes in a data warehouse. In a data warehouse, data is typically integrated from multiple data sources. Over time, the data in these sources may change, such as updates, additions, or deletions. SCD is a technique used to handle and update these data changes. There are multiple types of SCD, including SCD1: overwrite updates, SCD2: historical records, etc.

We simulate that when the data in the original table changes, the slowly changing dimension table will also change through streaming SQL processing.

1. Create a new ordinary SQL node. Execute the following SQL to create the original table, insert some test data, and enable table stream to capture changes in the original table.

```SQL
create schema continuous_job;
drop table if exists continuous_job.test_table_offset;
drop table stream  if exists continuous_job.test_table_offset_stream;
-- Create the original table
CREATE TABLE continuous_job.test_table_offset (id INT, name VARCHAR, age INT);
-- Must be enabled when creating table stream
ALTER TABLE continuous_job.test_table_offset set PROPERTIES ('change_tracking' = 'true');
CREATE table stream continuous_job.test_table_offset_stream ON TABLE continuous_job.test_table_offset
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');
-- Insert some data into the test table
INSERT INTO continuous_job.test_table_offset VALUES
  (1, 'Alice', 20),
  (2, 'Bob', 25),
  (3, 'Charlie', 30),
  (4, 'David', 35),
  (5, 'Eve', 40);
```

2. Create a Slowly Changing Dimension Table to Keep Consistent with the Original Table

```SQL
drop table  if exists test_table_offset_consume;
-- Create target table
CREATE TABLE continuous_job.test_table_offset_consume (id INT, name VARCHAR, age INT);
```

```markdown
### 3. Create a new streaming SQL node and copy the following SQL into the streaming SQL node. We set a 20-second interval to process the data once
```

```SQL
MERGE INTO continuous_job.test_table_offset_consume target USING continuous_job.test_table_offset_stream source_stream ON target.id = source_stream.id WHEN MATCHED
AND source_stream.__change_type = 'UPDATE_AFTER' THEN update set target.age = source_stream.age WHEN MATCHED
AND source_stream.__change_type = 'DELETE' THEN DELETE WHEN NOT MATCHED
AND source_stream.__change_type = 'INSERT' THEN
INSERT VALUES (target.id, target.name, target.age);
```

4. Submit the streaming SQL and click start in the operations center

5. By updating the original table data, after the streaming SQL runs successfully, the SCD table will also be consistent with the streaming SQL

* Execute SQL on a regular node

```SQL
-- Update some data in the original table
update continuous_job.test_table_offset set age = age + 5 WHERE id = 1 OR id = 3;
-- Wait for 20s, continues job executes successfully. Verify if the data in the scd table and the original table are consistent
select "test_table_offset", * from continuous_job.test_table_offset
union all
SELECT "test_table_offset_consume",* FROM continuous_job.test_table_offset_consume;

-- Delete some data from the test table
DELETE FROM continuous_job.test_table_offset WHERE id = 2 OR id = 4;
-- Wait for 20s, continues job executes successfully. Verify if the data in the scd table and the original table are consistent
select "test_table_offset", * from continuous_job.test_table_offset
union all
SELECT "test_table_offset_consume",* FROM continuous_job.test_table_offset_consume;
```

6. Clean up the environment

* Stop streaming SQL in the Operations Center

* Delete schema

```SQL
drop schema continuous_job;
```

## Using Dynamic Table with Streaming SQL

In this case, a dynamic table is used to aggregate data by time. Streaming SQL micro-batch scheduling is used to improve data freshness.

* Create an ods table

```SQL
CREATE TABLE event_tb (
    event STRING,
    process DOUBLE,
    event_time TIMESTAMP
  );
INSERT INTO event_tb VALUES
  ('event-0', 20.0, TIMESTAMP '2023-09-20 14:43:13'),
  ('event-0', 20.0, TIMESTAMP '2023-09-19 11:40:13'),
  ('event-1', 21.0, TIMESTAMP '2023-09-19 14:30:14'),
  ('event-1', 22.0, TIMESTAMP '2023-09-20 14:20:15');
```

* Use dynamic tables for aggregation. Create dynamic tables in a regular SQL node, be careful not to set the scheduling period in the ddl

```SQL
CREATE dynamic table IF NOT EXISTS event_group_minute AS
SELECT
  event,
  hour(event_time) hour,
  year(event_time) year,
  SUM(process) process_sum
FROM
  event_tb
GROUP BY
  event,
  year(event_time),
  hour(event_time);
```

* Create a new streaming SQL node, copy the SQL below into the node content, and configure it to run every 10 seconds

```SQL
refresh dynamic table event_group_minute;
```

* Start streaming SQL to refresh the dynamic table

* Create a new regular SQL node, insert some data into the original table, and check if the dynamic table is refreshed successfully

```SQL

  INSERT INTO event_tb VALUES
  ('event-0', 20.0, TIMESTAMP '2024-09-20 14:43:13'),
  ('event-0', 20.0, TIMESTAMP '2024-09-19 11:40:13'),
  ('event-1', 21.0, TIMESTAMP '2024-09-19 14:30:14'),
  ('event-1', 22.0, TIMESTAMP '2024-09-20 14:20:15');
  
  --Wait for 10s to observe the dynamic table changes
  select * from event_group_minute;  
```

^
