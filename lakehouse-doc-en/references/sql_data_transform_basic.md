# SQL Data Transformation Basics

SQL data transformation is the process of converting data from one format or structure to another. The goal is to clean, integrate, and shape data so it can be effectively stored, analyzed, and utilized.

## Basic Concepts

1. **Extract**: Pulling data from various data sources such as databases and file systems. Common operations include data querying and data export.
2. **Transform**: Performing various operations on the extracted data to meet the requirements of the target storage or analysis system. Common transformation operations include data cleansing, type conversion, and data aggregation.
3. **Load**: Loading the transformed data into the target storage system, such as a data warehouse or data lake.

## Common Data Transformation Operations

1. **Data cleansing**: Removing or correcting noise, duplicates, and errors in the data. For example:
   * Delete null values: `DELETE FROM table_name WHERE column_name IS NULL;`
   * Correct erroneous data: `UPDATE table_name SET column_name = 'Correct Value' WHERE column_name = 'Incorrect Value';`

2. **Type conversion**: Converting data from one data type to another. For example:
   * Convert a string to a date: `CAST(column_name AS DATE);`
   * Convert an integer to a string: `CAST(column_name AS STRING);`

3. **Data aggregation**: Summarizing and computing statistics on data, such as sum, average, and count. For example:
   * Calculate the sum: `SELECT SUM(column_name) FROM table_name;`
   * Calculate the average: `SELECT AVG(column_name) FROM table_name;`

4. **Data merging**: Combining data from different tables or data sources. For example:
   * Merge data using a join: `SELECT a.*, b.* FROM table_a a JOIN table_b b ON a.id = b.id;`
   * Merge data using a union: `SELECT column_name FROM table_a UNION SELECT column_name FROM table_b;`

5. **Data filtering**: Selecting data that meets certain conditions. For example:
   * Retrieve data matching a specific condition: `SELECT * FROM table_name WHERE column_name = 'value';`

## Data Model

TPC-H data represents the data warehouse of an automotive parts supplier, recording orders, items that make up the orders (lineitem), suppliers, customers, parts sold (part), regions, countries, and parts suppliers (partsupp).

Singdata Lakehouse has built-in shared TPC-H data that every user can query directly by adding the data context, for example:

```SQL
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```

## Use Cases

1. **Data warehouse construction**: When building a data warehouse, you need to extract, transform, and load data from different sources into the warehouse to ensure consistency and high quality.
2. **Business intelligence and data analysis**: For BI and data analysis, raw data needs to be transformed so that analysis tools can efficiently parse and display it.
3. **Data migration**: During data migration, data needs to be transformed to ensure structural and quality consistency between the old and new systems.
4. **Compliance and data governance**: Ensuring data meets industry standards and regulatory requirements often requires data cleansing and transformation.
5. **Real-time data processing**: In real-time and stream data processing, data needs to be transformed to support real-time analysis and decision-making.

SQL data transformation is a core aspect of data processing that helps organizations improve data quality and utilization efficiency, supporting better decision-making and business operations.

## Basic Data Transformation with Singdata Lakehouse SQL

### Retrieving Data

Use SELECT...FROM, LIMIT, WHERE, and ORDER BY to read the required data from a table.

The most common use of queries is to read data from a table. You can use the `SELECT ... FROM` statement as shown below.

```SQL
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
LIMIT
  1;
```

^

```SQL
-- Use * to specify all columns
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.orders
LIMIT
  5;
```

However, running `SELECT ... FROM` without a limit can be problematic when the dataset is large.

```SQL
-- Only use column names to read data for those specific columns
SELECT
  o_orderkey,
  o_totalprice
FROM
  clickzetta_sample_data.tpch_100g.orders
LIMIT
  5;
```

To retrieve rows that meet specific conditions, use the `WHERE` clause. You can specify one or more filter conditions in the `WHERE` clause.

The `WHERE` clause can combine multiple filter conditions using `AND` and `OR`, as shown below.

```SQL
-- All customer rows with c_nationkey = 20
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_nationkey = 20
LIMIT
  10;
```

^

```SQL
-- All customer rows where c_nationkey = 20 and c_acctbal > 1000
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_nationkey = 20
  AND c_acctbal > 1000
LIMIT
  10;
```

```SQL
-- All customer rows where c_nationkey = 20 or c_acctbal > 1000
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_nationkey = 20
  OR c_acctbal > 1000
LIMIT
  10;
```

