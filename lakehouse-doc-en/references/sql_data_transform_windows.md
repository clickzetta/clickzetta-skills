# Data Transformation Using Window Functions (Windows)

Let's first understand the basic concepts and common use cases of using window functions for data transformation in the ETL/ELT (Extract, Transform, Load) process.

## Basic Concepts

[Window functions](window-function-summary.md) are a type of function in SQL specifically used to perform complex multi-row operations within a specified data set (i.e., "window"). Window functions can retain row-level details while performing calculations within a specific data window.

[Basic syntax](windowframe.md):
```sql
Window function() OVER (PARTITION BY column_name ORDER BY column_name)
```
* **OVER** keyword defines the scope of the window.

* **PARTITION BY** defines how to partition the data, applying the window function within each partition. If no partition is specified, the entire table is considered as one partition.

* **Function** applied to the current row. The function result adds an extra column in the output.

* **ORDER BY** defines the sorting within the window.

## Common Window Functions

1. [RANK()](sql_functions/window_functions/rank.md): Ranking function, assigns a rank to each row within each partition.
2. [DENSE\_RANK()](sql_functions/window_functions/dense_rank.md): Similar to RANK(), but does not skip ranks.
3. [ROW\_NUMBER()](sql_functions/window_functions/row_number.md): Assigns a unique number to each row within each partition.
4. [SUM()](sql_functions/window_functions/sum.md): Cumulative sum.
5. [AVG()](sql_functions/window_functions/avg.md): Calculates the average.
6. [LAG()](sql_functions/window_functions/lag.md): Retrieves data from a previous row.
7. [LEAD()](sql_functions/window_functions/lead.md): Retrieves data from a subsequent row.

## Use Cases

### 1. Data Deduplication and Tagging

Window functions are often used for data deduplication and tagging duplicate rows. For example, we can use window functions to number each group and delete duplicate rows except the first one.
```sql
DELETE FROM table_name
WHERE ROW_NUMBER() OVER (PARTITION BY column_field ORDER BY identifier_field) > 1;
```
### 2. Data Partitioning and Aggregation

Window functions can be used to perform aggregation operations within partitions, such as cumulative sums and moving averages.
```sql
SELECT 
    product_id, 
    order_date, 
    SUM(order_amount) OVER (PARTITION BY product_id ORDER BY order_date) cumulative_sales 
FROM orders;
```
### 3. Data Sorting and Ranking

Through window functions, data can be sorted and ranked, and the results can be used for subsequent calculations.
```sql
SELECT 
    customer_id, 
    purchase_amount, 
    RANK() OVER (PARTITION BY region ORDER BY purchase_amount DESC) purchase_rank 
FROM purchases;
```
### 4. Data Completion and Lag/Lead Columns

Using the `LAG()` and `LEAD()` functions, you can obtain previous/next row data to complete missing data.
```sql
SELECT 
    customer_id,
    order_date,
    order_amount,
    LAG(order_amount) OVER (PARTITION BY customer_id ORDER BY order_date) previous_order_amount 
FROM orders;
```
Using window functions for ETL data transformation can effectively improve the flexibility and efficiency of data processing, making complex data analysis and transformation operations faster and simpler.

## Data Model

TPC-H data represents the data warehouse of an auto parts supplier, which records orders, items that make up the orders (lineitem), suppliers, customers, parts sold (part), regions, countries, and parts suppliers (partsupp).

Singdata Lakehouse has built-in shared TPC-H data, which each user can directly use by adding the data context, for example:
```sql
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```
## Data Transformation Using Singdata Lakehouse SQL Window Functions

### Window Functions Have Four Basic Parts

1. **Partition**: Defines a set of rows based on the values of specified columns. If no partition is specified, the entire table is considered as one partition.
2. **Order By**: This optional clause specifies how to sort the rows within a partition.
3. **Function**: The function applied to the current row. The function result adds an extra column in the output.
4. **Window Frame**: Within a partition, the window frame allows you to specify the rows to be considered in the function calculation.
```sql
SELECT
  o_custkey,
  o_orderdate,
  o_totalprice,
  SUM(o_totalprice) -- Function
  OVER (
    PARTITION BY
      o_custkey -- Partition
    ORDER BY
      o_orderdate -- Order By; ascending unless specified as DESC
  ) AS running_sum
FROM
  clickzetta_sample_data.tpch_100g.orders
WHERE
  o_custkey = 4
ORDER BY
  o_orderdate
LIMIT
  10;
```
The `SUM` function in the above query is an aggregate function. Notice how `running_sum` accumulates (i.e., aggregates) `o_totalprice` over all rows. The rows themselves are ordered in ascending order by their order date.

