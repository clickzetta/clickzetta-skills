# SHIFTRIGHTUNSIGNED

```sql
shiftrightunsigned(value, n)
```

#### Function

Performs a logical right bit-shift operation on an integer value. Logical right shift does not preserve the sign bit; the most significant bit is filled with 0, so negative numbers become positive after the shift. Supports int and bigint types.

#### Parameters

* `value`: int or bigint type, the value to shift
* `n`: int type, the number of bit positions to shift; must be greater than or equal to 0

#### Return Value

* The same type as `value` (int or bigint)
* Returns the result after the right shift
* Returns NULL if `value` or `n` is NULL

#### Examples

```sql
SELECT shiftrightunsigned(8, 2);
-- Result: 2
```

```sql
SELECT shiftrightunsigned(1, 2);
-- Result: 0
```

```sql
SELECT shiftrightunsigned(0, 2);
-- Result: 0
```

```sql
SELECT shiftrightunsigned(8L, 2);
-- Result: 2
```

```sql
SELECT shiftrightunsigned(32L, 2);
-- Result: 8
```

```sql
SELECT shiftrightunsigned(NULL, 2);
-- Result: NULL
```

```sql
SELECT shiftrightunsigned(8, NULL);
-- Result: NULL
```

```sql
SELECT shiftrightunsigned(-4, 2);
-- Result: 1073741823
```

```sql
SELECT shiftright(-4, 2), shiftrightunsigned(-4, 2);
-- Result: -1	1073741823
```

#### Notes

* `shiftrightunsigned` is a logical right shift; it does not preserve the sign bit and fills the most significant bit with 0
* For positive numbers, logical right shift and arithmetic right shift produce the same result
* For negative numbers, logical right shift treats the sign bit as a regular bit and fills the most significant bit with 0
* Difference from `shiftright`:
  * `shiftright` is arithmetic right shift, preserving the sign bit
  * `shiftrightunsigned` is logical right shift, not preserving the sign bit
* Example: for -4 (int type, 32-bit binary representation: `11111111111111111111111111111100`)
  * `shiftright(-4, 2)` = -1 (sign bit preserved, result: `11111111111111111111111111111111`)
  * `shiftrightunsigned(-4, 2)` = 1073741823 (filled with 0, result: `00111111111111111111111111111111`)
* For bigint type (64-bit), the behavior is the same with more bits
* Common use cases:
  * Unsigned integer arithmetic
  * Bit mask operations
  * Hash computation
  * Data encoding and decoding
* Related functions:
  * `shiftleft` — left shift
  * `shiftright` — arithmetic right shift (preserves sign bit)
