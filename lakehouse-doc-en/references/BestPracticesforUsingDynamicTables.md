# Introduction to Dynamic Tables

## What is a Dynamic Table

A Dynamic Table is a data object in Cloud Lakehouse. It is distinguished from regular tables by dynamically generating data through a defined query statement. During refresh, it automatically retrieves incremental data from the Base Table and uses an incremental algorithm for computation. This approach significantly enhances data processing efficiency, especially for handling large-scale data.

## Application Scenarios for Dynamic Tables

### Real-time Processing Scenarios

In real-time data processing scenarios, data flows into the system continuously and rapidly. Traditional data processing methods, such as Full Reload or Full Refresh, may not be efficient in terms of performance and resource consumption, particularly when dealing with large data streams. Dynamic Tables use incremental computation methods, processing only the data that has changed since the last update, which significantly reduces the consumption of computing resources.

**Advantages of Dynamic Tables:**

* **Real-time**: Quickly reflects new data changes in the data warehouse, maintaining high data freshness.
* **Cost-effective**: By setting a reasonable refresh interval, it balances performance with cost, optimizing resource utilization.
* **Resource elasticity**: Lakehouse resources can be easily scaled elastically, especially advantageous during peak data inflow periods.
* **On-demand computing**: Future Lakehouse implementations will activate computing resources only when data needs to be computed, further improving efficiency and reducing costs.

**Application Example:**

**Background**: An e-commerce company wants to analyze its sales data in real-time to make quick inventory and pricing decisions. Data flows into the system at a high rate, requiring an efficient data processing method.

**Challenges**:

* Traditional full data processing methods are inefficient in terms of performance and resource consumption, especially during peak times.
* There is a need for a mechanism that can quickly respond to data changes and maintain data freshness.

**Solution**:

* Introduce Dynamic Tables that use incremental computation methods, processing only the data that has changed since the last update.

**Advantages of Dynamic Tables**:

1. **Real-time**: Dynamic Tables quickly capture and reflect data changes, ensuring decisions are based on the latest sales data.
2. **Cost-effective**: The company can set a reasonable data refresh interval according to actual needs, avoiding unnecessary waste of computing resources.
3. **Resource elasticity**: During peak traffic periods such as promotional events or holidays, Lakehouse resources can be scaled on demand to cope with data inflow peaks without maintaining a high resource configuration for long periods.
4. **On-demand computing**: In the future, Lakehouse's on-demand computing feature will further improve efficiency by activating resources only when data needs to be computed, thereby reducing costs.

### Fixed Dimension Analysis Query Scenarios

In fixed dimension analysis query scenarios, we strive to provide near real-time analysis results. Traditional view queries can achieve this, but if they involve a large amount of data transformation, they may slow down the query speed. To address this issue, we can materialize the transformed results, which allows queries to directly return these results, thus improving query speed. Materialized results can use traditional tables or Dynamic Tables.

Using traditional tables can provide the highest performance as they only return pre-transformed data during queries. However, the downside is that it requires periodic assessment of the data transformation time and full-scale computation through scheduling, which usually takes a long time.

Dynamic Tables combine the advantages of incremental computation. By only updating records that have changed since the last load, Dynamic Tables not only reduce the time required for each build but also maintain data recency by shortening the time interval.

**Notes**

* When dealing with a large amount of changing data from the source, the computation task may approach the load of a full-scale computation. Although incremental computation has significant efficiency advantages, setting a refresh interval that is too short may lead to task backlog. This is because each refresh operation itself requires a certain amount of time to complete, and if this time exceeds the set refresh interval, it will cause subsequent refresh tasks to queue up and wait.

  * **Recommendations**:

    * Set a reasonable refresh interval based on the frequency of data changes and the time required for task refresh to avoid backlog.
    * Continuously monitor and adjust the refresh interval according to actual data change patterns and system performance to optimize the use of resources and efficiency.

## Overview of How Dynamic Tables Work

### **How to Obtain Changed Data**:

* MetaService (a component service of Lakehouse) records every historical data version of each table in Lakehouse.

  * ![](.topwrite/assets/image_1716281490512.png)

* Basic Concepts: A Snapshot (full volume) VS Delta (change) of a table.

### Incremental Refresh of Operators

