# STARTSWITH 

##  Description

The `STARTSWITH` function is used to determine whether a string starts with another specified string. If the condition is met, it returns the Boolean value `TRUE`; otherwise, it returns `FALSE`. This function supports both string and binary data and is applicable to string processing and pattern matching scenarios.

## Syntax

```sql
STARTSWITH(expr, startExpr)
```

## Parameters

- `expr`: A `STRING` or `BINARY` expression representing the target data to be checked.
- `startExpr`: A `STRING` or `BINARY` expression representing the starting pattern for comparison.

## Return Value

- The return value is of Boolean type (`TRUE` or `FALSE`).
- If either `expr` or `startExpr` is `NULL`, the function returns `NULL`.
- If `startExpr` is an empty string or empty binary data, the function returns `TRUE`.

## Examples

Example 1: String pattern matching

```sql
SELECT STARTSWITH('SparkSQL', 'Spark') AS result;
+--------+
| result |
+--------+
| true   |
+--------+
```

Example 2: Case sensitivity

```sql
SELECT STARTSWITH('LakehouseSQL', 'lakehouse') AS result;
+--------+
| result |
+--------+
| false  |
+--------+
```

Example 3: Including NULL values

```sql
SELECT STARTSWITH('LakehouseSQL', NULL) AS result;
+--------+
| result |
+--------+
| null   |
+--------+
```

Example 4: Empty string or empty binary

```sql
SELECT STARTSWITH('LakehouseSQL', '') AS result;
+--------+
| result |
+--------+
| true   |
+--------+
```