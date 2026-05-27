## SQL Window Function
## Description

Window functions are a powerful analytical feature in SQL statements that allow you to perform calculations over a set of related rows, rather than just individual rows. By using the WINDOW clause, you can define one or more named windows, and then reference these windows in window functions to avoid rewriting the same window specification. This makes handling complex data sets in queries simpler and more efficient.

## Syntax
```SQL
WINDOW <window_name> AS (<window_specification>, ...)
```
Where `<window_name>` is the name specified for the window. It must be a valid identifier and cannot conflict with table names or column names. `<window_specification>` is the clause that defines the window range and order. It can contain the following parts:

* `PARTITION BY` clause: specifies how to divide data into different groups, each group being a partition.
* `ORDER BY` clause: specifies how to sort data within each partition. The sort order affects the results of some window functions, such as `ROW_NUMBER()`, `RANK()`, etc.
* `frame_clause` clause: specifies a subset of the window, i.e., the window frame, which can be used to limit the calculation range of window functions to only the data within the window frame. The `frame_clause` has two forms: `ROWS frame` and `RANGE frame`. For their syntax and meaning, refer to the [Window Frame](windowframe.md) documentation.

## Example of Using Window Clause

Below are some examples of SQL statements using the WINDOW clause and their output results. Assume we have a table named sales that contains sales amount and profit rate data for each month, as shown below:
```SQL
create table sales(month int,sales int,profit double);
INSERT INTO sales (month, sales, profit) VALUES
(1, 100, 0.1),
(2, 120, 0.15),
(3, 80, 0.05),
(4, 150, 0.2),
(5, 90, 0.1),
(6, 110, 0.12);
```
* Query: Use the window clause to define a window named w, which is ordered by month and includes the current row and the previous two rows of data. Then use the `SUM()` function and the `AVG()` function to calculate the total and average sales for each month.
```SQL
SELECT month, sales, SUM(sales) OVER w AS sum_sales, AVG(sales) OVER w AS avg_sales
FROM sales
WINDOW w AS (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW);



+-------+-------+-----------+--------------------+
| month | sales | sum_sales |     avg_sales      |
+-------+-------+-----------+--------------------+
| 1     | 100   | 100       | 100.0              |
| 2     | 120   | 220       | 110.0              |
| 3     | 80    | 300       | 100.0              |
| 4     | 150   | 350       | 116.66666666666667 |
| 5     | 90    | 320       | 106.66666666666667 |
| 6     | 110   | 350       | 116.66666666666667 |
+-------+-------+-----------+--------------------+
```
* Query: Define two windows named w1 and w2 using the window clause, which group and sort by quarter and month respectively, then use the `RANK()` function and `ROW_NUMBER()` function to calculate the sales ranking for each month within the quarter and the entire year.
```SQL
SELECT month, sales, RANK() OVER w1 AS rank_quarter, ROW_NUMBER() OVER w2 AS rank_year
FROM sales
WINDOW w1 AS (PARTITION BY CEIL(month / 3) ORDER BY sales DESC),
       w2 AS (ORDER BY sales DESC);
       
       
+-------+-------+--------------+-----------+
| month | sales | rank_quarter | rank_year |
+-------+-------+--------------+-----------+
| 4     | 150   | 1            | 1         |
| 2     | 120   | 1            | 2         |
| 6     | 110   | 2            | 3         |
| 1     | 100   | 2            | 4         |
| 5     | 90    | 3            | 5         |
| 3     | 80    | 3            | 6         |
+-------+-------+--------------+-----------+
```