Below is the translation of the provided content into English, presented in a tabular format:
| Operator                                         | Incremental Method                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SELECT \<scalar expressions>                     | Obtains incremental data and then passes the changed data into the expressions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| WHERE \<scalar expressions>                      | "Implements incremental computation by evaluating the predicate for each changed row and including only the rows that satisfy the predicate."                                                                                                                                                                                                                                                                                                                                                                                                                                                              | "Performance scales linearly with the size of the changes."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| FROM \<base table>                               | "This method implements incremental computation by scanning the data that has been added to or removed from the table since the last refresh."                                                                                                                                                                                                                                                                                                                                                                                                                                                             | "Performance consumption is linearly related to the size of the added/removed data."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Suggestions:                                     | "Limit the amount of change per refresh to about 5% of the source table."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| \<query> UNION ALL \<query>                      | "Implements incremental computation by performing a union operation on the changes from both sides of the union-all."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| WITH \<CTE list> \<query>                        | "Implements incremental computation by calculating the changes for each CTE."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | "If the Query within the WITH statement is too complex, the entire WITH can be split out and established as a separate dynamic table."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| in \<subquery>                                   | "The IN operation is equivalent to a Semi-join, and the incremental algorithm is the same as Semi-join."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| GROUP BY \<keys>                                 | "This method implements incremental computation by recalculating the aggregate functions for each group key that has changed."                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| DISTINCT                                         | "Equivalent to group by without aggregate functions."                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | "In incremental refresh, since duplicates need to be checked with each refresh, the DISTINCT operation will repeatedly consume resources. A simple method to optimize performance is to find and remove unnecessary DISTINCT operations, which can be achieved by further eliminating duplicates upstream and carefully considering the join cardinality."                                                                                                                                                                                                                                                                         |
| \<fn> OVER \<window>                             | "Lakehouse currently implements partial incremental window functions (lag, row\_number), which implement incremental computation by recalculating the window functions for each partition key that has changed."                                                                                                                                                                                                                                                                                                                                                                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| \<left> INNER JOIN \<right>                      | "First, join the changed data on the left with the changed data on the right. Then, join the result with the changed data on the left again."                                                                                                                                                                                                                                                                                                                                                                                                                                                              | If one side of the join has a small amount of data, the performance may not be significantly affected. Joining a small amount of data usually does not significantly increase the computation cost.If one side of the join frequently updates, clustering the other side's data according to the join key may improve performance. This is because it can quickly locate the rows in the other table that match the updated data."                                                                                                                                                                                                 |
| \<left> \[{LEFT RIGHT FULL}] OUTER JOIN \<right> | Taking a Left Join as an example, the OUTER JOIN is broken down into multiple parts:Calculate the increment by comparing the changes in the left table with the right table.Calculate the increment by comparing the changes in the right table with the left table.Distinguish between deleted and newly added data from the right table's increment and search within the left table. It is necessary to remove the NULLs from the original Join calculation results (rows that originally couldn't join now can join) / or set the results to NULL (rows that could originally join have been deleted). | Recommendations:If one side of the join is frequently updated, clustering the other side's data based on the join key may improve performance.Place the table that is updated more frequently on the left side of the join.Minimize updates to the side that is not the outer join table (OUTER). For example, for a LEFT OUTER JOIN, try to minimize updates to the right table. This is because a LEFT OUTER JOIN will include all rows from the left table in the result, and if there are no matching records on the right, they will be filled with NULL values. Frequent updates to the result table can reduce performance. |


## Lakehouse Dynamic Table Refresh Mechanism

Lakehouse currently uses a scheduling mechanism to update Dynamic Tables. It supports the following scheduling modes:

1. Defining scheduling attributes in DDL statements.
2. Defining scheduling in Lakehouse Studio.
3. Submitting Refresh jobs using a third-party scheduling engine.

| Operator                      | Advantages                                                                                                                                                                                                                                       | Disadvantages                                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| DDL Statements                | - Easy to use, allowing quick setup of refresh options.\<br>- Does not rely on any third-party tools.                                                                                                                                            | - Current Lakehouse does not support strict upstream and downstream dependencies on Dynamic Tables.\<br>- Scheduling is based on time intervals. |
| Lakehouse Studio              | - Visual configuration, user-friendly.\<br>- Supports scheduling dependency configuration to ensure upstream refresh is completed before downstream.\<br>- Supports single-node operation monitoring, such as failure alerts and timeout alerts. | - Currently limited to a refresh interval of one minute.                                                                                         |
| Third-Party Scheduling Engine | - More flexible control over job submission and scheduling information.\<br>- No time interval restrictions.                                                                                                                                     | - Requires reliance on third-party scheduling systems.                                                                                           |

## Dynamic Table vs. Materialized View

* Dynamic Tables have evolved from traditional materialized views. While they share some commonalities, there are significant differences in their positioning.

## Dynamic Table Refresh Monitoring

### **Viewing **Refresh** History with SQL Commands**:

* You can currently use SQL commands to monitor the refresh history of Dynamic Tables. Although the command may not be fully available, you can already obtain an overview of the refresh status of all Dynamic Tables through the following SQL statement:

  * ```Plain
    SHOW DYNAMIC TABLE REFRESH HISTORY [WHERE <condition>];
    ```

