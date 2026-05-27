# Window Frame

Window Frame is a subset defined when using window functions to limit the computation scope of the window function, performing calculations only on the data within the window frame. Through window frames, you can precisely control how window functions compute and their results. Below is a detailed description and usage examples of window frames.

## Window Frame Syntax

When using window functions, define the window frame through the `OVER` clause with the following syntax:

```SQL
<window_function> OVER (
    [PARTITION BY <partition_expression>]
    [ORDER BY <order_expression>]
    [frame_clause>]
)
```

Where `<window_function>` represents the window function to use, such as `ROW_NUMBER()`, `RANK()`, `SUM()`, etc. The `PARTITION BY` clause is used to group data, with each group called a partition. The `ORDER BY` clause is used to sort data within each partition, which will affect the results of certain window functions such as `ROW_NUMBER()`, `RANK()`, etc. `frame_clause` is used to define the scope of the window frame and comes in two forms: `ROWS frame` and `RANGE frame`.

### ROWS frame

`ROWS frame` is a row-based window frame used to specify the number or position of rows included in the window frame. Its syntax is as follows:

```SQL
ROWS BETWEEN <start_boundary> AND <end_boundary>
```

`<start_boundary>` and `<end_boundary>` define the start and end boundaries of the window frame and can be one of the following values:

- `UNBOUNDED PRECEDING`: Starts from the first row of the partition.
- `UNBOUNDED FOLLOWING`: Ends at the last row of the partition.
- `CURRENT ROW`: The current row.
- `<offset> PRECEDING`: The row `<offset>` rows before the current row, where `<offset>` is a non-negative integer.
- `<offset> FOLLOWING`: The row `<offset>` rows after the current row, where `<offset>` is a non-negative integer.

### RANGE frame

`RANGE frame` is a value-based window frame used to specify the range of values of rows included in the window frame. Its syntax is as follows:

```SQL
RANGE BETWEEN <start_boundary> AND <end_boundary>
```

`<start_boundary>` and `<end_boundary>` define the start and end boundaries of the window frame and can be one of the following values:

- `UNBOUNDED PRECEDING`: Starts from the minimum value in the partition.
- `UNBOUNDED FOLLOWING`: Ends at the maximum value in the partition.
- `CURRENT ROW`: The value of the current row.
- `<value> PRECEDING`: The value of the current row minus `<value>`, where `<value>` is a non-negative number.
- `<value> FOLLOWING`: The value of the current row plus `<value>`, where `<value>` is a non-negative number.

## Window Frame Usage Examples

Below are some SQL query examples using Window Frames, along with their output results. Assume we have a table called sales containing monthly sales and profit margin data as follows:

| month | sales | profit |
| ----- | ----- | ------ |
| 1     | 100   | 0.1    |
| 2     | 120   | 0.15   |
| 3     | 80    | 0.05   |
| 4     | 150   | 0.2    |
| 5     | 90    | 0.1    |
| 6     | 110   | 0.12   |

### ROWS frame

* Query: Use the `SUM()` function and `ROWS frame` to calculate the sum of sales for the current month and the two months before and after.

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

* Query: Use the `AVG()` function and `ROWS frame` to calculate the average profit margin for the current month and the months before and after.

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

* Query: Use the `COUNT()` function and `RANGE frame` to calculate the distribution of each month's sales across the year, i.e., how many months have sales within 10 of the current month's sales.

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

* Query: Use the `MAX()` function and `RANGE frame` to calculate the maximum profit margin among the current month and the adjacent months.

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
