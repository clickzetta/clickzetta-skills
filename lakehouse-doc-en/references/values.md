# VALUES Clause

## Description

The `VALUES` clause is used to construct inline row data. It can be used as a standalone query or as a temporary table in the `FROM` clause. It is commonly used for quick testing, constructing sample data, or inserting data together with `INSERT INTO`.

## Syntax

```sql
-- Standalone usage
VALUES (expr1 [, expr2, ...]) [, (expr1 [, expr2, ...]), ...]

-- Used in FROM clause, specifying table alias and column names
SELECT ...
FROM VALUES (expr1 [, expr2, ...]) [, ...] AS table_alias(col1 [, col2, ...])

-- Short form (omitting the VALUES keyword)
SELECT ...
FROM (expr1 [, expr2, ...]) [, ...] AS table_alias(col1 [, col2, ...])
```

## Parameters

- `expr`: Any expression, which can be a literal, function call, or computed expression.
- `table_alias`: The alias for the temporary table.
- `col1, col2, ...`: The aliases for the columns.

## Examples

### Standalone Query

```sql
VALUES (1, 'a'), (2, 'b'), (3, 'c');
+------+------+
| col1 | col2 |
+------+------+
| 1    | a    |
| 2    | b    |
| 3    | c    |
+------+------+
```

### Using in FROM Clause

```sql
SELECT id, name
FROM VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie') AS t(id, name);
+----+---------+
| id | name    |
+----+---------+
| 1  | Alice   |
| 2  | Bob     |
| 3  | Charlie |
+----+---------+
```

### Using with Aggregate Functions

```sql
SELECT sum(val) AS total
FROM VALUES (10), (20), (30) AS t(val);
+-------+
| total |
+-------+
| 60    |
+-------+
```

### Multiple Columns of Different Types

```sql
SELECT *
FROM VALUES
  (1, 'hello', date '2024-01-01', true),
  (2, 'world', date '2024-06-15', false)
AS t(id, msg, dt, flag);
+----+-------+------------+-------+
| id | msg   | dt         | flag  |
+----+-------+------------+-------+
| 1  | hello | 2024-01-01 | true  |
| 2  | world | 2024-06-15 | false |
+----+-------+------------+-------+
```

### Using with INSERT INTO

```sql
INSERT INTO my_table
VALUES (1, 'Alice'), (2, 'Bob');
```

## Notes

- The number of columns in each row must be consistent.
- The types of columns in corresponding positions across rows must be compatible; the system will automatically infer the common type.
- When using in the FROM clause, it is recommended to specify column names via `AS table_alias(col1, col2, ...)`, otherwise column names default to `col1`, `col2`, etc.
- VALUES can be combined with UNION, JOIN, and other operations.
