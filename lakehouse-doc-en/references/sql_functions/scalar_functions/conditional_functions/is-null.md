## IS NULL

The `IS NULL` clause is used in `WHERE` conditions to determine whether a column value is `NULL`. `NULL` means the column has no value or the value is unknown. Note that `NULL` is different from an empty string or spaces, which are concrete values.

## Notes

Using the equality operator (`=`) to check for `NULL` does not produce the expected result, because `NULL` cannot be compared using the equality operator.

## Syntax

```sql
SELECT * FROM table_name WHERE expression IS NULL;
SELECT * FROM table_name WHERE expression IS NOT NULL;
```

Here, `expression` is the expression to evaluate, which can be of any type. `IS NULL` and `IS NOT NULL` return a boolean type (`BOOLEAN`). If the value of `expression` is `NULL`, it returns `TRUE`, otherwise it returns `FALSE`.

## Examples

Suppose we have a table named `student` with the following data:

| id | name  | gender |
|----|-------|--------|
| 1  | Alice | F      |
| 2  | Bob   | M      |
| 3  | Cathy | F      |
| 4  | David | NULL   |

1. Now, we want to query students from the `student` table whose gender is `NULL`. We can use the following SQL statement:

   ```sql
   SELECT * FROM student WHERE gender IS NULL;
   ```

   The result set is:

   | id | name  | gender |
   |---|-------|--------|
   | 4  | David | NULL   |

2. If we want to query students whose gender is not `NULL`, we can use the following SQL statement:

   ```sql
   SELECT * FROM student WHERE gender IS NOT NULL;
   ```

   The result set is:

   | id | name  | gender |
   |---|-------|--------|
   | 1  | Alice | F      |
   | 2  | Bob   | M      |
   | 3  | Cathy | F      |

## FAQ

Q: Why does using the equality operator (`=`) to check for `NULL` not produce the expected result?

A: This is because `NULL` represents an unknown or missing value, so it cannot be compared with any value (including `NULL`). When using the equality operator (`=`) to evaluate `NULL`, the result will be `UNKNOWN`, not `TRUE` or `FALSE`. Therefore, you must use `IS NULL` or `IS NOT NULL` to check for `NULL`.
