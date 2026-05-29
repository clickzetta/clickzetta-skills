# Data Transformation with Window Functions

Let's start by understanding the basic concepts and common use cases for data transformation using window functions in ETL/ELT (Extract, Transform, Load) workflows.

## Basic Concepts

[Window functions](window-function-summary.md) are a class of SQL functions designed to perform complex multi-row operations over a specified set of data (the "window"). Window functions preserve row-level detail while performing calculations within a defined data window.

[Basic syntax](window-frame.md):

```SQL
window_function() OVER (PARTITION BY column_name ORDER BY column_name)
```

* **OVER** defines the scope of the window.

* **PARTITION BY** defines how to divide the data into partitions. The window function is applied within each partition. If no partition is specified, the entire table is treated as a single partition.

* **Function** is the function applied to the current row. The result is added as an extra column in the output.

* **ORDER BY** defines the sort order within the window.

## Common Window Functions

1. [RANK()](sql_functions/window_functions/rank.md): A ranking function that assigns a rank to each row within a partition.
2. [DENSE\_RANK()](sql_functions/window_functions/dense_rank.md): Similar to RANK(), but does not skip rank values.
3. [ROW\_NUMBER()](sql_functions/window_functions/row_number.md): Assigns a unique sequential number to each row within a partition.
4. [SUM()](sql_functions/window_functions/sum.md): Computes a running sum.
5. [AVG()](sql_functions/window_functions/avg.md): Computes an average.
6. [LAG()](sql_functions/window_functions/lag.md): Accesses data from a preceding row.
7. [LEAD()](sql_functions/window_functions/lead.md): Accesses data from a following row.

## Use Cases

### 1. Deduplication and Flagging

Window functions are commonly used for deduplication — identifying and flagging duplicate rows.

**Prerequisite**: The table must have a **unique identifier** (such as an auto-increment ID, UUID, or business primary key) to precisely target rows for deletion.

For example, you can use a window function to number rows within each group and delete all duplicates beyond the first.

```SQL
DELETE FROM table_name 
WHERE id IN (
    SELECT id FROM (
        SELECT 
            id,  -- unique identifier
            ROW_NUMBER() OVER (
                PARTITION BY column_field      -- field used to detect duplicates
                ORDER BY identifier_field      -- determines which row to keep
            ) AS rn
        FROM table_name
    ) WHERE rn > 1
);
```

Or use MERGE INTO for more complex matching logic:

```SQL
MERGE INTO table_name t
USING (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY column_field ORDER BY identifier_field) AS rn
        FROM table_name
    ) WHERE rn > 1
) s
ON t.id = s.id
WHEN MATCHED THEN DELETE;
```

> ⚠️ **Note**: Window functions cannot be used directly in a DELETE WHERE clause. The following will produce an error:

```SQL
-- ❌ Incorrect usage
DELETE FROM table_name
WHERE ROW_NUMBER() OVER (PARTITION BY column_field ORDER BY identifier_field) > 1;
```

### 2. Partitioned Aggregation

Window functions can perform aggregations within partitions, such as running totals and moving averages.

```SQL
SELECT 
    product_id, 
    order_date, 
    SUM(order_amount) OVER (PARTITION BY product_id ORDER BY order_date) cumulative_sales 
FROM orders;
```

### 3. Sorting and Ranking

Window functions let you rank data and use those rankings in downstream calculations.

```SQL
SELECT 
    customer_id, 
    purchase_amount, 
    RANK() OVER (PARTITION BY region ORDER BY purchase_amount DESC) purchase_rank 
FROM purchases;
```

### 4. Data Backfill with Lag/Lead Columns

Use `LAG()` and `LEAD()` to access values from preceding or following rows, which is useful for filling in missing data.

```SQL
SELECT 
    customer_id,
    order_date,
    order_amount,
    LAG(order_amount) OVER (PARTITION BY customer_id ORDER BY order_date) previous_order_amount 
FROM orders;
```

Using window functions for ETL data transformation effectively improves the flexibility and efficiency of data processing, making complex analytical and transformation operations faster and more concise.

## Data Model

The TPC-H dataset represents a data warehouse for an auto parts supplier, containing records for orders, line items, suppliers, customers, parts, regions, nations, and part suppliers (partsupp).

Singdata Lakehouse includes built-in shared TPC-H data that any user can query directly by specifying the data context, for example:

```SQL
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```

## Data Transformation with Singdata Lakehouse SQL Window Functions

### Window Functions Have Four Core Components

1. **Partition**: Defines a group of rows based on the values of specified columns. If no partition is specified, the entire table is treated as a single partition.
2. **ORDER BY**: This optional clause specifies how rows are sorted within the partition.
3. **Function**: The function applied to the current row. The result is added as an extra column in the output.
4. **Window Frame**: Within a partition, the window frame lets you specify which rows are included in the function's calculation.

```SQL
SELECT
  o_custkey,
  o_orderdate,
  o_totalprice,
  SUM(o_totalprice) -- function 
  OVER (
    PARTITION BY
      o_custkey -- partition
    ORDER BY
      o_orderdate -- Order By; ascending unless DESC is specified
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

The `SUM` function in the query above is an aggregate function. Notice how `running_sum` accumulates (aggregates) `o_totalprice` across all rows. The rows themselves are sorted in ascending order by order date.

**Reference**: The standard aggregate functions are `MIN, MAX, AVG, SUM, & COUNT`. Modern data systems provide a variety of powerful aggregate functions. Consult your database documentation for available options. [Read this article](agg_function.md) for a list of aggregate functions available in Lakehouse.

## Using Ranking Functions to Get the Top/Bottom N Rows

If you need to retrieve the top or bottom N rows (defined by some value), use **row** functions.

Here is an example of how to use a row function:

**Get the top 3 highest-spending customers per day** from the `orders` table. The schema of the `orders` table is shown below:

```SQL
SELECT
  *
