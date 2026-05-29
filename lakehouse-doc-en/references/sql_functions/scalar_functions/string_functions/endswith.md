## ENDSWITH 

##  Description

The `ENDSWITH` function is used to determine whether a string or binary expression ends with another specified string or binary expression. If the condition is met, it returns the Boolean value `TRUE`; otherwise, it returns `FALSE`. This function supports both string and binary data and is applicable to string processing and pattern matching scenarios.

## Syntax

```sql
ENDSWITH(expr, endExpr)
```

## Parameters

- `expr`: A string or binary expression representing the target data to be checked.
- `endExpr`: A string or binary expression representing the ending pattern for comparison.

## Return Value

- The return value is of Boolean type (`TRUE` or `FALSE`).
- If either `expr` or `endExpr` is `NULL`, the function returns `NULL`.
- If `endExpr` is an empty string or empty binary data, the function returns `TRUE`.

## Examples

Example 1: String pattern matching

```sql
SELECT ENDSWITH('LakehouseSQL', 'SQL') AS result;
+--------+
| result |
+--------+
| true   |
+--------+
```

Example 2: Case sensitivity

```sql
SELECT ENDSWITH('LakehouseSQL', 'sql') AS result;
+--------+
| result |
+--------+
| false  |
+--------+
```

Example 3: Including NULL values

```sql
SELECT ENDSWITH('LakehouseSQL', NULL) AS result;
+--------+
| result |
+--------+
| null   |
+--------+
```

Example 4: Empty string

```sql
SELECT ENDSWITH('LakehouseSQL', '') AS result;
+--------+
| result |
+--------+
| true   |
+--------+
```