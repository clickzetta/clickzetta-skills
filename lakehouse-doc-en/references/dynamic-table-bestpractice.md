# Best Practices for Using Dynamic Table

## What is a Dynamic Table

A Dynamic Table is a data object in Singdata Lakehouse. The difference from a regular table is that it dynamically generates data through a defined query statement, automatically fetching incremental data from the Base Table during refresh, and using incremental algorithms for computation. This approach significantly improves data processing efficiency, especially suitable for handling large-scale data.

## Application Scenarios of Dynamic Tables

### Real-time Processing Scenarios

In real-time data processing scenarios, data flows into the system continuously and rapidly. Traditional data processing methods, such as Full Reload or Full Refresh, may not be efficient in terms of performance and resource consumption, especially when dealing with large-scale data streams. Dynamic Tables use incremental computation methods, processing only the data that has changed since the last update, thereby significantly reducing the consumption of computing resources.

**Advantages of Dynamic Tables**:

* **Real-time**: Quickly reflects new data changes in the data warehouse, maintaining high data freshness.
* **Cost-effective**: By setting reasonable refresh intervals, it balances performance and cost, achieving optimal resource utilization.
* **Resource Elasticity**: Lakehouse resources can be easily elastically expanded, especially advantageous when handling peak data inflows.
* **On-demand Computation**: In the future, Lakehouse will achieve on-demand computation, starting computing resources only when data needs to be processed, further improving efficiency and reducing costs.

**Application Example**:

**Background**: An e-commerce company wants to analyze its sales data in real-time to make quick inventory and pricing decisions. Data flows into the system at a high rate, requiring an efficient data processing method.

**Challenges**:

* Traditional full data processing methods are inefficient in terms of performance and resource consumption, especially during peak periods.
* A mechanism is needed to quickly respond to data changes and maintain data freshness.

**Solution**:

* Introduce Dynamic Tables, using incremental computation methods to process only the data that has changed since the last update.

**Advantages of Dynamic Tables**:

1. **Real-time**: Dynamic Tables can quickly capture and reflect data changes, ensuring decisions are based on the latest sales data.

2. **Cost-effective**: With Dynamic Tables, the company can set reasonable data refresh intervals based on actual needs, avoiding unnecessary waste of computing resources.

3. **Resource Elasticity**: During promotional events or holidays, Lakehouse resources can be expanded on-demand to handle peak data inflows without maintaining high resource configurations long-term.

4. **On-demand Computation**: In the future, Lakehouse's on-demand computation feature will further improve efficiency, starting resources only when data needs to be processed, thereby reducing costs.

### High Data Freshness Requirements for Fixed Dimension Analysis Query Scenarios

In fixed dimension analysis query scenarios, the goal is to provide near real-time analysis results. Traditional view queries can achieve this, but if a large amount of data transformation is involved, it may slow down the query speed. To solve this problem, we can materialize the transformed results, so that the query can directly return these results, thereby improving query speed. The materialized results can be in the form of traditional tables or dynamic tables.

Using traditional tables can provide the highest performance because they return pre-transformed data during queries. However, the downside of this method is that it requires regular evaluation of data transformation time and full computation through scheduling, which usually takes a long time.

Dynamic Tables combine the advantages of incremental computation. By updating only the records that have changed since the last load, Dynamic Tables not only reduce the time for each build but also maintain data freshness by shortening the time interval.

### Notes

* When handling a large amount of changing data at the source, the computation task may approach the load of full computation. Although incremental computation has significant efficiency advantages, if you set the refresh interval too short, it may lead to task backlog. This is because each refresh operation itself takes a certain amount of time to complete, and if this time exceeds the refresh interval you set, it will cause subsequent refresh tasks to queue up.
  * **Suggestions**:
    * **Set a reasonable refresh interval**: Based on the frequency of data changes and the refresh time of tasks, set a reasonable refresh interval to avoid backlog of refresh operations.
    * **Monitor and adjust**: Continuously monitor data change patterns and system performance, and adjust the refresh interval according to the actual situation to achieve optimal utilization of efficiency and resources.
* When writing operators, refer to the notes on how operators perform incremental refresh to optimize incremental refresh tasks.

