### CUME\_DIST 
```sql
cume_dist() OVER ([PARTITION BY column1, column2, ...] [ORDER BY column1 [ASC|DESC], column2 [ASC|DESC], ...])
```
####  Description

The CUME\_DIST function is used to calculate the cumulative distribution ratio of the current row within the specified partition. Specifically, it returns a double type value representing the proportion of the current row and all preceding rows (within the partition) to the total number of rows in the partition. This function is commonly used in data analysis to understand the distribution of data across different groups.

#### Usage Instructions

* The PARTITION BY clause is used to divide the data into different partitions. If the PARTITION BY clause is not specified, the entire dataset will be considered as one partition.
* The ORDER BY clause is used to specify how the data should be sorted within each partition. The result of the CUME\_DIST function depends on the sorting order of the ORDER BY clause.
* If there are identical values in the ORDER BY column, the CUME\_DIST function will return the same result for these rows, which is the row\_number() of the last row divided by the number of rows in the window.

#### Return Results

* The return value type is double.
* The result is equal to `last_peer_row_number / partition_row_count`, where last\_peer\_row\_number represents the maximum row\_number() value of the current row and all preceding rows (within the partition), and partition\_row\_count represents the total number of rows in the partition.

#### Example
```sql
SELECT a,
       b,
       ROW_NUMBER() OVER(PARTITION BY a ORDER BY b) AS row_num,
       CUME_DIST() OVER (PARTITION BY a ORDER BY b) AS cume_dist
FROM VALUES ('A', 2), ('A', 1), ('B', 3), ('A', 1) tab(a, b);
```
Results:
```
A	b	row_num	cume_dist
------------------------------------------------------------------------------------------
A	1	1	0.6666666666666666
A	1	2	0.6666666666666666
A	2	3	1.0
B	3	1	1.0
```
In this example, we can see:

* When a = 'A', there are two rows (b = 1 and b = 2), their cume\_dist are 0.67 (2/3) and 1 (3/3) respectively.
* When a = 'B', there is only one row (b = 3), its cume\_dist is 1 (1/1).

#### More Examples

1. Calculate the cumulative distribution of employee salaries within each department:
```sql
SELECT dep_no,
       name,
       salary,
       CUME_DIST() OVER (PARTITION BY dep_no ORDER BY salary) AS cume_dist_salary
FROM VALUES
  ('Eric', 1, 28000),
  ('Alex', 1, 32000),
  ('Felix', 2, 21000),
  ('Frank', 1, 30000),
  ('Tom', 2, 23000),
  ('Jane', 3, 29000),
  ('Jeff', 3, 35000),
  ('Paul', 2, 29000),
  ('Charles', 2, 23000),
  ('null',4,null)
AS tab(name, dep_no, salary);
+--------+---------+--------+--------------------+
| dep_no |  name   | salary |  cume_dist_salary  |
+--------+---------+--------+--------------------+
| 3      | Jane    | 29000  | 0.5                |
| 3      | Jeff    | 35000  | 1.0                |
| 1      | Eric    | 28000  | 0.3333333333333333 |
| 1      | Frank   | 30000  | 0.6666666666666666 |
| 1      | Alex    | 32000  | 1.0                |
| 2      | Felix   | 21000  | 0.25               |
| 2      | Tom     | 23000  | 0.75               |
| 2      | Charles | 23000  | 0.75               |
| 2      | Paul    | 29000  | 1.0                |
| 4      | null    | null   | 1.0                |
+--------+---------+--------+--------------------+
```
2. Calculate the cumulative distribution of product sales within each category:
```sql
SELECT category_id,
       product_id,
       sales_amount,
       CUME_DIST() OVER (PARTITION BY category_id ORDER BY sales_amount) AS cume_dist_sales
FROM sales_data;
```
3. Calculate the cumulative distribution of the number of users in each age group:
```sql
SELECT age_group,
       user_id,
       CUME_DIST() OVER (ORDER BY age_group) AS cume_dist_users
FROM users;
```
Through these examples, you can better understand the application of the CUME\_DIST function in different scenarios.