**Reference**: Standard aggregate functions are `MIN, MAX, AVG, SUM, & COUNT`. Modern data systems offer a variety of powerful aggregate functions. Please refer to your database documentation to learn about the available aggregate functions. Please [read this article](agg_function.md) for a list of aggregate functions available in Lakehouse.

## Using Ranking Functions to Get Top/Bottom n Rows

If you are dealing with a problem that requires getting the top/bottom n rows (defined by some value), then use **row** functions.

Let's look at an example of how to use row functions:

From the `orders` table, **get the top 3 customers with the highest spending each day**. The schema of the `orders` table is as follows:
```sql
SELECT
  *
FROM
  (
    SELECT
      o_orderdate,
      o_totalprice,
      o_custkey,
      RANK() -- Ranking function
      OVER (
        PARTITION BY
          o_orderdate -- Partition by order date
        ORDER BY
          o_totalprice DESC -- Order rows within the partition by total price in descending order
      ) AS rnk
    FROM
      clickzetta_sample_data.tpch_100g.orders
  )
WHERE
  rnk <= 3
ORDER BY
  o_orderdate
LIMIT
  5;
```
## Standard Ranking Functions

1. \`\`：Ranks rows within the window frame from 1 to n. Rows with the same value (as defined by the "ORDER BY" clause) receive the same rank, and the ranking numbers that would have been used if the values were different are skipped.
2. \`\`：Ranks rows within the window frame from 1 to n. Rows with the same value (as defined by the "ORDER BY" clause) receive the same rank, and no ranking numbers are skipped.
3. \`\`：Adds row numbers from 1 to n within the window frame, without creating any duplicate values.
```sql
-- Let's look at an example that shows the difference between RANK, DENSE_RANK, and ROW_NUMBER
SELECT 
    order_date,
    order_id,
    total_price,
    ROW_NUMBER() OVER (PARTITION BY order_date ORDER BY total_price) AS row_number,
    RANK() OVER (PARTITION BY order_date ORDER BY total_price) AS rank,
    DENSE_RANK() OVER (PARTITION BY order_date ORDER BY total_price) AS dense_rank
