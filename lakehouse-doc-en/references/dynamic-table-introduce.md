# Introduction to Dynamic Table

## What is a Dynamic Table

A Dynamic Table is a data object in Singdata Lakehouse. The difference from a regular table is that it dynamically generates data through a defined query statement, automatically obtaining incremental data from the Base Table during refresh, and uses incremental algorithms for computation. This approach significantly improves data processing efficiency, especially suitable for handling large-scale data.

## Application Scenarios of Dynamic Table

### Real-time Processing Scenarios

In real-time data processing scenarios, data flows into the system continuously and rapidly. Traditional data processing methods, such as Full Reload or Full Refresh, may not be efficient in terms of performance and resource consumption, especially when dealing with large-scale data streams. Dynamic Tables use incremental computation methods, processing only the data that has changed since the last update, thereby significantly reducing the consumption of computing resources.

**Advantages of Dynamic Table**:

* **Real-time**: Quickly reflects new data changes in the data warehouse, maintaining high data freshness.
* **Cost-effective**: By setting reasonable refresh intervals, it balances performance and cost, achieving optimal resource utilization.
* **Resource Elasticity**: Lakehouse resources can be easily elastically expanded, especially advantageous when handling peak data inflows.
* **On-demand Computation**: In the future, Lakehouse will achieve on-demand activation of computing resources, starting the corresponding resources only when there is data to be computed, further improving efficiency and reducing costs.

**Application Example**:

**Background**: An e-commerce company wants to analyze its sales data in real-time to make quick inventory and pricing decisions. Data flows into the system at a high rate, requiring an efficient data processing method.

**Challenges**:

* Traditional full data processing methods are inefficient in terms of performance and resource consumption, especially during peak periods.
* A processing mechanism is needed that can quickly respond to data changes and maintain data freshness.

**Solution**:

* Introduce Dynamic Tables, using incremental computation methods to process only the data that has changed since the last update.

**Advantages of Dynamic Table**:

1. **Real-time**: Dynamic Tables can quickly capture and reflect data changes, ensuring decisions are based on the latest sales data.

2. **Cost-effective**: With Dynamic Tables, the company can set reasonable data refresh intervals based on actual needs, avoiding unnecessary waste of computing resources.

3. **Resource Elasticity**: During promotional events or holidays, when traffic peaks, Lakehouse resources can be expanded on-demand to handle peak data inflows without maintaining high resource configurations long-term.

4. **On-demand Computation**: In the future, Lakehouse's on-demand computation feature will further improve efficiency, activating resources only when there is data to be computed, thereby reducing costs.

### High Data Freshness Requirements for Fixed Dimension Analysis Query Scenarios

In fixed dimension analysis query scenarios, we aim to provide near real-time analysis results. Traditional view queries can achieve this, but if a large amount of data transformation is involved, it may slow down the query speed. To solve this problem, we can materialize the transformed results, so that the query can directly return these results, thereby improving query speed. The materialized results can be in the form of traditional tables or dynamic tables.

Using traditional tables can provide the highest performance because they return pre-transformed data during queries. However, the downside of this method is that it requires regular evaluation of data transformation time and full computation through scheduling, which usually takes a long time.

Dynamic Tables combine the advantages of incremental computation. By updating only the records that have changed since the last load, Dynamic Tables not only reduce the build time each time but also maintain data freshness by shortening the time interval.

### Notes

* When handling a large amount of changing data at the source, the computation task may approach the load of full computation. Although incremental computation has obvious efficiency advantages, if you set the refresh interval too short, it may lead to task backlog. This is because each refresh operation itself takes a certain amount of time to complete, and if this time exceeds the refresh interval you set, it will cause subsequent refresh tasks to queue up.
  * **Suggestions**:
    * **Set a reasonable refresh interval**: Based on the frequency of data changes and the refresh time of the task, set a reasonable refresh interval to avoid backlog of refresh operations.
    * **Monitor and adjust**: Continuously monitor data change patterns and system performance, and adjust the refresh interval according to the actual situation to achieve optimal utilization of efficiency and resources.
* When writing operators, refer to the notes on how operators perform incremental refresh to optimize incremental refresh tasks.

## Overview of Dynamic Table Working Principle

### How to Obtain Changed Data

* MetaService (Metadata Service, a component service of Lakehouse) records every historical data version of each table in Lakehouse
  * ![](.topwrite/assets/image_1716281294985.png)
  * Basic concept: A table's **Snapshot (full)** VS **Delta (change)**


## **Lakehouse Dynamic Table Refresh Mechanism** <!--permalink-->

