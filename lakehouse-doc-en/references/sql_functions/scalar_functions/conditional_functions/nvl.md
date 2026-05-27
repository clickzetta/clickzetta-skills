### NVL 
```
nvl(expr1, expr2)
```
####  Description
The NVL function is used to handle NULL values in SQL queries. When the value of expr1 is NULL, the NVL function returns the value of expr2; otherwise, it returns the value of expr1. This function ensures that the returned result does not contain NULL values, facilitating subsequent data processing and analysis.

#### Parameter Description
- expr1: An expression of any type. When its value is NULL, the value of expr2 will be used as a substitute.
- expr2: An expression of the same type as expr1. When expr1 is NULL, it is returned as the substitute value.

#### Return Result
The return result is of the same type as expr1 and expr2.

#### Usage Example

1. Query employee salaries. If an employee's salary is NULL, display it as "Unknown":
```sql
SELECT name, nvl(salary, 'Unknown') AS salary FROM employees;
```
2. Calculate the total amount of the order. If the amount of an order is NULL, treat its amount as 0:
```sql
SELECT order_id, nvl(amount, 0) AS total_amount FROM orders;
```
### 3. Compare two numeric fields, if one of the fields is NULL, return the value of the other field: {#compare-two-numeric-fields-if-one-of-the-fields-is-null-return-the-value-of-the-other-field}
```sql
SELECT product_id, nvl(column1, column2) AS result FROM products;
```
4. Determine whether a student passes based on their exam scores. If the score is NULL, it is considered a pass:
```sql
SELECT student_id, nvl(score, 60) AS adjusted_score FROM student_scores;
```
By the above example, you can see that the NVL function is very useful when dealing with NULL values in SQL queries. It can help you avoid issues caused by NULL values in data analysis and report generation.