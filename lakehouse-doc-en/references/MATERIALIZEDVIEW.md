# MATERIALIZED VIEW

A materialized view is a special database object that can periodically cache query results to improve performance and efficiency. Since the data in a materialized view is precomputed, querying the materialized view is usually faster than directly querying the base table. This performance difference can be very significant when queries are frequently run or sufficiently complex. Therefore, materialized views can accelerate expensive aggregation, projection, and selection operations, especially those that are frequently run and operate on large datasets.

## Materialized View

* Materialized views can improve the performance of queries that repeatedly use the same subquery results. Query rewriting is possible.
* When the table corresponding to the data in the materialized view undergoes insert, overwrite, update, or delete operations, the materialized view will automatically become invalid and cannot be used for query rewriting.

## When to Create a Materialized View

Materialized views are particularly suitable for the following situations:

* The query results contain fewer rows and/or columns compared to the base table.
* The query results require extensive processing, including semi-structured data analysis, long-running aggregations, etc.
* The base table of the materialized view does not change frequently.

## Singdata Lakehouse Materialized View Features

* Materialized views can improve the performance of queries that repeatedly use the same subquery results.
* Materialized views support scheduled refresh functionality. This can be created through SQL syntax, which is more efficient and less error-prone compared to manually maintaining materialized views at the application level.

## Choosing Between Materialized Views and Regular Views

Generally, when deciding whether to create a materialized view or a regular view, the following criteria can be used:

* If the query results of the view do not change frequently, are used frequently, and the query consumes a lot of resources, create a materialized view.
* If the query results of the view change frequently, are not used frequently, or the query does not consume too many resources, create a regular view.

## Comparison of Materialized Views with Tables, Regular Views, and Cached Results

Materialized views are similar to tables in some ways and similar to regular (non-materialized) views in other ways. Additionally, materialized views have some similarities with cached results, particularly in that both allow storing query results for future reuse.

## Materialized View Management

Singdata Lakehouse provides the following DDL commands to create and maintain materialized views:
* [Create Materialized View](create-materialized-view.md): Creating a materialized view requires specifying the base table, query statement, and other related parameters. Once created successfully, the materialized view will be stored in the database for subsequent queries.
* [Drop Materialized View](drop-materialized-view.md): When a materialized view is no longer needed, it can be dropped to release related resources.
* [Refresh Materialized View](refresh-materialized-view.md): When the data in a materialized view needs to be updated, the refresh operation can be executed to update the data in the materialized view.

For more operations, please refer to [Materialized View Command Details](<materialized_ddl.md>).

## Application Scenarios

The following use cases highlight the value of materialized views. If your application scenarios meet the following conditions, materialized views can improve query performance:

* **Pre-aggregated Data**: If you need to perform aggregation analysis on a large amount of data, materialized views can use scheduled tasks to pre-aggregate, thereby improving query performance.
* **Pre-filtered Data**: If your query only needs to read specific parts of a table, materialized views can pre-filter the data, thereby reducing the amount of data during the query.
* **Pre-joined Data**: If your query needs to join multiple tables, especially joins between large and small tables, materialized views can pre-join the data, thereby improving query performance.

## Differences Between Materialized Views and Dynamic Tables

From the implementation mechanism of Lakehouse, dynamic tables are evolved from traditional materialized views. Although they have some commonalities, there are significant differences in their positioning.

**Materialized View: A Tool for Performance Optimization** Materialized views are special views that precompute and store query results, significantly improving query efficiency. Unlike traditional views, materialized views store the computed results in a table-like structure, allowing subsequent similar queries to be automatically recognized and directly use the pre-stored results, reducing redundant computations and speeding up queries.

**Dynamic Table: An Efficient Tool for Data Processing** Dynamic tables focus on data processing. Although they can also improve query performance, they do not rely on the query optimizer's automatic rewriting. Materialized views can only be rewritten if the data is up-to-date, while dynamic tables may not have the latest data in processing scenarios.

**Traditional materialized views in some products have the following limitations, which Lakehouse currently does not have**:

1. Only a single base table can be used. Materialized views cannot be based on complex queries (i.e., queries with joins or nested views).

2. Materialized views are not necessarily incrementally refreshed. Each system implements this differently. A few systems implement incremental computation for some operators to save computing resources and speed up processing.

**Advanced Features of Dynamic Tables**:

1. **Incremental Identification and Optimization**: Supports file-level incremental identification in big data environments, achieving real-time incremental reading and computation optimization, as well as write optimization.
2. **Intelligent Decision Making**: Uses a cost-based optimizer to intelligently choose between full, incremental, or partial incremental computation to meet different query needs.
3. **Real-time Task Operations and Maintenance**: Provides mechanisms for data version management, rollback, and rerun, offering comprehensive support for real-time task operations and maintenance.

**Data Timeliness Considerations**:

* Materialized views require immediate data updates to ensure the accuracy of query rewriting. When the base table data changes, Lakehouse uses a scheduled refresh mechanism to ensure that the data in the materialized view is always up-to-date.
* Dynamic tables focus more on the flexibility of data processing, adjusting data latency according to business definitions, without the strict requirement for real-time data updates.
## Query Rewrite Functionality

Currently, the query rewrite functionality of Lakehouse is in the Preview stage. If you need to enable it, please use the following configuration when submitting SQL queries:
`set cz.optimizer.enable.mv.rewrite=true;`

Specific Cases
```SQL

create table product_sales(sale_id int, product_name string, sale_date string, quantity_sold int);
INSERT INTO product_sales (sale_id, product_name, sale_date, quantity_sold)
VALUES
(1, 'Widget', '2024-05-01', 10),
(2, 'Widget', '2024-05-02', 20),
(3, 'Gadget', '2024-05-01', 15),
(4, 'Widget', '2024-05-03', 5);
CREATE MATERIALIZED VIEW product_sales_filter AS
SELECT    sale_id,
          product_name,
          sale_date
FROM      product_sales
WHERE     sale_id < 3;

set cz.optimizer.enable.mv.rewrite=true;
SELECT    sale_id,
          product_name,
          sale_date
FROM      product_sales
WHERE     sale_id < 2;

set cz.optimizer.enable.mv.rewrite=true;
SELECT    sale_id,
          product_name
FROM      product_sales
WHERE     sale_id < 2;
```

^
