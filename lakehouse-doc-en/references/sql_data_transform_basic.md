# Basic SQL Data Transformation

SQL data transformation is the process of converting data from one format or structure to another. The goal is to clean, integrate, and shape the data so that it can be effectively stored, analyzed, and utilized.

## Basic Concepts

1. **Extract**: Extracting data from various data sources (such as databases, file systems). Common operations include data querying and data exporting.
2. **Transform**: Performing various operations on the extracted data to meet the requirements of target storage or analysis. Common transformation operations include data cleaning, type conversion, data aggregation, etc.
3. **Load**: Loading the transformed data into the target storage system, such as a data warehouse or data lake.

## Common Data Transformation Operations

1. **Data Cleaning**: Removing or correcting noise, duplicates, and errors in the data. For example:
   * Deleting null values: `DELETE FROM table_name WHERE column_name IS NULL;`
   * Correcting erroneous data: `UPDATE table_name SET column_name = 'Correct Value' WHERE column_name = 'Incorrect Value';`

2. **Type Conversion**: Converting data from one data type to another. For example:
   * Converting a string to a date: `CAST(column_name AS DATE);`
   * Converting an integer to a string: `CAST(column_name AS VARCHAR);`

3. **Data Aggregation**: Summarizing and calculating statistics on the data, such as sum, average, count, etc. For example:
   * Calculating the sum: `SELECT SUM(column_name) FROM table_name;`
   * Calculating the average: `SELECT AVG(column_name) FROM table_name;`

4. **Data Merging**: Combining data from different tables or data sources. For example:
   * Merging data using a join operation: `SELECT a.*, b.* FROM table_a a JOIN table_b b ON a.id = b.id;`
   * Merging data using a union operation: `SELECT column_name FROM table_a UNION SELECT column_name FROM table_b;`

5. **Data Filtering**: Selecting data that meets certain conditions. For example:
   * Retrieving data that meets specific conditions: `SELECT * FROM table_name WHERE column_name = 'value';`

## Data Model

TPC-H data represents the data warehouse of an automotive parts supplier, recording orders, items that make up the orders (lineitem), suppliers, customers, parts sold (part), regions, countries, and parts suppliers (partsupp).

Singdata Lakehouse has built-in shared TPC-H data, which each user can directly use by adding the data context, for example:
```sql
SELECT * FROM 
clickzetta_sample_data.tpch_100g.customer
LIMIT 10;
```
## Use Cases

1. **Data Warehouse Construction**: When building a data warehouse, it is necessary to extract, transform, and load data from different data sources into the data warehouse to ensure data consistency and high quality.
2. **Business Intelligence and Data Analysis**: For business intelligence (BI) and data analysis, raw data needs to be transformed so that analysis tools can efficiently parse and display the data.
3. **Data Migration**: During data migration, data needs to be transformed to ensure consistency in data structure and quality from the old system to the new system.
4. **Compliance and Data Governance**: Ensuring data meets industry standards and regulatory requirements often requires data cleansing and transformation.
5. **Real-time Data Processing**: In real-time data processing and stream data processing, data needs to be transformed for real-time analysis and decision support.

SQL data transformation is a core aspect of data processing that can help enterprises improve data quality and utilization efficiency, thereby supporting better decision-making and business operations.

## Basic Data Transformation with Singdata Lakehouse SQL

### Retrieving Data

Use SELECT...FROM, LIMIT, WHERE, & ORDER BY to read the required data from the table.

The most common use of queries is to read data from a table. We can use the `SELECT ... FROM` statement as shown below.
```sql
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
LIMIT
  1;
```

^

```sql
-- Use * to specify all columns
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.orders
LIMIT
  5;
```
However, running the `SELECT ... FROM` statement may encounter issues when the dataset is large.
```sql
-- Only use column names to read the data of these columns
SELECT
  o_orderkey,
  o_totalprice
FROM
  clickzetta_sample_data.tpch_100g.orders
LIMIT
  5;
```
If we want to retrieve rows that meet specific conditions, we can use the `WHERE` clause. We can specify one or more filter conditions in the `WHERE` clause.

The `WHERE` clause can combine multiple filter conditions using `AND` and `OR` conditions, as shown below.
```sql
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

```sql
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
```sql
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
```sql
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
We can combine multiple filter conditions, as shown above. We have already seen the equal (`=`) and greater than (`>`) conditional operators. There are a total of 6 **conditional operators**, which are:

1. < Less than
2. \> Greater than
3. <= Less than or equal to
4. \>= Greater than or equal to
5. \= Equal to
6. <> and != both mean not equal to (some databases only support one of them)

Additionally, for string types, we can use the `like` condition for **pattern matching**. In the `like` condition, `_` represents any single character, and `%` represents zero or more characters, for example.
```sql
-- All customer rows where c_name contains 381
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_name LIKE '%381%';
```

^