**Filtering Refresh History**

* You can use the WHERE clause to filter information based on specific fields. For example, to view the refresh history of a Dynamic Table named my\_dy, you can use the following command:

  * ```Plain
    SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name='my_dy';
    ```



|                   |                                                                                                                                                             |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| workspace\_name   | Workspace Name                                                                                                                                              |
| schema\_name      | Schema Name                                                                                                                                                 |
| name              | Dynamic Table Name                                                                                                                                          |
| virtual\_cluster  | Virtual Cluster Used                                                                                                                                        |
| start\_time       | Refresh Start Time                                                                                                                                          |
| end\_time         | Refresh End Time                                                                                                                                            |
| duration          | Refresh Duration                                                                                                                                            |
| state             | "Job Status, setup\resuming cluster\queued\running\success\failed"                                                                                          |
| refresh\_trigger  | "Refresh Trigger, MANUAL (Manual refresh triggered by user, including Studio scheduled refresh), LH\_SCHEDULED (Refresh triggered by Lakehouse scheduling)" |
| suspended\_reason | Suspended Reason                                                                                                                                            |
| refresh\_mode     | "Refresh Mode, NO\_DATA, FULL, INCREMENTAL"                                                                                                                 |
| error\_message    | Error Message (if refresh fails, the information will be here)                                                                                              |
| source\_tables    | Records the table names used by the dynamic table                                                                                                           |
| stats             | Incremental Refresh Counts and Other Information                                                                                                            |
| job\_id           | Job ID, by clicking on the Job ID, you can view the job profile                                                                                             |



### Job Profile for Individual Job Refresh Status

* In addition to SQL commands, you can also view the refresh details of individual jobs through the Job Profile.

![](.topwrite/assets/image_1716281689154.png)

![](.topwrite/assets/image_1716281707296.png)

## Dynamic Table Costs

### **Computing Costs**:

* The refresh operations of Dynamic Tables rely on computing resources (Virtual Cluster) to execute, including:

  * Scheduled refresh: Automatically performs refresh based on the set time interval.
  * Manual refresh: Triggered manually by the user as needed.

### **Storage Costs**:

* Dynamic Tables also require storage space to save their materialized results. Like regular tables, Dynamic Tables support:

  * Time Travel: Allows users to access data from any point in time within the past 7 days.
  * Time Travel Retention Period: The default setting is 7 days. After this period, data will no longer be accessible via Time Travel and will be physically deleted.

### Refresh Scheduling and Frequency

* **Factors Affecting Incremental Refresh Speed**:

  * The amount of changed data in the source: The larger the data volume that needs to be processed during a refresh, the longer the time required.
  * Fixed overhead: Some basic overhead is incurred with each refresh, regardless of the amount of data change.

<!---->

* **Business Value vs. Refresh Frequency**:

  * If data freshness is not critical to your business value, you may consider reducing the refresh frequency. This strategy can reduce the computational overhead caused by frequent refreshes.
  * Incremental computation mode can increase the speed of a single refresh because it only processes data that has changed since the last refresh.

<!---->

* **Balancing Refresh Costs and Frequency**:

  * Refresh costs will rise with increased refresh frequency. Therefore, you need to balance the business value brought by data freshness against the resulting computational costs.
  * High-frequency refresh operations can maintain real-time data updates, but the cumulative computational costs will also increase.

**Recommendations**

* Assess your business needs to determine the specific value of data freshness to your business.
* Set a reasonable refresh frequency based on business value to optimize cost-effectiveness.
* Utilize incremental computation mode to improve refresh efficiency and reduce unnecessary computational overhead.

## Dynamic Table Limitations

* Incremental refresh limitations: Do not support non-deterministic functions, such as random, current\_timestamp, current\_date, etc.
* Do not support direct modification of Dynamic Table data, such as performing update, delete, truncate operations.

# Using Dynamic Tables for Data Processing

## Processing Lakehouse Sample Data:

Lakehouse provides a dynamic public dataset named ecommerce\_events\_multicategorystore\_live, located under the path clickzetta\_sample\_data.clickzetta\_sample\_data.ecommerce\_events\_history. This dataset is updated in real-time and can be queried directly.

**Real-time Dataset Availability**:Currently, the ecommerce\_events\_multicategorystore\_live real-time writing public dataset is only available in the Shanghai region of Alibaba Cloud. If your account or service is not in this region, you will not be able to query this public dataset.

1. Writing SQL Scripts to Define Scheduled Data Processing