```SQL
-- All customer rows where (c_nationkey = 20 and c_acctbal > 1000) or c_nationkey = 11
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  (
    c_nationkey = 20
    AND c_acctbal > 1000
  )
  OR c_nationkey = 11
LIMIT
  10;
```

You can combine multiple filter conditions as shown above. The equal (`=`) and greater than (`>`) conditional operators have already been demonstrated. There are 6 **conditional operators** in total:

1. < Less than
2. \> Greater than
3. <= Less than or equal to
4. \>= Greater than or equal to
5. \= Equal to
6. <> and != both mean not equal to (some databases only support one of them)

For string types, you can use the `LIKE` condition for **pattern matching**. In a `LIKE` condition, `_` represents any single character and `%` represents zero or more characters, for example:

```SQL
-- All customer rows where c_name contains 381
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_name LIKE '%381%';
```

^

```SQL
-- All customer rows where c_name contains any character followed by 9 and 1
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_name LIKE '%_91%';
```

You can also use `IN` and `NOT IN` to filter multiple values.

^

```SQL
-- All customer rows with c_nationkey = 10 or c_nationkey = 20
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_nationkey IN (10, 20);
```

Use `count(*)` to get the number of rows in a table, as shown below.

^

```SQL
SELECT
  COUNT(*)
FROM
  clickzetta_sample_data.tpch_100g.lineitem;
```

^

```SQL
SELECT  COUNT(*)FROM  clickzetta_sample_data.tpch_100g.lineitem;
```

To sort rows by the values of a specific column, use `ORDER BY`, for example:

^

```SQL
-- Display the first ten customer records with the smallest custkey
-- Rows are sorted in ascending order by default
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.orders
ORDER BY
  o_custkey
LIMIT
  10;
```

### Join

Use JOINs to combine data from multiple tables (there are different types of JOINs).

You can use joins to combine data from multiple tables. The format for writing a join query is as follows.

^

```SQL
-- Based on non-real tables
SELECT
    a.*
FROM
    table_a a -- Left table a
    JOIN table_b b -- Right table b
    ON a.id = b.id
```

The first table specified (table\_a) is the left table, and the second is the right table. When joining multiple tables, the joined dataset of the first two tables is treated as the left table and the third table as the right table (the database optimizes the join order for performance).

^

```SQL
-- Based on non-real tables
SELECT
    a.*
FROM
    table_a a -- Left table a
    JOIN table_b b -- Right table b
    ON a.id = b.id
    JOIN table_c c -- Left table is the joined data of table_a and table_b; right table is table_c
    ON a.c_id = c.id
```

There are five main join types:

#### 1. Inner Join (default): Only returns rows that exist in both tables

^

```SQL
SELECT
  o.o_orderkey,
  l.l_orderkey
FROM
  clickzetta_sample_data.tpch_100g.orders o
  JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY
LIMIT
  100;
```

^

```SQL
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```

**Note**: The join defaults to an inner join.

The output includes records where at least one matching row is found in both orders and line items (same o\_orderkey and order date within 5 days before or after the ship date).

You can also see that there are 24,792,743 matching rows across the orders and line items tables.

#### 2. Left Outer Join (also known as Left Join): Returns all rows from the left table and matching rows from the right table

```SQL
SELECT
  o.o_orderkey,
  l.l_orderkey
FROM
  clickzetta_sample_data.tpch_100g.orders o
  LEFT JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY
LIMIT
  100;
```

^

```SQL
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  LEFT JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```

The output includes all rows from the orders table and records from the line items table that have at least one matching row (same o\_orderkey and order date within 5 days before or after the ship date).

You can also see that the orders table has 151,947,677 rows and the line items table has 24,792,743 rows. The orders table has 1,500,000 rows, but the join condition produces 151,947,677 rows because some orders match multiple line items.

#### 3. Right Outer Join (also known as Right Join): Returns matching rows from the left table and all rows from the right table

```SQL
SELECT
  o.o_orderkey,
  l.l_orderkey
FROM
  clickzetta_sample_data.tpch_100g.orders o
  RIGHT JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY
LIMIT
  100;
```

^

```SQL
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  RIGHT JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```

The output includes records from the orders table where at least one matching row is found (same o\_orderkey and order date within 5 days before or after the ship date) and all rows from the line items table.