```sql
-- All customer rows where c_name contains any character, 9, and 1
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_name LIKE '%_91%';
```
We can also use `IN` and `NOT IN` to filter multiple values.

^
```sql
-- All customer rows with c_nationkey = 10 or c_nationkey = 20
SELECT
  *
FROM
  clickzetta_sample_data.tpch_100g.customer
WHERE
  c_nationkey IN (10, 20);
```
You can use `count(*)` to get the number of rows in the table, as shown below.

^
```sql
SELECT
  COUNT(*)
FROM
  clickzetta_sample_data.tpch_100g.lineitem;
```

^

```sql
SELECT  COUNT(*)FROM  clickzetta_sample_data.tpch_100g.lineitem;
```
If we want to sort rows by the values of a specific column, we can use `ORDER BY`, for example.

^
```sql
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

We can use joins to combine data from multiple tables. When writing join queries, the format is as follows.

^
```sql
-- Based on non-real table
SELECT
    a.*
FROM
    table_a a -- Left table a
    JOIN table_b b -- Right table b
    ON a.id = b.id
```
First, the specified table (table\_a) is the left table, and the second specified table is the right table. When multiple tables are joined, we treat the joined dataset of the first two tables as the left table and the third table as the right table (the database will optimize the join to improve performance).

^
```sql
-- Based on non-real table
SELECT
    a.*
FROM
    table_a a -- Left table a
    JOIN table_b b -- Right table b
    ON a.id = b.id
    JOIN table_c c -- The left table is the join data of table_a and table_b, the right table is table_c
    ON a.c_id = c.id
```
There are mainly five types of connections, which are:

#### 1. Inner Join (default): Only get the rows that exist in both tables

^
```sql
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

```sql
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```
**Note**: The connection defaults to an inner join.

The output will include records where at least one matching row is found in the orders and line items (same o\_orderkey and order date within 5 days before or after the ship date).

We can also see that there are 24,792,743 matching rows in the orders and line items tables.

#### 2. Left Outer Join (also known as Left Join): Get all rows from the left table and matching rows from the right table
```sql
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

```sql
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  LEFT JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```
The output will include all rows from the orders table and records from the line items table that have at least one matching row (same o_orderkey and the order date is within 5 days before or after the ship date).

We can also see that the orders table has 151,947,677 rows, and the line items table has 24,792,743 rows. The number of rows in the orders table is 1,500,000, but due to the join condition, 151,947,677 rows are generated because some orders match multiple line items.

#### 3. Right Outer Join (also known as Right Join): Get matching rows from the left table and all rows from the right table
```sql
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

```sql
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  RIGHT JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```
The output will include records from the orders table where at least one matching row is found (same o\_orderkey and the order date is within 5 days before or after the ship date) and all rows from the lineitem table.

We can also see that the orders table has 24,792,743 rows, and the lineitem table has 600,037,902 rows.

#### 4. Full Outer Join: Get all rows from the left and right tables
```sql
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

```sql
SELECT
  COUNT(o.o_orderkey) AS order_rows_count,
  COUNT(l.l_orderkey) AS lineitem_rows_count
FROM
  clickzetta_sample_data.tpch_100g.orders o
  FULL OUTER JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
  AND o.o_orderdate BETWEEN l.l_shipdate - INTERVAL '5' DAY AND l.l_shipdate  + INTERVAL '5' DAY;
```
The output will include records from the orders table where at least one matching row is found (same o\_orderkey and order date within 5 days before or after the ship date) and all rows from the lineitem table.

We can also see that the orders table has 151,947,677 rows, and the lineitem table has 600,037,902 rows.

#### 5. Cross Join: Get the Cartesian Product of All Rows
```sql
SELECT
  n.n_name AS nation_c_name,
  r.r_name AS region_c_name
FROM
  clickzetta_sample_data.tpch_100g.nation n
  CROSS JOIN clickzetta_sample_data.tpch_100g.region r;
```
The output will include the join of each row of the country table with each row of the region table. There are 25 countries and 5 regions, so the result of the cross join has 125 rows.

^

Sometimes we need to join a table with itself, which is called a self-join.

**Example**:

1. For each customer order, get the orders placed earlier in the same week (Sunday - Saturday, not the previous seven days). Only show customer orders that have at least one such order.
```sql
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
Most analytical queries require calculating metrics that involve multiple rows of data. `GROUP BY` allows us to perform aggregate calculations on sets of rows grouped by specified column values.

**Example**:

1. Create a report that shows the number of orders for each order priority segment.
```sql
SELECT
  o_orderpriority,
  COUNT(*) AS num_orders
FROM
  clickzetta_sample_data.tpch_100g.orders
GROUP BY
  o_orderpriority;
```
In the above query, we group by `orderpriority`, and the `count(*)` calculation will be applied to rows with a specific `orderpriority` value. The output will contain one row for each unique `orderpriority` value and the `count(*)` calculation.

^

