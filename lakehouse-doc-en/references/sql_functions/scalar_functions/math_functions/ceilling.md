#### Description

The `CEILING` function is used to return the smallest integer greater than or equal to a specified value. In other words, it rounds the given value up to the nearest integer. This is particularly useful in situations where you need to ensure that a value is not less than a certain threshold.

#### Syntax
```Plain
CEILING(value)
```
#### Parameters

* `value`: The value to be rounded up, which can be an integer, a floating-point number, or other numeric types.

#### Return Results

* Returns the smallest integer greater than or equal to `value`. The result is typically an integer.

#### Usage Example

1. **Basic Example**:
```SQL
SELECT CEILING(3.2) AS result;
+--------+
| result |
+--------+
| 4      |
+--------+
```
2. **Negative Number Example**:
```SQL
SELECT CEILING(-2.7) AS result;
+--------+
| result |
+--------+
| -2     |
+--------+
```
#### Notes

* The return value of the `CEILING` function is always an integer type.
* For positive numbers, the `CEILING` function rounds up to the next integer; for negative numbers, it returns the smaller integer (i.e., the integer closer to zero).
* If the input value is already an integer, the `CEILING` function will return the integer itself.