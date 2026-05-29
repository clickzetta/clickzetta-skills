# Window Frame

Window Frame is a subset defined when using window functions to limit the calculation range of the window function, only calculating data within the window frame. Through the window frame, you can more precisely control the calculation method and results of the window function. Below are detailed explanations and usage examples of the window frame.

## Window Frame Syntax

When using window functions, you can define the window frame through the `OVER` clause, with the following syntax:

```SQL
<window_function> OVER (
    [PARTITION BY <partition_expression>]
    [ORDER BY <order_expression>]
    [<frame_clause>]
)
```

The syntax includes:

* `<window_function>`: Specifies the window function name (e.g., `ROW_NUMBER(), RANK(), SUM()`)
* `PARTITION BY`: Defines data partitioning criteria, creating distinct groups called partitions
* `ORDER BY`: Determines the sort order within partitions, crucial for functions like `ROW_NUMBER()` and `RANK()`
* frame\_clause: Specifies window frame boundaries, available in either ROWS or RANGE format

### ROWS frame

ROWS frame is a row-based window frame used to specify the number or position of rows included in the window frame. The syntax is as follows:

```SQL
ROWS BETWEEN <start_boundary> AND <end_boundary>
```

`<start_boundary>` and `<end_boundary>` are used to define the start and end boundaries of the window frame, and can be one of the following values:

* `UNBOUNDED PRECEDING`: Starts from the first row of the partition.
* `UNBOUNDED FOLLOWING`: Ends at the last row of the partition.
* `CURRENT ROW`: The current row.
* `<offset> PRECEDING`: The `<offset>`th row before the current row, where `<offset>` is a non-negative integer.
* `<offset> FOLLOWING`: The `<offset>`th row after the current row, where `<offset>` is a non-negative integer.

### RANGE frame

`RANGE frame` is a value-based window frame used to specify the range of values for the rows included in the window frame. The syntax is as follows:

```SQL
RANGE BETWEEN <start_boundary> AND <end_boundary>
```

`<start_boundary>` and `<end_boundary>` are used to define the start and end boundaries of the window frame, and can be one of the following values:

* `UNBOUNDED PRECEDING`: Starts from the minimum value in the partition.
* `UNBOUNDED FOLLOWING`: Ends at the maximum value in the partition.
* `CURRENT ROW`: The value of the current row.
* `<value> PRECEDING`: The value of the current row minus `<value>`, where `<value>` is a non-negative number.
* `<value> FOLLOWING`: The value of the current row plus `<value>`, where `<value>` is a non-negative number.

## Example Usage of Window Frame

Below are some examples of SQL queries using window frames and their output results. Suppose we have a table named sales that contains data on monthly sales and profit margins, as shown below:

|       |       |        |
| ----- | ----- | ------ |
| month | sales | profit |
| 1     | 100   | 0.1    |
| 2     | 120   | 0.15   |
| 3     | 80    | 0.05   |
| 4     | 150   | 0.2    |
| 5     | 90    | 0.1    |
| 6     | 110   | 0.12   |

### ROWS frame

* Query: Use the `SUM()` function and `ROWS frame` to calculate the total sales for each month along with the sales of the previous two months and the next two months.

```SQL
SELECT month, sales, SUM(sales) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) AS sum_sales
FROM sales;

+-------+-------+-----------+
| month | sales | sum_sales |
+-------+-------+-----------+
| 1     | 100   | 300       |
| 2     | 120   | 450       |
| 3     | 80    | 540       |
| 4     | 150   | 550       |
| 5     | 90    | 430       |
| 6     | 110   | 350       |
+-------+-------+-----------+
```

* Query: Use the `AVG()` function and `ROWS frame` to calculate the average profit margin for each month with the profit margin of the previous month and the next month.

```SQL
SELECT month, profit, AVG(profit) OVER (ORDER BY month ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS avg_profit
FROM sales;
+-------+--------+---------------------+
| month | profit |     avg_profit      |
+-------+--------+---------------------+
| 1     | 0.1    | 0.125               |
| 2     | 0.15   | 0.09999999999999999 |
| 3     | 0.05   | 0.13333333333333333 |
| 4     | 0.2    | 0.11666666666666665 |
| 5     | 0.1    | 0.14                |
| 6     | 0.12   | 0.11                |
+-------+--------+---------------------+
```

### RANGE frame

* Query: Use the `COUNT()` function and `RANGE frame` to calculate the distribution of each month's sales in the annual sales, that is, how many months' sales differ from the current month's sales by no more than 10.

```SQL
SELECT month, sales, COUNT(*) OVER (ORDER BY sales RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING) AS count_sales
FROM sales;
+-------+-------+-------------+
| month | sales | count_sales |
+-------+-------+-------------+
| 3     | 80    | 2           |
| 5     | 90    | 3           |
| 1     | 100   | 3           |
| 6     | 110   | 3           |
| 2     | 120   | 2           |
| 4     | 150   | 1           |
+-------+-------+-------------+
```

* Query: Use the `MAX()` function and `RANGE frame` to calculate the maximum profit margin for each month compared to the previous month and the following month.

```SQL
SELECT month, profit, MAX(profit) OVER (ORDER BY month RANGE BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS max_profit
FROM sales;
+-------+--------+------------+
| month | profit | max_profit |
+-------+--------+------------+
| 1     | 0.1    | 0.15       |
| 2     | 0.15   | 0.15       |
| 3     | 0.05   | 0.2        |
| 4     | 0.2    | 0.2        |
| 5     | 0.1    | 0.2        |
| 6     | 0.12   | 0.12       |
+-------+--------+------------+
```

^