Allowed calculations are usually SUM/MIN/MAX/AVG/COUNT. However, some databases have more complex aggregate functions; please refer to your database documentation.

### Subqueries

Use subqueries to use query results within a query.

When we want to use the result of one query as a table in another query, we use subqueries. **Example**:

1. Create a report showing the country, the number of items supplied by suppliers from that country, and the number of items purchased by customers from that country.
```sql
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
In the above query, we can see that there are two subqueries, one for calculating the number of items supplied by a country, and the other for calculating the number of items purchased by customers in that country.

### CASE WHEN&#x20;

Use the CASE statement to replicate IF.ELSE logic.

We can perform conditional logic in the `SELECT ... FROM` part of the query, as shown below.
```sql
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
We can see how to display different values based on the `totalprice` column. We can also use multiple conditions as our criteria (e.g., totalprice > 100000 AND orderpriority = '2-HIGH').

### Standard Functions

Use standard built-in database functions for common string, time, and numeric data operations.

When processing data, we often need to change the values in columns; here are some standard functions to be aware of:

1. **String Functions**

   1. **LENGTH** is used to calculate the length of a string. For example, `SELECT LENGTH('hi');` will output 2.
   2. **CONCAT** combines multiple string columns into one. For example, `SELECT CONCAT(o_orderstatus, '-', o_orderpriority) FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;` will concatenate the o\_orderstatus and o\_orderpriority columns, separated by a hyphen.
   3. **SPLIT** is used to split a value into an array based on a given delimiter. For example, `SELECT STRING_SPLIT(o_orderpriority, '-') FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;` will output a column where the array is formed by splitting the o\_orderpriority value at the `-`.
   4. **SUBSTRING** is used to get a substring from a value, given the start and end character indices. For example, `SELECT o_orderpriority, SUBSTRING(o_orderpriority, 1, 5) FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;` will get the first five (1 - 5) characters of the o\_orderpriority column.
   5. **TRIM** is used to remove spaces from both sides of a value. For example, `SELECT TRIM(' hi ');` will output `hi` without surrounding spaces. LTRIM and RTRIM are similar but only remove spaces from the beginning and end of the string, respectively.

2. **Date and Time Functions**

   1. **Adding and Subtracting Dates**: Used to add and subtract time periods; the format largely depends on the database. In Lakehouse, `datediff` takes 3 parameters, the output unit (day, month, year), date/time values a and b, so that the output is a - b. `+ INTERVAL n UNIT(DAY/MONTH/YEAR)` will add the value of the specified unit to the timestamp value.
```sql
  -- Date and Time Functions
  SELECT
      datediff(day, DATE '2022-10-01', DATE '2023-11-05') AS diff_in_days,
      datediff(month, DATE '2022-10-01', DATE '2023-11-05') AS diff_in_months,
      datediff(year, DATE '2022-10-01', DATE '2023-11-05') AS diff_in_years,
      DATE '2022-10-01' + INTERVAL 400 DAY AS new_date;
```
It will display the difference of the specified time period between two dates. We can also add/subtract any time period from the date/time column. For example, `SELECT DATE '2022-11-05' + INTERVAL '10' DAY;` will display the output `2022-11-15` (try date subtraction).

^

3. **String <=> Date/Time Conversion** <a name="string-date-time-conversion"></a>

When we want to change the data type of a string to date/time, we can use the `DATE 'YYYY-MM-DD'` or `TIMESTAMP 'YYYY-MM-DD HH:mm:SS'` functions. But if the data is in a non-standard date/time format, such as `MM/DD/YYYY`, we need to specify the input structure; we use `date\_format` to achieve this, for example:
```sql
SELECT date_format('2023-05-11', 'M-d-y');
```
We can use `date_format` to convert a timestamp/date into a string of the desired format. For example:
```sql
SELECT date_format(o_orderdate, 'yyyy-MM-01') AS first_month_date FROM clickzetta_sample_data.tpch_100g.orders LIMIT 5;
```
Please refer to [this page](sql_functions/scalar_functions/datetime_functions/date_format.md) to learn how to set the correct date and time format.

4. **Time Frame Functions (YEAR/MONTH/DAY)**: When we want to extract a specific time period from a date/time column, we can use these functions. For example, `SELECT year(DATE '2023-11-05');` will return 2023. Similarly, we also have month, day, hour, min, etc.

Please refer to [this page](time-function.md) to learn more about time functions.

5. **Numbers**

   1. **ROUND** is used to specify the number of digits allowed after the decimal point. For example, `SELECT ROUND(100.102345, 2);`
   2. **ABS** is used to get the absolute value of a given number. For example, `SELECT ABS(-100), ABS(100);`
   3. **Mathematical Operations** such as +,-,\*,/.
   4. **Ceil/Floor** is used to get the next higher and the nearest lower integer of a given decimal. For example, `SELECT CEIL(100.1), FLOOR(100.1);`

^