Lakehouse currently uses a scheduling mechanism to update Dynamic Tables. The following scheduling modes are supported:

1. **Define scheduling properties in DDL statements**
2. **Define scheduling in Lakehouse Studio**
3. **Submit Refresh jobs using a third-party scheduling engine**

|                          | Usage                                                                                                    | Advantages                                                  | Disadvantages                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Define scheduling properties in DDL statements             | Define the refresh interval in refreshOption, refer to the documentation create-dynamic-table.md for specific usage. Currently, the refresh interval is limited to one minute. | Simple and easy to use, can quickly set refresh options. Does not rely on any third-party tools. | Currently, Lakehouse does not support defining strict upstream and downstream dependencies on Dynamic Tables. In DDL definitions, it relies on time scheduling. You can ensure the upstream refresh is completed before scheduling the downstream through time intervals. |
| Define scheduling in Lakehouse Studio | You can configure scheduling through a visual interface in Lakehouse Studio, refer to the [task development scheduling documentation](taskdevelop.md) for specific configuration methods. Currently, the refresh interval is limited to one minute.                     | Visual configuration, user-friendly. Supports scheduling dependency configuration to ensure the upstream refresh is completed before refreshing the downstream. Supports single-node operation monitoring, such as failure alerts, timeout alerts, etc. |                                                                                       |
| Submitting Refresh Jobs Using Third-Party Scheduling Engines | By downloading the Lakehouse client command, use cron expressions to schedule Refresh tasks. Alternatively, use the Java Jdbc interface to customize the submission of Refresh commands. | You can more flexibly control job submission and configure scheduling information, with no time interval restrictions | Requires reliance on third-party scheduling. Introduces third-party scheduling systems |

## Comparison of Dynamic Tables, Materialized Views, and Regular Views

From the implementation mechanism of Lakehouse, dynamic tables are evolved based on traditional materialized views. Although they have some commonalities, there are significant differences in their positioning.

|       | Materialized View                                | Dynamic Table                     | Regular View                                              |
| ----- | ------------------------------------------- | --------------------------- | ------------------------------------------------- |
| Definition    | A special view that precomputes and stores query results | A high-efficiency tool focused on data processing | A virtual table that does not store data, only saves the query definition |
| Performance Optimization  | Significantly improves query efficiency by reducing redundant calculations through pre-stored results. Other SQL can utilize this materialized result for query rewriting | Although it can also improve query efficiency, the query optimizer will not rewrite the query | Performance depends on the query efficiency of the underlying data table; the query logic is recalculated each time |
| Data Timeliness | Requires immediate data updates to ensure the accuracy of query rewriting | Focuses on data processing flexibility, allowing for adjustable data latency | Data freshness is always the latest each time |
| Update Mechanism  | Uses a scheduled refresh mechanism to keep data up-to-date | Adjusted according to business definitions, not forced to update in real-time | Does not store data, no need for updates |
| Query Optimization  | Optimizer automatically identifies and uses pre-stored results | Does not rely on automatic rewriting by the query optimizer |                                                   |
| Use Case  | Suitable for scenarios where precomputed and reusable query results are needed | Suitable for data processing, where data may not be the latest | Suitable for scenarios with low query complexity and no extensive processing; if involving large data volumes and many complex operators, queries are slow because they are recalculated each time |
| Operations and Maintenance    | No complex maintenance scenarios | Dynamic tables also support complex column addition, version rollback, etc. | No complex maintenance scenarios |

## Dynamic Table Refresh Monitoring

### **View Refresh History via SQL Commands**

You can currently use SQL commands to monitor the refresh history of dynamic tables. Although this command may not be fully available yet, you can already get an overview of the refresh status of all dynamic tables with the following SQL statement:
```SQL
SHOW DYNAMIC TABLE REFRESH HISTORY [WHERE <condition>];
```
**Filter Refresh History**

You can use the `WHERE` clause to filter information based on specific fields. For example, to view the refresh history of a dynamic table named `my_dy`, you can use the following command:
```SQL
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name='my_dy';
```
| Field Name        | Meaning                                                                 |
| ----------------- | ----------------------------------------------------------------------- |
| workspace\_name   | Workspace name                                                          |
| schema\_name      | Schema name                                                             |
| name              | Dynamic table name                                                      |
| virtual\_cluster  | Computing cluster used                                                  |
| start\_time       | Refresh start time                                                      |
| end\_time         | Refresh end time                                                        |
| duration          | Refresh duration                                                        |
| state             | Job status: setup\resuming cluster\queued\running\sucess\failed\success  |
| refresh\_trigger  | MANUAL (manually triggered by user, including studio scheduling) LH\_SCHEDULED (scheduled by lakehouse) |
| suspended\_reson  | Reason for suspension                                                   |
| refresh\_mode     | NO\_DATA FULL INCREMENTAL                                               |
| error\_message    | Information on refresh failure, if any                                  |
| source\_tables    | Names of tables used by the dynamic table                               |
| stats             | Information on incremental refresh counts                               |
| job\_id           | Job ID, clicking on it shows the job profile                            |

