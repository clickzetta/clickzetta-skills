### COUNT Function
#### Overview
The `COUNT` function is used to calculate the number of rows in a set of data. It supports counting all rows or counting specified columns, including distinct counts.

#### Syntax
```sql
COUNT(*)
COUNT([DISTINCT] expr1[, expr2, ...])
```
#### Parameter Description
- `exprN`: Can be an expression of any type.

#### Return Results
- The return value type is `bigint`.
- When using the `COUNT(*)` form, all rows are counted, including rows with `NULL` values.
- When using the `COUNT(expr1[, expr2, ...])` form, if any expression value in a row is `NULL`, that row is ignored.
- When using the `COUNT(DISTINCT expr1[, expr2, ...])` form, the expression values are first deduplicated, then counted. If any expression value in a row is `NULL`, that row is ignored.

#### Example
1. Count the number of all rows (including `NULL` values):
```sql
SELECT COUNT(*) FROM employees;
```
Assume the `employees` table has 100 rows of data, including rows with `NULL` values, this query will return 100.

2. Count the number of rows with non-`NULL` values:
```sql
SELECT COUNT(DISTINCT department_id) FROM employees;
```
If the `employees` table has 80 distinct `department_id` values, this query will return 80.

3. Count the number of rows under specific conditions:
```sql
SELECT COUNT(*) FROM products WHERE quantity > 10;
```
If the `quantity` value in the `products` table is greater than 10 for 30 rows, this query will return 30.

4. Calculate the number of combinations of non-`NULL` values for two columns:
```sql
SELECT COUNT(*) FROM customers WHERE country != 'USA' AND city = 'New York';
```
If there are 20 rows in the `customers` table that meet the conditions, i.e., `country` is not 'USA' and `city` is 'New York', this query will return 20.

With the above example, you can use the `COUNT` function more effectively to get statistical information about the number of rows in the dataset.