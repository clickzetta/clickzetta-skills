# NTH_VALUE 

## Description

The NTH_VALUE function is used to return the value of the row at the specified offset within a given window. This function is very useful when processing data, especially when you need to retrieve data from a specific position.

## Syntax
```sql
nth_value(expr, offset[,ignoreNull]) over ([partition_clause] [orderby_clause] [frame_clause])
```
## Parameters

- `expr`: An expression of any type.
- `offset`: A BIGINT type, must be a positive integer constant. When offset is 1, the function behaves the same as the FIRST_VALUE function.
- `ignoreNull`: Optional parameter, a boolean constant, default is false. When set to true, the function will return the nth non-null value within the window.

## Return Results

The return value type is the same as the expr type.

##  Example

Example 1
```sql
SELECT dep_no, salary, nth_value(salary, 3) OVER (PARTITION BY dep_no)
FROM VALUES
  ('Eric', 1, null),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000)
AS tab(name, dep_no, salary);
```
Result:
```
dep_no | salary | nth_value
-------+--------+-----------
1      | null   | 30000
1      | 32000  | 30000
1      | 30000  | 30000
2      | 21000  | 29000
2      | 23000  | 29000
2      | 29000  | 29000
2      | 23000  | 29000
3      | 29000  | null
3      | 35000  | null
```
Example 2
```sql
SELECT dep_no, salary, nth_value(salary, 3, true) OVER (PARTITION BY dep_no)
FROM VALUES
  ('Eric', 1, null),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000)
AS tab(name, dep_no, salary);
```
Result:
```
dep_no | salary | nth_value
-------+--------+-----------
1      | null   | null
1      | 32000  | null
1      | 30000  | null
2      | 21000  | 29000
2      | 23000  | 29000
2      | 29000  | 29000
2      | 23000  | 29000
3      | 29000  | null
3      | 35000  | null
```
Example 3
```sql
SELECT dep_no, salary, nth_value(salary, 3, true) OVER (PARTITION BY dep_no ORDER BY salary)
FROM VALUES
  ('Eric', 1, null),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000)
AS tab(name, dep_no, salary);
```
Result:
```
dep_no | salary | nth_value
-------+--------+-----------
1      | null   | null
1      | 30000  | null
1      | 32000  | null
2      | 21000  | null
2      | 23000  | 23000
2      | 23000  | 23000
2      | 29000  | 23000
3      | 29000  | null
3      | 3