### View the refresh status of a single job through Job Profile

In addition to SQL commands, you can also view the refresh details of a single job through Job Profile

![](.topwrite/assets/image_1716280617859.png)

* You can also determine if data is read incrementally through the input records of the job profile

## Cost of Dynamic Tables

#### **Computing Cost**

The refresh operation of dynamic tables relies on computing resources (Virtual Cluster) to execute, including:

* **Scheduled Refresh**: Automatically executes refresh based on the set interval.
* **Manual Refresh**: Users manually trigger refresh as needed.

These refresh operations consume computing resources.

#### **Storage Cost**

Dynamic tables also require storage space to save their materialized results. Like regular tables, dynamic tables support:

* **Time Travel**: Allows users to access data from any point in the past 7 days.
* **Time Travel Retention Period**: Default is set to 7 days. After this period, data will no longer be accessible through Time Travel and will be physically deleted.
**Note**: Time Travel is currently in preview, with a default retention period of 7 days. During the preview period, users can query data versions within 7 days for free, and there will be no charges for versions within this period. After the preview period ends, Lakehouse will start charging separately for storage costs incurred by using the Time Travel feature.

#### **Refresh Schedule Settings Period**

**Factors Affecting Refresh Speed**

The speed of incremental refresh mainly depends on two factors:

1. **Amount of changes in source data**: The larger the amount of data that needs to be processed during the refresh operation, the longer it will take.
2. **Fixed overhead**: Some basic overhead is incurred with each refresh, regardless of the amount of data changes.

**Business Value and Refresh Frequency**

* If data freshness is not critical to your business value, consider reducing the refresh frequency. This strategy can reduce the computational overhead caused by frequent refreshes.
* Using an incremental computation mode can increase the speed of a single refresh, as it only processes data that has changed since the last refresh.

**Balancing Refresh Costs and Frequency**

* Refresh costs will increase with the frequency of refreshes. Therefore, you need to balance the business value brought by data freshness with the computational costs incurred.
* High-frequency refresh operations can keep data updated in real-time, but the accumulated computational costs will also increase.

**Recommendations**

* Evaluate your business needs to determine the specific value of data freshness to your business.
* Set a reasonable refresh frequency based on business value to optimize cost-effectiveness.
* Use incremental computation mode to improve refresh efficiency and reduce unnecessary computational overhead.

## Dynamic Table Limitations

* Incremental refresh limitations: Non-deterministic functions such as random, current\_timestamp, current\_date, etc., are not supported.
* Direct modification of dynamic table data, such as executing update, delete, truncate data, is not supported.

# Use Cases for Processing with Dynamic Tables

## Processing Sample Data Provided by Lakehouse with Dynamic Tables

Lakehouse provides a dynamic public dataset named `ecommerce_events_multicategorystore_live`, located at `clickzetta_sample_data.clickzetta_sample_data.ecommerce_events_history`. This dataset is updated in real-time and can be queried directly.

Real-time dataset availability: Currently, the `ecommerce_events_multicategorystore_live` real-time writing public dataset is only available in the Shanghai region of Alibaba Cloud. If your account or service is not in that region, you will not be able to query this public dataset.

1. **Write SQL script to define scheduling and processing data using DDL**
```SQL
CREATE  DYNAMIC TABLE event_type_count
REFRESH interval 1 minute vcluster default
as
SELECT event_type, COUNT(*) AS events_count
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live
GROUP BY event_type;
-- Initialize DYNAMIC TABLE data
REFRESH DYNAMIC TABLE event_type_count;
```
2. View Dynamic Table Refresh

**Use commands to view dynamic table refresh**
```SQL
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name='event_type_count';
```
**View dynamic table refresh history in job history**

![](.topwrite/assets/image_1716280651911.png)

Click into the details to view the input records and see how many incremental records were obtained. In the diagnostics, you can view the execution plan of the incremental SQL.

![](.topwrite/assets/image_1716280668286.png)

