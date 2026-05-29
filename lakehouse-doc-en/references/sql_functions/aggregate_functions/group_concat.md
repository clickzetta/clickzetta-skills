#### Overview

The `group_concat` function concatenates a group of string values into a single string. This function is useful when processing multiple rows or records, allowing you to merge results from the same group into one string, commonly used for report generation and data aggregation scenarios.

#### Syntax

```sql
group_concat([DISTINCT] expression [ORDER BY sort_expr [ASC|DESC]] [SEPARATOR sep_string]) [FILTER (WHERE condition)]
```

#### Parameters

* `DISTINCT`: (Optional) Removes duplicate values before concatenation.
* `expression`: The column or expression to concatenate.
* `ORDER BY sort_expr`: (Optional) Specifies the sort order of elements in the concatenated result.
* `sep_string`: (Optional) The string used as a separator. If omitted, `Lakehouse` defaults to a comma (`,`).

#### Return Results

* Returns a string containing all concatenated non-`NULL` values, separated by the specified separator.

#### Examples

1. Basic usage:

```sql
SELECT a, group_concat(b SEPARATOR "-")
FROM VALUES ('A1', 2), ('A1', 1), ('A2', 3), ('A1', 1) AS tab(a, b)
GROUP BY a;
+----+-------------------+
| a  | WM_CONCAT('-', b) |
+----+-------------------+
| A2 | 3                 |
| A1 | 2-1-1             |
+----+-------------------+
```

2. Conditionally concatenate strings using the FILTER clause (use `wm_concat` instead; the `group_concat(expr SEPARATOR sep) FILTER (WHERE ...)` syntax is not supported):

```sql
SELECT a, wm_concat('-', b) FILTER (WHERE b > 1)
FROM VALUES ('A1', 2), ('A1', 1), ('A2', 3), ('A1', 3) AS tab(a, b)
GROUP BY a;
+----+--------------------------------------------+
| a  | WM_CONCAT('-', b) FILTER (WHERE (b > 1))   |
+----+--------------------------------------------+
| A2 | 3                                          |
| A1 | 2-3                                        |
+----+--------------------------------------------+
```

3. Use ORDER BY to control concatenation order:

```sql
SELECT a, group_concat(b ORDER BY b ASC SEPARATOR "-")
FROM VALUES ('A1', 2), ('A1', 1), ('A2', 3), ('A1', 3) AS tab(a, b)
GROUP BY a;
-- Result for A1 is 1-2-3 (sorted in ascending order)
```

4. Use DISTINCT to remove duplicates:

```sql
SELECT a, group_concat(DISTINCT b SEPARATOR ",")
FROM VALUES ('A1', 1), ('A1', 1), ('A1', 2) AS tab(a, b)
GROUP BY a;
-- Result for A1 is 1,2 (duplicate 1 removed)
```

#### Notes

* If the resulting string exceeds the system's maximum length limit, `group_concat` may throw an error. In `Lakehouse`, this limit can be adjusted by setting the table property `cz.storage.write.max.string.bytes` system variable.
* When using the `group_concat` function, note that `NULL` values are ignored and not included in the final string.
* The `group_concat(expr SEPARATOR sep) FILTER (WHERE ...)` syntax is not supported and will produce a syntax error. To use a FILTER clause, use the equivalent `wm_concat(sep, expr) FILTER (WHERE ...)` syntax instead.