FROM
  (
    SELECT
      o_orderdate,
      o_totalprice,
      o_custkey,
      RANK() -- ranking function 
      OVER (
        PARTITION BY
          o_orderdate -- partition by order date
        ORDER BY
          o_totalprice DESC -- sort rows within partition by total price descending
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

1. `RANK()`: Ranks rows from 1 to n within the window frame. Rows with the same value (as defined by the ORDER BY clause) receive the same rank, and rank numbers that would otherwise exist are skipped.
2. `DENSE_RANK()`: Ranks rows from 1 to n within the window frame. Rows with the same value receive the same rank, and no rank numbers are skipped.
3. `ROW_NUMBER()`: Assigns row numbers from 1 to n within the window frame, with no duplicate values.

```SQL
-- An example showing the difference between RANK, DENSE_RANK, and ROW_NUMBER
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

Now you have seen how to **use window functions** along with **ranking and aggregate** functions.

## Why Define a Window Frame When You Already Have a Partition?

While functions operate on rows within a partition, the window frame provides a more granular way to operate on a selected subset of rows within that partition.

When you need to operate on a subset of rows within a partition (for example, a sliding window), you can use the window frame to define those rows.

Consider a scenario where you have sales data and want to calculate a 3-day moving average of sales for each store:

```SQL
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

1. **PARTITION BY** store\_id ensures the calculation is performed separately for each store.
2. **ORDER BY** sale\_date defines the order of rows within each partition.
3. **ROWS BETWEEN 2 PRECEDING AND CURRENT ROW** specifies the window frame, considering the current row and the two preceding rows to compute the moving average.

Without a defined window frame, the function may not produce the specific moving average calculation you need.

## Defining a Window Frame with ROWS

**ROWS**: Used to select a set of rows relative to the current row based on position.

1. Row definition format: `ROWS BETWEEN start_point AND end_point`.

   2. start\_point and end\_point can be any of the following (in the correct order):

      1. **n PRECEDING**: n rows before the current row. UNBOUNDED PRECEDING means all rows before the current row.
      2. **n FOLLOWING**: n rows after the current row. UNBOUNDED FOLLOWING means all rows after the current row.

Here is how to use relative row numbers to define a window range.

Consider this window function:

```SQL
AVG(total_price) OVER ( -- function: running average
    PARTITION BY o_custkey -- partition by customer
    ORDER BY order_month 
    ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING -- window frame: 1 row before to 1 row after
    )
```

Write a SQL query to retrieve the following output from the orders table:

1. 1. o\_custkey
   2. order\_month: formatted as YYYY-MM, using `date_format(o_orderdate, 'yyyy-MM') AS order_month`
   3. total\_price: the sum of o\_totalprice for that month
   4. three\_mo\_total\_price\_avg: the average total\_price across the previous, current, and next month for that customer

```SQL
SELECT
  order_month,
  o_custkey,
  total_price,
  ROUND(
    AVG(total_price) OVER ( -- function: running average
      PARTITION BY
        o_custkey -- partition by customer
      ORDER BY
        order_month ROWS BETWEEN 1 PRECEDING
        AND 1 FOLLOWING -- window frame: 1 row before to 1 row after
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

## Defining a Window Frame with RANGE

1. **RANGE**: Used to select a set of rows relative to the current row based on the value of the column specified in the `ORDER BY` clause.

   1. Range definition format: `RANGE BETWEEN start_point AND end_point`.

   2. start\_point and end\_point can be any of the following:

      1. **CURRENT ROW**: The current row.
      2. **n PRECEDING**: All rows whose values fall within n units before the current row's value.
      3. **n FOLLOWING**: All rows whose values fall within n units after the current row's value.
      4. **UNBOUNDED PRECEDING**: All rows before the current row in the partition.
      5. **UNBOUNDED FOLLOWING**: All rows after the current row in the partition.

   3. `RANGE` is particularly useful when working with numeric or date/time ranges, enabling calculations such as running totals, moving averages, or cumulative distributions.

Let's see how `RANGE` works with `AVG(total price) OVER (PARTITION BY customer id ORDER BY date RANGE BETWEEN INTERVAL '1' DAY PRECEDING AND '1' DAY FOLLOWING)`.

Now that you have seen how to create a window frame with ROWS, let's explore how to do the same with RANGE.

1. Write a query to retrieve the following output from the orders table:

   1. order\_month,
   2. o\_custkey,
   3. total\_price,
   4. three\_mo\_total\_price\_avg
   5. **consecutive\_three\_mo\_total\_price\_avg**: The average total\_price over 3 consecutive months for that customer. Note that this should only include months that are consecutive in time.

```SQL
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
      date_format (o_orderdate, 'yyyy-MM-01') AS order_month,
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

## Summary

1. Use window functions when you need to:

   * Compute running metrics (similar to `GROUP BY`, but preserving all rows)
   * Rank rows based on a specific column
   * Access values from other rows relative to the current row

2. A window has four key components: Partition, Order By, Function, Window Frame

3. Use ROWS or RANGE to define the window frame

4. Window functions are computationally expensive; be mindful of performance

## References

[Window Functions](window-function-summary.md)

[Window Function List](WINDOWFUNCTION.md)
