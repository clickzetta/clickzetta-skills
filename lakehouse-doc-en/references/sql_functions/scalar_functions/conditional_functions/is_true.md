### IS_TRUE Function

```
is_true(expr)
```

#### Description

The `IS_TRUE` function determines whether the value of an expression is `true`. This function supports boolean and string types, and can recognize various string formats that represent `true`.

#### Parameters

* `expr`: `BOOLEAN` or `STRING` type, the expression to evaluate.

#### Return Type

* Returns `BOOLEAN` type.
* Returns `true` if the expression value is `true` or a string representing `true`.
* Returns `false` if the expression value is `false` or a string representing `false`.
* Returns `false` if the expression value is `NULL`.

#### Notes

* The `IS_TRUE` function recognizes the following strings as `true`: 't', 'true', '1', 'yes'.
* The `IS_TRUE` function recognizes the following strings as `false`: 'f', 'false', '0', 'no'.
* Difference from using `expr` directly: `is_true(NULL)` returns `false`, while `NULL` in a boolean context is handled specially.
* String matching is case-insensitive.

#### Examples

1. Boolean evaluation

```sql
SELECT is_true(true), is_true(false), is_true(NULL);
+---------------+----------------+----------------+
| is_true(true) | is_true(false) | is_true(NULL)  |
+---------------+----------------+----------------+
| true          | false          | false          |
+---------------+----------------+----------------+
```

2. String evaluation (supports multiple formats)

```sql
SELECT is_true('t'), is_true('f');
+--------------+--------------+
| is_true('t') | is_true('f') |
+--------------+--------------+
| true         | false        |
+--------------+--------------+
```

3. Using in a WHERE clause

```sql
SELECT * FROM VALUES (true), (false), (NULL) AS t(flag)
WHERE is_true(flag);
+------+
| flag |
+------+
| true |
+------+
```