```SQL
CREATE DYNAMIC TABLE event_type_count
PROPERTIES ('refresh_vc'='default')
REFRESH interval 1 minute
AS
SELECT event_type, COUNT(*) AS events_count
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live
GROUP BY event_type;
-- Initialize DYNAMIC TABLE data
REFRESH DYNAMIC TABLE event_type_count;
```

2. **Viewing Dynamic Table Refresh**

```SQL
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name='event_type_count';
```

Viewing Data Changes After Incremental Refresh

```SQL
SELECT * FROM event_type_count;
+-------------+--------------+
| event_type  | events_count |
+-------------+--------------+
| view        | 91634700     |
| purchase    | 91630921     |
| add_to_cart | 91622270     |
+-------------+--------------+
-- After incremental refresh
SELECT * FROM event_type_count;
+-------------+--------------+
| event_type  | events_count |
+-------------+--------------+
| purchase    | 91633135     |
| add_to_cart | 91624515     |
| view        | 91636913     |
+-------------+--------------+
```

## Using STUDIO to Schedule Dynamic Table Refresh Tasks

In this demonstration, we will simulate the insertion of incremental data and showcase the effects of incremental computation through the following steps:

* **Simulating Incremental Data Insertion**: Use the INSERT INTO statement to insert simulated data into a specified table, simulating incremental data updates in actual business scenarios.
* **Scheduling Refresh with Studio**: We will then use the scheduling feature of Lakehouse Studio to trigger and execute refresh tasks for incremental data.
* **Demonstrating Incremental Computation Effects**: Through the above steps, we aim to show how incremental computation efficiently processes newly inserted data and reflects the updates in the final query results.

1. **Data Preparation**

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

2. **Data Processing**

![](.topwrite/assets/image_1716281736152.png)

* Create a new SQL script "1. Time Processing dt" to process the prepared data using SQL to create a dynamic table.

```SQL
CREATE dynamic table if not exists event_gettime AS
SELECT
  event,
  process,
  YEAR(event_time) event_year,
  MONTH(event_time) event_month,
  DAY(event_time) event_day,
  hour(event_time) event_hour,
  minute(event_time) event_minute
FROM event_tb;
refresh dynamic table event_gettime;
```

* Create a new SQL script "2. Aggregation dy" to perform aggregation operations on the data processed in the previous step.

```SQL
CREATE dynamic table IF NOT EXISTS event_group_minute AS
SELECT
  event,
  event_hour,
  event_minute,
  SUM(process) process_sum
FROM
  event_gettime
GROUP BY
  event,
  event_hour,
  event_minute;
refresh dynamic table event_group_minute;
```

3. **Building Dependencies and Scheduling Relationships**

* Task one "1.TimeProcessing\_dy" is configured to schedule once a minute.

![](.topwrite/assets/image_1716281754103.png)

* Task two "2.Aggregation\_dy" is also configured to schedule once a minute and depends on task one "1.TimeProcessing\_dy".

![](.topwrite/assets/image_1716281775201.png)

4. Checking for Incremental Refresh

* Manually insert data and check if the dynamic table is incrementally refreshed and how many records have been refreshed.

```SQL
-- Manually insert data
INSERT INTO event_tb VALUES
  ('event-0', 20.0, TIMESTAMP '2024-01-20 14:43:13');
-- Check if event_gettime is incrementally refreshed and how many records have been refreshed
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name='event_gettime';
+----------------+-------------+---------------+-----------------+-------------------------+-------------------------+----------------------+---------+-----------------+------------------+--------------+---------------+-------------------------------------------------------------------+------------------------------------------+-------------------+-------------------------------+
| workspace_name | schema_name |     name      | virtual_cluster |       start_time        |        end_time         |       duration       |  state  | refresh_trigger | suspended_reason | refresh_mode | error_message |                           source_tables                           |                  stats                   | completion_target |            job_id             |
+----------------+-------------+---------------+-----------------+-------------------------+-------------------------+----------------------+---------+-----------------+------------------+--------------+---------------+-------------------------------------------------------------------+------------------------------------------+-------------------+-------------------------------+
| ql_ws          | public      | event_gettime | DEFAULT         | 2024-05-17 11:33:15.512 | 2024-05-17 11:33:15.839 | 0 00:00:00.327000000 | SUCCEED | MANUAL          | null             | INCREMENTAL  | null          | [{"schema":"public","table_name":"event_tb","workspace":"ql_ws"}] | {"rows_deleted":"0","rows_inserted":"1"} | null              | 202405170333149794gibwyt3dv0g |
+----------------+-------------+---------------+-----------------+-------------------------+-------------------------+----------------------+---------+-----------------+------------------+--------------+---------------+-------------------------------------------------------------------+------------------------------------------+-------------------+-------------------------------+
```
