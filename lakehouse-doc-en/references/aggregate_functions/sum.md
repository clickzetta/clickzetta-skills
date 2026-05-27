### SUM Function
```sql
sum([distinct] expr)
```
#### Function Description
The SUM function is used to calculate and return the total sum of a set of numeric data. If the DISTINCT keyword is specified, the sum of the unique set of values will be calculated.

#### Parameter Description
- expr: A numeric type expression, which can be of type tinyint, smallint, int, bigint, float, double, or decimal.

#### Return Type
- For decimal type input, the result will be of decimal type, and the precision may increase accordingly.
- In other cases, the result will be of double type.

#### Notes
- If the value of expr is null, that value will not be included in the calculation.

#### Usage Example
1. Calculate the total sum of all values:
```sql
SELECT sum(col) FROM VALUES (5), (10), (15), (20) AS tab(col);
```
Results:
```
40
```
1. Calculate the sum of the deduplicated value set:
```sql
SELECT sum(DISTINCT col) FROM VALUES (5), (10), (15), (20) AS tab(col);
```
Results:
```
30
```
1. Calculate the sum of a column in an actual data table:
```sql
SELECT sum(score) FROM students;
```
Assume there is a column named score in the students table, this query will return the total sum of all students' scores.
2. Calculate the total sales within a certain period:
```sql
SELECT sum(sales) FROM sales_data WHERE date >= '2022-01-01' AND date <= '2022-12-31';
```
Assuming the `sales_data` table contains two columns, date and sales, this query will return the total sales for the year 2022.
3. Calculate the sum of values within a group:
```sql
SELECT department, sum(salary) FROM employees GROUP BY department;
```
Assuming the employees table contains the columns department and salary, this query will return the total salary of employees in each department.

From the above example, you can see the application of the SUM function in different scenarios. Please adjust the parameters and query conditions according to your actual needs.