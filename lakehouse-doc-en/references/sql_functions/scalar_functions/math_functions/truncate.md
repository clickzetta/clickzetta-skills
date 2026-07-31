# TRUNCATE

#### Introduction

The `TRUNCATE` function truncates the numeric value `x` to `d` decimal places by discarding the excess digits without rounding.

> ⚠️ **Note**: `TRUNCATE` has floating-point precision issues, and the truncated result may not match expectations (for example, `TRUNCATE(3.14159, 2)` may return `3.14158` instead of `3.14`). For precise truncation, use `TRUNCATE_PRESTO` instead.

#### Syntax

```Plain
TRUNCATE(x, d)
```

#### Parameters

* `x`: The numeric value to truncate. Supports `FLOAT` and `DOUBLE` types.
* `d`: The number of decimal places to keep, of type `INT`. A positive `d` keeps the specified number of decimal places; `d = 0` truncates to an integer; a negative `d` truncates to the corresponding position to the left of the decimal point.

#### Return Value

Returns a numeric value of the same type as `x`.

#### Examples

Basic usage:

```sql
SELECT TRUNCATE(3.14159, 2);
-- Result: 3.14158 (note: floating-point precision may cause the actual result to differ from expected)

SELECT TRUNCATE(3.14500, 2);
-- Result: 3.14500

SELECT TRUNCATE(-3.14159, 2);
-- Result: -3.14160 (note: floating-point precision may cause the actual result to differ from expected)
```

Truncate to integer (`d = 0`):

```sql
SELECT TRUNCATE(9.99, 0);
-- Result: 9

SELECT TRUNCATE(-9.99, 0);
-- Result: -9
```

Truncate to the left of the decimal point with negative `d`:

```sql
SELECT TRUNCATE(123.456, -1);
-- Result: 120

SELECT TRUNCATE(123.456, -2);
-- Result: 100
```

#### Notes

* `TRUNCATE` discards excess decimal places directly — **no rounding is performed**.
* Due to the internal representation of floating-point numbers, results may be counterintuitive. For example, `TRUNCATE(3.14159, 2)` may actually return `3.14158`, and `TRUNCATE(-3.14159, 2)` may return `-3.14160`.
* For precise truncation, use `TRUNCATE_PRESTO`, which uses exact decimal arithmetic and is not affected by floating-point precision issues.
* When `d = 0`, the behavior is equivalent to taking the integer part (truncation toward zero, symmetric for positive and negative numbers).