You can also see that the orders table has 24,792,743 rows and the line items table has 600,037,902 rows.

#### 4. Full Outer Join: Returns all rows from both the left and right tables

```SQL
SELECT
  o.o_orderkey,
  l.l_orderkey
FROM
  clickzetta_sample_data.tpch_100g.orders o
  FULL OUTER JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY
LIMIT
  100;
```

^

```SQL
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  FULL OUTER JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```

The output includes records from the orders table where at least one matching row is found (same o\_orderkey and order date within 5 days before or after the ship date) and all rows from the line items table.

You can also see that the orders table has 151,947,677 rows and the line items table has 600,037,902 rows.

#### 5. Cross Join: Returns the Cartesian product of all rows

```SQL
SELECT
  n.n_name AS nation_c_name,
  r.r_name AS region_c_name
FROM
  clickzetta_sample_data.tpch_100g.nation n
  CROSS JOIN clickzetta_sample_data.tpch_100g.region r;
```

The output includes every row from the nation table joined with every row from the region table. There are 25 nations and 5 regions, so the cross join produces 125 rows.

^

Sometimes you need to join a table with itself, which is called a self-join.

**Example**:

1. For each customer order, get the orders placed earlier in the same week (Sunday through Saturday, not the previous seven days). Only show customer orders that have at least one such earlier order.

```SQL
SELECT
  o1.o_custkey
FROM
  clickzetta_sample_data.tpch_100g.orders o1
  JOIN clickzetta_sample_data.tpch_100g.orders o2 ON o1.o_custkey = o2.o_custkey
  AND YEAR (o1.o_orderdate) = YEAR (o2.o_orderdate)
  AND week (o1.o_orderdate) = week (o2.o_orderdate)
WHERE
  o1.o_orderkey != o2.o_orderkey;
```

Most analytical queries require computing metrics that involve multiple rows. `GROUP BY` lets you perform aggregate calculations on sets of rows grouped by specified column values.

**Example**:

1. Create a report showing the number of orders for each order priority segment.

```SQL
SELECT
  o_orderpriority,
  COUNT(*) AS num_orders
FROM
  clickzetta_sample_data.tpch_100g.orders
GROUP BY
  o_orderpriority;
```

In the above query, rows are grouped by `orderpriority` and `count(*)` is applied to each group. The output contains one row per unique `orderpriority` value along with the `count(*)` result.

^

Allowed aggregate functions are typically SUM/MIN/MAX/AVG/COUNT. Some databases offer more complex aggregate functions; refer to your database documentation for details.

### Subqueries

Use subqueries to use the result of one query inside another query.

When you want to use the result of one query as a table in another query, use a subquery. **Example**:

1. Create a report showing each country, the number of items supplied by suppliers from that country, and the number of items purchased by customers from that country.

```SQL
SELECT
  n.n_name AS nation_c_name,
  s.quantity AS supplied_items_quantity,
  c.quantity AS purchased_items_quantity
FROM
  clickzetta_sample_data.tpch_100g.nation n
  LEFT JOIN (
    SELECT
      n.n_nationkey,
      SUM(l.l_quantity) AS quantity
    FROM
      clickzetta_sample_data.tpch_100g.lineitem l
      JOIN clickzetta_sample_data.tpch_100g.supplier s ON l.l_suppkey = s.s_suppkey
      JOIN clickzetta_sample_data.tpch_100g.nation n ON s.s_nationkey = n.n_nationkey
    GROUP BY
      n.n_nationkey
  ) s ON n.n_nationkey = s.n_nationkey
  LEFT JOIN (
    SELECT
      n.n_nationkey,
      SUM(l.l_quantity) AS quantity
    FROM
      clickzetta_sample_data.tpch_100g.lineitem l
      JOIN clickzetta_sample_data.tpch_100g.orders o ON l.l_orderkey = o.o_orderkey
      JOIN clickzetta_sample_data.tpch_100g.customer c ON o.o_custkey = c.c_custkey
      JOIN clickzetta_sample_data.tpch_100g.nation n ON c.c_nationkey = n.n_nationkey
    GROUP BY
      n.n_nationkey
  ) c ON n.n_nationkey = c.n_nationkey;
```

In the above query, there are two subqueries: one calculates the number of items supplied by each country's suppliers, and the other calculates the number of items purchased by each country's customers.

### CASE WHEN&#x20;

Use the CASE statement to replicate IF/ELSE logic.