FROM (
    SELECT 
        '2024-07-08' AS order_date, 'order_1' AS order_id, 100 AS total_price UNION ALL
    SELECT 
        '2024-07-08', 'order_2', 200 UNION ALL
    SELECT 
        '2024-07-08', 'order_3', 150 UNION ALL
    SELECT 
        '2024-07-08', 'order_4', 90 UNION ALL
    SELECT 
        '2024-07-08', 'order_5', 100 UNION ALL
    SELECT 
        '2024-07-08', 'order_6', 90 UNION ALL
    SELECT 
        '2024-07-08', 'order_7', 100 UNION ALL
    SELECT 
        '2024-07-10', 'order_8', 100 UNION ALL
    SELECT 
        '2024-07-10', 'order_9', 100 UNION ALL
    SELECT 
        '2024-07-10', 'order_10', 100 UNION ALL
    SELECT 
        '2024-07-11', 'order_11', 100
) AS orders
ORDER BY order_date, row_number;
```
:-: ![](.topwrite/assets/image_1736841886300.png =818)

Now we have seen how to **use window functions** and how to use **ranking and aggregation** functions.

## Why define a window frame with partitions?

While our functions operate on rows within partitions, the window frame provides a more refined way to operate on a selected set of rows within a partition.

When we need to operate on a set of rows within a partition (e.g., sliding window), we can use the window frame to define these rows.

Consider a scenario where you have sales data and you want to calculate the 3-day moving average sales for each store:
```sql
SELECT
    store_id,
    sale_date,
    sales_amount,
    AVG(sales_amount) OVER (
        PARTITION BY store_id
        ORDER BY sale_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_sales
FROM
    sales;
```
In this example:

1. **PARTITION BY** store\_id ensures that the calculation is performed separately for each store.
2. **ORDER BY** sale\_date defines the order of rows within each partition.
3. **ROWS BETWEEN 2 PRECEDING AND CURRENT ROW** specifies the window frame, considering the current row and the two preceding rows to calculate the moving average.

If the window frame is not defined, the function may not provide the specific moving average calculation you need.

## Using ROWS to Define Window Frame

**ROWS**: Used to select a set of rows relative to the current row based on position.

1. The row definition format is `ROWS BETWEEN start_point AND end_point`.

   2. start\_point and end\_point can be any of the following three (in the correct order):

      1. **n PRECEDING**: The n rows before the current row. UNBOUNDED PRECEDING means all rows before the current row.
      2. **n FOLLOWING**: The n rows after the current row. UNBOUNDED FOLLOWING means all rows after the current row.

Let's see how to use relative row numbers to define the window range.

Consider this window function:
```sql
AVG(total_price) OVER ( -- Function: Running Average
    PARTITION BY o_custkey -- Partition by customer
    ORDER BY order_month 
    ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING -- Window frame defined as 1 row before to 1 row after
    )
```
Write an SQL query to get the following output from the orders table:

1. o\_custkey
   2. order\_month: Format as YYYY-MM, use strftime(o\_orderdate, '%Y-%m') AS order\_month
   3. total\_price: The sum of o\_totalprice for that month
   4. three\_mo\_total\_price\_avg: The average total\_price for the past, current, and next month for that customer
```sql
SELECT
  order_month,
  o_custkey,
  total_price,
  ROUND(
    AVG(total_price) OVER ( -- Function: Running Average
      PARTITION BY
        o_custkey -- Partition by customer
      ORDER BY
        order_month ROWS BETWEEN 1 PRECEDING
        AND 1 FOLLOWING -- Window frame defined as 1 row before to 1 row after
    ),
    2
  ) AS three_mo_total_price_avg
FROM
  (
    SELECT
      date_format (o_orderdate, 'yyyy-MM') AS order_month,
      o_custkey,
      SUM(o_totalprice) AS total_price
    FROM
      clickzetta_sample_data.tpch_100g.orders
    GROUP BY
      1,
      2
  )
LIMIT
  5;
```
## Using RANGE to Define Window Frames

1. **RANGE**: Used to select a set of rows related to the current row based on the values of the columns specified in the `ORDER BY` clause.

   1. Range definition format `RANGE BETWEEN start_point AND end_point`.

   2. start\_point and end\_point can be any of the following:

      1. **CURRENT ROW**: The current row.
      2. **n PRECEDING**: All rows within the specified range and n units before the current row value.
      3. **n FOLLOWING**: All rows within the specified range and n units after the current row value.
      4. **UNBOUNDED PRECEDING**: All rows before the current row in the partition.
      5. **UNBOUNDED FOLLOWING**: All rows after the current row in the partition.

   3. `RANGE` is particularly useful when dealing with numerical or date/time ranges, allowing calculations such as running totals, moving averages, or cumulative distributions.

Let's see how `RANGE` works with `AVG(total price) OVER (PARTITION BY customer id ORDER BY date RANGE BETWEEN INTERVAL '1' DAY PRECEDING AND '1' DAY FOLLOWING)`.

Now that we've seen how to create window frames using ROWS, let's explore how to do this using RANGE.

1. Write a query to get the following output from the orders table:

   1. order\_month,
   2. o\_custkey,
   3. total\_price,
   4. three\_mo\_total\_price\_avg
   5. **consecutive\_three\_mo\_total\_price\_avg**: The average total\_price for consecutive 3 months for the customer. Note that this should only include months arranged in chronological order.
```sql
SELECT
  order_month,
  o_custkey,
  total_price,
  ROUND(
    AVG(total_price) OVER (
      PARTITION BY
        o_custkey
      ORDER BY
        CAST(order_month AS DATE) RANGE BETWEEN INTERVAL '1' MONTH PRECEDING
        AND INTERVAL '1' MONTH FOLLOWING
    ),
    2
  ) AS consecutive_three_mo_total_price_avg,
  ROUND(
    AVG(total_price) OVER (
      PARTITION BY
        o_custkey
      ORDER BY
        order_month ROWS BETWEEN 1 PRECEDING
        AND 1 FOLLOWING
    ),
    2
  ) AS three_mo_total_price_avg
FROM
  (
    SELECT
      date_format (o_orderdate, 'yyyy-mm-01') AS order_month,
      o_custkey,
      SUM(o_totalprice) AS total_price
    FROM
      clickzetta_sample_data.tpch_100g.orders
    GROUP BY
      1,
      2
  )
ORDER BY
  o_custkey,
  order_month
LIMIT
  50;
```
:-: ![](.topwrite/assets/image_1736843103972.png =811)

## Review

1. When using window functions:

   * Calculate running metrics (similar to `GROUP BY`, but retains all rows)
   * Rank rows based on specific columns
   * Access values from other rows relative to the current row

2. Windows have four key parts: Partition, Order By, Function, Window Frame

3. Define window frames using ROWS or RANGE

4. Window functions are costly; be mindful of performance

## Resources

[Window Functions](window-function-summary.md)

[List of Window Functions](WINDOWFUNCTION.md)