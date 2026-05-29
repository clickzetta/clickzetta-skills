## IS NULL

`IS NULL` clause is used in the `WHERE` condition to determine if the value in a column is `NULL`. `NULL` indicates that the column has no value or the value is unknown. It is important to note that `NULL` is different from an empty string or a space, which have specific values.

## Notes

Using an equal sign (`=`) to determine `NULL` will not yield the expected result because `NULL` cannot be compared using an equal sign.

## Syntax
```sql
SELECT * FROM table_name WHERE expression IS NULL;
SELECT * FROM table_name WHERE expression IS NOT NULL;
```
Among them` Expression is the expression to be evaluated, and it can be of any type` The return values of IS NULL and IS NOT NULL are Boolean types (BOOLEAN). If the value of expression is NULL, return TRUE; otherwise, return FALSE.

## Example

Assuming we have a table named 'student', which contains the following data:

| id | name  | gender |
|----|-------|--------|
| 1  | Alice | F      |
| 2  | Bob   | M      |
| 3  | Cathy | F      |
| 4  | David | NULL   |

1. Now, to query students with gender 'NULL' from the 'student' table, we can use the following SQL statement:
   ```sql
   SELECT * FROM student WHERE gender IS NULL;
   ```
The result set is as follows:

| id | name  | gender |
|---|-------|--------|
| 4  | David | NULL   |

2. If we want to query students whose gender is not `NULL`, we can use the following SQL statement:
   ```sql
   SELECT * FROM student WHERE gender IS NOT NULL;
   ```
The result set is as follows:

   | id | name  | gender |
   |---|-------|--------|
   | 1  | Alice | F      |
   | 2  | Bob   | M      |
   | 3  | Cathy | F      |

## Frequently Asked Questions

Q: Why does using the equals sign (`=`) to compare `NULL` values not yield the expected result?

A: This is because `NULL` represents an unknown or missing value, so it cannot be compared to any value (including `NULL`). When using the equals sign (`=`) to compare `NULL` values, the result will be `UNKNOWN`, not `TRUE` or `FALSE`. Therefore, we need to use `IS NULL` or `IS NOT NULL` to determine `NULL` values.