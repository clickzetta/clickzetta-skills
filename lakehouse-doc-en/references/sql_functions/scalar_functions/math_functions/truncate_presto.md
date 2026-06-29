# TRUNCATE_PRESTO

#### Introduction

`TRUNCATE_PRESTO` truncates a numeric value to the specified number of decimal places by discarding excess digits without rounding.

Compared to the `TRUNCATE` function, `TRUNCATE_PRESTO` does not have floating-point precision issues (`TRUNCATE(3.14159, 2)` may return `3.14158`, whereas `TRUNCATE_PRESTO(3.14159, 2)` always returns `3.14`). Use `TRUNCATE_PRESTO` as the preferred option.

#### Syntax

```sql
TRUNCATE_PRESTO(x, d)
```

#### Parameters

* `x`: A numeric expression to truncate. Supports `FLOAT`, `DOUBLE`, `DECIMAL`, and other numeric types.
* `d`: The number of decimal places to keep, as an integer. `d = 0` truncates to an integer; `d > 0` keeps the specified number of decimal places; `d < 0` truncates to the corresponding position to the left of the decimal point.

#### Return Value

* Returns the truncated numeric value of the same type as the input `x`.
* Truncation discards excess digits without rounding.
* Negative numbers are truncated on their absolute value and the sign is preserved. For example, `-3.14159` truncated to 2 decimal places returns `-3.14`.

#### Examples

1. Truncate a positive number to 2 decimal places:

```sql
SELECT TRUNCATE_PRESTO(3.14159, 2);
+-----------------------------+
| truncate_presto(3.14159, 2) |
+-----------------------------+
| 3.14                        |
+-----------------------------+
```

2. Truncate a negative number to 2 decimal places:

```sql
SELECT TRUNCATE_PRESTO(-3.14159, 2);
+------------------------------+
| truncate_presto(-3.14159, 2) |
+------------------------------+
| -3.14                        |
+------------------------------+
```

3. Truncate to an integer (`d = 0`):

```sql
SELECT TRUNCATE_PRESTO(9.99, 0);
+--------------------------+
| truncate_presto(9.99, 0) |
+--------------------------+
| 9                        |
+--------------------------+
```

4. Truncate to the left of the decimal point (`d < 0`):

```sql
SELECT TRUNCATE_PRESTO(314.159, -2);
+------------------------------+
| truncate_presto(314.159, -2) |
+------------------------------+
| 300                          |
+------------------------------+
```

5. Precision comparison with `TRUNCATE`:

```sql
SELECT TRUNCATE(3.14159, 2), TRUNCATE_PRESTO(3.14159, 2);
+----------------------+-----------------------------+
| truncate(3.14159, 2) | truncate_presto(3.14159, 2) |
+----------------------+-----------------------------+
| 3.14158              | 3.14                        |
+----------------------+-----------------------------+
```

#### Notes

* `TRUNCATE_PRESTO` only truncates; it does not round. `TRUNCATE_PRESTO(3.999, 2)` returns `3.99`, not `4.00`.
* When `TRUNCATE` produces unexpected floating-point results (such as returning `3.14158` instead of `3.14`), switch to `TRUNCATE_PRESTO`.
* Use the `ROUND` function when rounding is needed.

#### Related Documentation

* [ROUND](round.md)
* [FLOOR](floor.md)
* [CEIL](ceil.md)