## Overview of How Dynamic Tables Work

### How to Get Changed Data

* MetaService (a component service of Lakehouse) records every historical data version of each table in Lakehouse

  :-: ![](.topwrite/assets/image_1716281294985.png =633)

  * Basic concept: A table's **Snapshot (full**) VS **Delta (change**)


## **Lakehouse Dynamic Table Refresh Mechanism**&#x20;

Lakehouse currently uses a scheduling mechanism to update Dynamic Table. The following scheduling modes are supported:

1. **Define scheduling attributes in DDL statements**
2. **Define scheduling in Lakehouse Studio**
3. **Submit Refresh jobs using a third-party scheduling engine**

|                                                              | Usage                                                                                                                                                                                                                                           | Advantages                                                                                                                                                                                                                                | Disadvantages                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Define scheduling attributes in DDL statements               | Define the refresh interval in refreshOption, refer to the documentation <https://dev-doc.clickzetta.com/zh-CN/create-dynamic-table> for specific usage. Currently, the refresh interval is limited to one minute.                              | Simple and easy to use, can quickly set refresh options. Does not rely on any third-party tools.                                                                                                                                          | Currently, Lakehouse does not support defining strict upstream and downstream dependencies on Dynamic Table. In DDL definition, it relies on time scheduling. You can ensure upstream refresh completion before scheduling downstream through time intervals. |
| Define scheduling in Lakehouse Studio                        | You can configure scheduling through a visual interface in Lakehouse Studio, refer to [Task Development Scheduling Documentation](taskdevelop.md) for specific configuration methods. Currently, the refresh interval is limited to one minute. | Visual configuration, user-friendly. Supports scheduling dependency configuration to ensure downstream refresh after upstream refresh completion. Supports single-node operation monitoring, such as failure alerts, timeout alerts, etc. |                                                                                                                                                                                                                                                               |
| Submitting Refresh Jobs Using Third-Party Scheduling Engines | By downloading the Lakehouse client command, use cron expressions to schedule Refresh tasks. Alternatively, use the Java Jdbc interface to customize the submission of Refresh commands.                                                        | You can more flexibly control job submission and configure scheduling information, with no time interval restrictions                                                                                                                     | Requires reliance on third-party scheduling. Introduces third-party scheduling systems                                                                                                                                                                        |

## Comparison of Dynamic Tables, Materialized Views, and Regular Views

From the implementation mechanism of Lakehouse, dynamic tables are evolved based on traditional materialized views. Although they have some commonalities, there are significant differences in their positioning.

|                            | Materialized Views                                                                                                                                                        | Dynamic Tables                                                                                | Regular Views                                                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Definition                 | A special view that precomputes and stores query results                                                                                                                  | An efficient tool focused on data processing                                                  | A virtual table that does not store data, only saves query definitions                                                                                                                             |
| Performance Optimization   | Significantly improves query efficiency by reducing redundant calculations through pre-stored results. Other SQL can utilize the materialized results for query rewriting | Although it can also improve query efficiency, the query optimizer will not rewrite the query | Performance depends on the query efficiency of the underlying data table, and the query logic is recalculated each time                                                                            |
| Data Timeliness            | Requires immediate data updates to ensure the accuracy of query rewriting                                                                                                 | Focuses on data processing flexibility, allowing for adjustable data latency                  | Data freshness is always the latest                                                                                                                                                                |
| Update Mechanism           | Uses a scheduled refresh mechanism to keep data up-to-date                                                                                                                | Adjusts according to business definitions, not mandatorily real-time updates                  | Does not store data, no need for updates                                                                                                                                                           |
| Query Optimization         | The optimizer automatically identifies and uses pre-stored results                                                                                                        | Does not rely on the query optimizer's automatic rewriting                                    |                                                                                                                                                                                                    |
| Use Cases                  | Suitable for scenarios where precomputed and reusable query results are needed                                                                                            | Suitable for data processing, where data may not be the latest                                | Suitable for scenarios with low query complexity and no extensive processing. If involving large data volumes and many complex operators, queries are slow because they are recalculated each time |
| Operations and Maintenance | No complex maintenance scenarios                                                                                                                                          | Dynamic tables also support complex column addition, version rollback, etc.                   | No complex maintenance scenarios                                                                                                                                                                   |

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

