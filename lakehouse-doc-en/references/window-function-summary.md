## Window Functions

Window Functions are powerful SQL functions that allow users to perform grouped calculations on a dataset within a query. Unlike traditional aggregate functions, window functions can calculate each row of data while retaining the detailed information of the original data. Window functions have a wide range of applications in data analysis, report generation, and other scenarios, such as calculating rankings, cumulative sums, moving averages, etc.

## Basic Syntax of Window Functions

The basic syntax of window functions is as follows:

```SQL
<window_function> OVER (
    [PARTITION BY <partition_expression>]
    [ORDER BY <order_expression>]
)
```

* `<window_function>`: Specify the window function to use, such as `ROW_NUMBER()`, `RANK()`, `SUM()`, etc.
* `PARTITION BY`: Divide the dataset into different partitions, each partition being an independent calculation scope.
* `ORDER BY`: Sort the data within each partition, affecting the calculation results of some window functions.

## Classification of Window Functions

Based on functionality and return value type, window functions can be divided into the following categories:

1. **Ranking Functions**: Rank the data and return an integer value representing the relative position. Common ranking functions include `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `PERCENT_RANK()`, `CUME_DIST()`, `NTILE()`, etc.
2. **Aggregate Functions**: Perform aggregate calculations on the data and return a value representing the overall characteristics. Lakehouse supports all standard aggregate functions.
3. **Analytic Functions**: Perform analytical calculations on the data and return a value representing the data characteristics. Common analytic functions include `FIRST_VALUE()`, `LAST_VALUE()`, `LAG()`, `LEAD()`, `NTH_VALUE()`, `CUME_DIST()`, etc.

## Examples of Using Window Functions

Below are some examples of SQL queries using window functions and their output results. Suppose we have a table named sales that contains data on monthly sales and profit margins, as shown below:

```SQL
CREATE    TABLE sales (MONTH int, sales int, profit double);
INSERT    INTO sales (MONTH, sales, profit)
VALUES    (1, 100, 0.1),
          (2, 120, 0.15),
          (3, 80, 0.05),
          (4, 150, 0.2),
          (5, 90, 0.1),
          (6, 110, 0.12);
```

### Ranking Functions

* Query: Use the `ROW_NUMBER()` function to rank sales in descending order.

```SQL
SELECT month, sales, ROW_NUMBER() OVER (ORDER BY sales DESC) AS rank
FROM sales;
+-------+-------+------+
| month | sales | rank |
+-------+-------+------+
| 4     | 150   | 1    |
| 2     | 120   | 2    |
| 6     | 110   | 3    |
| 1     | 100   | 4    |
| 5     | 90    | 5    |
| 3     | 80    | 6    |
+-------+-------+------+
```

* Query: Use the `RANK()` function to rank the profit margin in ascending order and group by quarter.

```SQL
SELECT month, profit, RANK() OVER (PARTITION BY CEIL(month / 3) ORDER BY profit ASC) AS rank
FROM sales;
+-------+--------+------+
| month | profit | rank |
+-------+--------+------+
| 3     | 0.05   | 1    |
| 1     | 0.1    | 2    |
| 2     | 0.15   | 3    |
| 5     | 0.1    | 1    |
| 6     | 0.12   | 2    |
| 4     | 0.2    | 3    |
+-------+--------+------+
```

### Aggregate Functions

* Query: Use the `AVG()` function to calculate the difference between the monthly sales and the annual average sales.

```SQL
SELECT month, sales, sales - AVG(sales) OVER () AS diff
FROM sales;
+-------+-------+--------------------+
| month | sales |        diff        |
+-------+-------+--------------------+
| 1     | 100   | -8.333333333333329 |
| 2     | 120   | 11.666666666666671 |
| 3     | 80    | -28.33333333333333 |
| 4     | 150   | 41.66666666666667  |
| 5     | 90    | -18.33333333333333 |
| 6     | 110   | 1.6666666666666714 |
+-------+-------+--------------------+
```

### Analytic Functions

* Query: Use the `LAG()` function and `LEAD()` function to calculate the difference in sales between each month and the previous month and the next month.

```SQL
SELECT month, sales, sales - LAG(sales) OVER (ORDER BY month) AS prev_diff, sales - LEAD(sales) OVER (ORDER BY month) AS next_diff
FROM sales;
+-------+-------+-----------+-----------+
| month | sales | prev_diff | next_diff |
+-------+-------+-----------+-----------+
| 1     | 100   | null      | -20       |
| 2     | 120   | 20        | 40        |
| 3     | 80    | -40       | -70       |
| 4     | 150   | 70        | 60        |
| 5     | 90    | -60       | -20       |
| 6     | 110   | 20        | null      |
+-------+-------+-----------+-----------+
```

* Query: Use the `CUME_DIST()` function to calculate the cumulative distribution of monthly sales in the annual sales.

```SQL
SELECT month, sales, CUME_DIST() OVER (ORDER BY sales) AS cume_dist
FROM sales;
+-------+-------+---------------------+
| month | sales |      cume_dist      |
+-------+-------+---------------------+
| 3     | 80    | 0.16666666666666666 |
| 5     | 90    | 0.3333333333333333  |
| 1     | 100   | 0.5                 |
| 6     | 110   | 0.6666666666666666  |
| 2     | 120   | 0.8333333333333334  |
| 4     | 150   | 1.0                 |
+-------+-------+---------------------+
```

^