You can apply conditional logic in the `SELECT ... FROM` part of a query, as shown below.

```SQL
SELECT
    o_orderkey,
    o_totalprice,
    CASE
        WHEN o_totalprice > 100000 THEN 'high'
        WHEN o_totalprice BETWEEN 25000
        AND 100000 THEN 'medium'
        ELSE 'low'
    END AS order_price_bucket
FROM
    clickzetta_sample_data.tpch_100g.orders;
```

You can see how different values are displayed based on the `totalprice` column. You can also use multiple conditions as criteria (for example, totalprice > 100000 AND orderpriority = '2-HIGH').

### Standard Functions

Use standard built-in database functions for common string, time, and numeric data operations.

When processing data, you often need to modify column values. Here are some standard functions to know:

1. **String functions**

   1. **LENGTH** calculates the length of a string. For example, `SELECT LENGTH('hi');` outputs 2.
   2. **CONCAT** combines multiple string columns into one. For example, `SELECT CONCAT(o_orderstatus, '-', o_orderpriority) FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;` concatenates the o\_orderstatus and o\_orderpriority columns with a hyphen separator.
   3. **SPLIT** splits a value into an array based on a given delimiter. For example, `SELECT SPLIT(o_orderpriority, '-') FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;` outputs an array formed by splitting o\_orderpriority at `-`.
   4. **SUBSTRING** extracts a substring from a value given start and end character indices. For example, `SELECT o_orderpriority, SUBSTRING(o_orderpriority, 1, 5) FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;` returns the first five characters (positions 1–5) of o\_orderpriority.
   5. **TRIM** removes spaces from both sides of a value. For example, `SELECT TRIM(' hi ');` outputs `hi` without surrounding spaces. LTRIM and RTRIM are similar but only remove spaces from the beginning or end of the string, respectively.

2. **Date and time functions**

   1. **Adding and subtracting dates**: Used to add and subtract time periods; the exact format depends on the database. In Lakehouse, `datediff` takes 3 parameters — the output unit (day, month, year) and date/time values a and b — and returns a - b. `+ INTERVAL n UNIT(DAY/MONTH/YEAR)` adds the specified unit value to a timestamp.

      ```SQL
        -- Date and time functions
        SELECT
            datediff(day, DATE '2022-10-01', DATE '2023-11-05') AS diff_in_days,
            datediff(month, DATE '2022-10-01', DATE '2023-11-05') AS diff_in_months,
            datediff(year, DATE '2022-10-01', DATE '2023-11-05') AS diff_in_years,
            DATE '2022-10-01' + INTERVAL 400 DAY AS new_date;
      ```

   This displays the difference between two dates in the specified time unit. You can also add or subtract any time period from a date/time column. For example, `SELECT DATE '2022-11-05' + INTERVAL '10' DAY;` outputs `2022-11-15` (try date subtraction as well).

   ^

3. **String <=> Date/Time conversion**

When you want to change the data type of a string to date/time, use the `DATE 'YYYY-MM-DD'` or `TIMESTAMP 'YYYY-MM-DD HH:mm:SS'` functions. If the data is in a non-standard date/time format such as `MM/DD/YYYY`, you need to specify the input structure using `date_format`, for example:

```SQL
SELECT date_format('2023-05-11', 'M-d-y');
```

You can also use `date_format` to convert a timestamp/date into a string of the desired format. For example:

```SQL
SELECT date_format(o_orderdate, 'yyyy-MM-01') AS first_month_date FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;
```

See [this page](sql_functions/scalar_functions/datetime_functions/date_format.md) for how to set the correct date and time format.

4. **Time frame functions (YEAR/MONTH/DAY)**: When you want to extract a specific time component from a date/time column, use these functions. For example, `SELECT year(DATE '2023-11-05');` returns 2023. Similarly, there are functions for month, day, hour, minute, and more.

See [this page](time-function.md) for more time functions.

5. **Numeric functions**

   1. **ROUND** specifies the number of decimal places. For example, `SELECT ROUND(100.102345, 2);`
   2. **ABS** returns the absolute value of a number. For example, `SELECT ABS(-100), ABS(100);`
   3. **Mathematical operators** such as +, -, \*, /.
   4. **CEIL/FLOOR** returns the next higher or nearest lower integer for a given decimal. For example, `SELECT CEIL(100.1), FLOOR(100.1);`