| Field Name       | Meaning                                                                                                                                 |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| workspace\_name  | Workspace name                                                                                                                          |
| schema\_name     | Schema name                                                                                                                             |
| name             | Dynamic table name                                                                                                                      |
| virtual\_cluster | Computing cluster used                                                                                                                  |
| start\_time      | Refresh start time                                                                                                                      |
| end\_time        | Refresh end time                                                                                                                        |
| duration         | Refresh duration                                                                                                                        |
| state            | Job status, setup\resuming cluster\queued\running\sucess\failed\success                                                                 |
| refresh\_trigger | MANUAL (manually triggered by user calling refresh, including studio scheduling refresh) LH\_SCHEDULED (scheduled refresh by lakehouse) |
| suspended\_reson | Reason for suspended scheduling                                                                                                         |
| refresh\_mode    | NO\_DATA FULL INCREMENTAl                                                                                                               |
| error\_message   | Information on refresh failure, if failed it will be here                                                                               |
| source\_tables   | Records the names of tables used by the dynamic table                                                                                   |
| stats            | Information on incremental refresh counts                                                                                               |
| job\_id          | Job ID, by clicking the job ID you can see the job profile                                                                              |

### View the refresh status of a single job through Job Profile

* In addition to SQL commands, you can also view the refresh details of a single job through Job Profile
  ![](.topwrite/assets/image_1740663208342.png)

* You can also determine whether data is read incrementally through the input records of the job profile
  ![](.topwrite/assets/image_1740662118892.png)

## Cost of Dynamic Tables

#### **Computing Cost**

The refresh operation of dynamic tables relies on computing resources (Virtual Cluster) to execute, including:

* **Scheduled Refresh**: Automatically executes refresh according to the set interval.
* **Manual Refresh**: Users manually trigger refresh as needed.

These refresh operations will consume computing resources.

#### **Storage Cost**

Dynamic tables also require storage space to save their materialized results. Like regular tables, dynamic tables support:

* **Time Travel**: Allows users to access data at any point in the past 7 days.
* **Time Travel Retention Period**: The default setting is 7 days. After this period, data will no longer be accessible through Time Travel and will be physically deleted.
  **Note**: Time Travel is currently in preview, with a default retention period of 7 days. During the preview period, users can query data versions within 7 days for free, and there will be no charges for versions within this period. After the preview period ends, Lakehouse will start charging separately for storage costs incurred by using the Time Travel feature.

#### **Refresh Scheduling Cycle**

**Factors Affecting Refresh Speed**

The speed of incremental refresh mainly depends on two factors:

1. **Amount of changes in source data**: The larger the amount of data that needs to be processed during the refresh operation, the longer it will take.
2. **Fixed overhead**: Some basic overhead is incurred with each refresh, regardless of the amount of data changes.

**Business Value and Refresh Frequency**

* If data freshness is not critical to your business value, consider reducing the refresh frequency. This strategy can reduce the computational overhead caused by frequent refreshes.
* Using an incremental computation model can increase the speed of a single refresh, as it only processes data that has changed since the last refresh.

**Balancing Refresh Costs and Frequency**

* Refresh costs will increase with the frequency of refreshes. Therefore, you need to balance the business value brought by data freshness with the computational costs incurred.
* Although high-frequency refresh operations can keep data updated in real-time, the accumulated computational costs will also increase.

**Recommendations**

* Evaluate your business needs to determine the specific value of data freshness to your business.
* Set a reasonable refresh frequency based on business value to optimize cost-effectiveness.
* Use an incremental computation model to improve refresh efficiency and reduce unnecessary computational overhead.

## Dynamic Table Limitations

* Incremental refresh limitations: Non-deterministic functions such as random, current\_timestamp, current\_date, etc., are not supported.
* Direct modification of dynamic table data is not supported, such as executing update, delete, truncate data.

## Use Cases for Processing with Dynamic Tables

Please refer to [Developing Monitoring Dynamic Tables with Studio](dynamic_table_using_studio.md).