3. **After seeing incremental refresh data in the job history, you can view the data changes**
```SQL
SELECT    *   FROM      event_type_count;
+-------------+--------------+
| event_type  | events_count |
+-------------+--------------+
| view        | 91634700     |
| purchase    | 91630921     |
| add_to_cart | 91622270     |
+-------------+--------------+
-- View data after incremental refresh
SELECT    *
FROM      event_type_count;
+-------------+--------------+
| event_type  | events_count |
+-------------+--------------+
| purchase    | 91633135     |
| add_to_cart | 91624515     |
| view        | 91636913     |
+-------------+--------------+
```
## Using STUDIO to Refresh Scheduled Dynamic Table Refresh Tasks

In this demonstration, we will simulate the insertion of incremental data and showcase the effects of incremental computation through the following steps:

* **Simulate Incremental Data Insertion**: Use the `INSERT INTO` statement to insert simulated data into the specified table, thereby mimicking the incremental data updates in actual business scenarios.
* **Utilize Studio Scheduling for Refresh**: Subsequently, we will use the scheduling feature of Lakehouse Studio to trigger and execute the incremental data refresh tasks.
* **Demonstrate Incremental Computation Effects**: Through the above steps, we aim to demonstrate how incremental computation efficiently processes newly inserted data and reflects the updates in the final query results.

1. Data Preparation
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
2. Data Processing

* Create a new SQL script "1. Time Processing dt" to process the prepared data using SQL to create dy

  ![](.topwrite/assets/image_1716280688236.png)
```SQL
CREATE dynamic TABLE IF NOT EXISTS event_gettime AS
SELECT    event,
          process,
          YEAR(event_time) event_year,
          MONTH(event_time) event_month,
          DAY(event_time) event_day,
          hour(event_time) event_hour,
          minute(event_time) event_minute
FROM      event_tb;

REFRESH   dynamic TABLE event_gettime;
```
* Create a new SQL script "2. Aggregate dy" to perform aggregation operations on the processed data from the previous step
  * ```SQL
    CREATE dynamic TABLE IF NOT EXISTS event_group_minute AS
    SELECT    event,
              event_hour,
              event_minute,
              SUM(process) process_sum
    FROM      event_gettime
    GROUP BY  event,
              event_hour,
              event_minute;

    refresh dynamic table event_group_minute;
    ```
### 3. Build Dependencies and Scheduling Relationships

* Task one "1. Time Processing dy" is configured to be scheduled once every minute

  * ![](.topwrite/assets/image_1716280711741.png)

* Task two "2. Aggregation dy" is configured to be scheduled once every minute like task one and is set to **depend on task one "1. Time Processing dy"** in the scheduling dependencies

  * ![](.topwrite/assets/image_1716280739978.png)

* In the data development interface, click to submit each task

  * ![](.topwrite/assets/image_1716280770050.png)

### 4. Check for Incremental Refresh
```SQL
--Manually insert data
INSERT INTO event_tb VALUES
  ('event-0', 20.0, TIMESTAMP '2024-01-20 14:43:13');
 --Check if event_gettime is incrementally refreshed and how many rows are incrementally refreshed
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name='event_gettime';
+----------------+-------------+---------------+-----------------+-------------------------+-------------------------+----------------------+---------+-----------------+------------------+--------------+---------------+-------------------------------------------------------------------+------------------------------------------+-------------------+-------------------------------+
| workspace_name | schema_name |     name      | virtual_cluster |       start_time        |        end_time         |       duration       |  state  | refresh_trigger | suspended_reason | refresh_mode | error_message |                           source_tables                           |                  stats                   | completion_target |            job_id             |
+----------------+-------------+---------------+-----------------+-------------------------+-------------------------+----------------------+---------+-----------------+------------------+--------------+---------------+-------------------------------------------------------------------+------------------------------------------+-------------------+-------------------------------+
| ql_ws          | public      | event_gettime | DEFAULT         | 2024-05-17 11:33:15.512 | 2024-05-17 11:33:15.839 | 0 00:00:00.327000000 | SUCCEED | MANUAL          | null             | INCREMENTAL  | null          | [{"schema":"public","table_name":"event_tb","workspace":"ql_ws"}] | {"rows_deleted":"0","rows_inserted":"1"} | null              | 202405170333149794gibwyt3dv0g |
+----------------+-------------+---------------+-----------------+-------------------------+-------------------------+----------------------+---------+-----------------+------------------+--------------+---------------+-------------------------------------------------------------------+------------------------------------------+-------------------+-------------------------------+
```


