## IFNULL Function

The IFNULL function is a logical function used to handle NULL values that may appear in SQL queries. When the value of the first parameter is NULL, the IFNULL function returns the value of the second parameter; if the value of the first parameter is not NULL, it returns the value of the first parameter.

### Syntax

```sql
IFNULL(expression_1, expression_2)
```

- `expression_1`: The expression to check, typically a field name.
- `expression_2`: The value to return when `expression_1` is NULL.

### Usage Notes

- `expression_1` and `expression_2` must be of the same or compatible data types.
- If `expression_1` and `expression_2` have incompatible data types, the IFNULL function returns NULL.
- The return value of the IFNULL function inherits the data type of `expression_1` or `expression_2`.

### Examples

Suppose we have a table named `student` with the following columns:

- `id`: The unique identifier of the student.
- `name`: The name of the student.
- `score`: The score of the student.

The `student` table contains the following data:

| id | name  | score |
|----|-------|-------|
| 1  | Alice | 90    |
| 2  | Bob   | NULL  |
| 3  | Cathy | 80    |
| 4  | David | NULL  |

Now, we want to query the name and score of each student, replacing NULL scores with 0. We can use the following SQL statement:

```sql
SELECT name, IFNULL(score, 0) AS score FROM student;
```

The query result is:

| name  | score |
|-------|-------|
| Alice | 90    |
| Bob   | 0     |
| Cathy | 80    |
| David | 0     |

### More Examples

1. Query the student's name and age; if age is NULL, display "Unknown":

```sql
SELECT name, IFNULL(age, 'Unknown') AS age FROM student;
```

2. Query the employee's name and salary; if salary is NULL, display "Not available":

```sql
SELECT name, IFNULL(salary, 'Not available') AS salary FROM employee;
```

3. Query the product name and stock quantity; if stock quantity is NULL, display "Out of stock":

```sql
SELECT product_name, IFNULL(stock_quantity, 'Out of stock') AS stock FROM products;
```

By using the IFNULL function, we can ensure that NULL values do not appear in query results, thereby improving data readability and usability.
