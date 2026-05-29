# CEIL

The `CEILING` function returns the smallest integer greater than or equal to the specified value. In other words, it rounds the given value up to the nearest integer. This is useful when you need to ensure a value is not below a certain threshold.

#### Syntax

```Plain
CEILING(value)
```

#### Parameters

* `value`: The numeric value to round up. Can be an integer, floating-point number, or other numeric type.

#### Return Value

* Returns the smallest integer greater than or equal to `value`. The result type is typically an integer.

#### Examples

1. **Basic example**:

```SQL
SELECT CEILING(3.2) AS result;
+--------+
| result |
+--------+
| 4      |
+--------+
```

2. **Negative number example**:

```SQL
SELECT CEILING(-2.7) AS result;
+--------+
| result |
+--------+
| -2     |
+--------+
```

#### Notes

* The return value of `CEILING` is always an integer type.
* For positive numbers, `CEILING` rounds up to the next integer; for negative numbers, it returns the less negative integer (i.e., the one closer to zero).
* If the input value is already an integer, `CEILING` returns that integer unchanged.
