### LAG 

#### Description

The LAG function is used to obtain the data of the previous row or a specified number of rows before the current row. By using the LAG function, you can easily access the previous row data within the window for calculations or comparisons.

#### Syntax
```sql
LAG(expr[,offset[,default]]) OVER ([partition_clause] orderby_clause)
```
#### Parameter Description

* `expr` (any type): The expression for which the previous row is needed.
* `offset` (optional, `bigint` type constant, default is 1): Indicates the number of rows to move backward from the current row. When the value is 0, it indicates the current row; when the value is positive, it indicates the number of rows to move backward; when the value is negative, it indicates the number of rows to move forward.
* `default` (optional, constant of the same type as `expr`, default is `null`): The default value used when `offset` exceeds the window boundary.

#### Return Result

Returns the same data type as `expr`.

#### Usage Example

1. Get the data of the previous row:
```sql
SELECT a, b, LAG(b) OVER (PARTITION BY a ORDER BY b) as prev_b FROM VALUES ('A', 2), ('A', 1), ('B', 3), ('A', 1) tab(a, b);
```
Results:
```
A	1	null
A	1	1
A	2	1
B	3	null
```
2. Get the first two rows of data: 

```sql
SELECT a, b, LAG(b, 2) OVER (PARTITION BY a ORDER BY b) as prev_b FROM VALUES ('A', 2), ('A', 1), ('B', 3), ('A', 1) tab(a, b);
```
Results:
```
A	1	null
A	2	null
A       2        1
B	3	null
```
3. Use Default Values: 
```sql
SELECT a, b, LAG(b, 1, 0) OVER (PARTITION BY a ORDER BY b) as prev_b FROM VALUES ('A', 2), ('A', 1), ('B', 3), ('A', 1) tab(a, b);
```
Results:
```
A	1	0
A	1	1
A	2	1
B	3	0
```
#### Summary

The LAG function is a very useful tool that can help you easily access the previous row of data within a window. By adjusting the offset and default parameters, you can flexibly obtain the required data. In practical applications, the LAG function can be used to calculate moving averages, cumulative sums, and other statistical indicators.