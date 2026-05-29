# SHIFTRIGHT

```sql
shiftright(value, n)
```

#### Function

Performs an arithmetic right bit-shift operation on an integer value. Arithmetic right shift preserves the sign bit, so negative numbers remain negative after the shift. Shifting right by n bits is equivalent to integer division by 2^n (floor). Supports int and bigint types.

#### Parameters

* `value`: int or bigint type, the value to shift
* `n`: int type, the number of bit positions to shift; must be greater than or equal to 0

#### Return Value

* The same type as `value` (int or bigint)
* Returns the result after the right shift
* Returns NULL if `value` or `n` is NULL

#### Examples

```sql
SELECT shiftright(8, 2);
-- Result: 2
```

```sql
SELECT shiftright(1, 2);
-- Result: 0
```

```sql
SELECT shiftright(0, 2);
-- Result: 0
```

```sql
SELECT shiftright(8L, 2);
-- Result: 2
```

```sql
SELECT shiftright(32L, 2);
-- Result: 8
```

```sql
SELECT shiftright(NULL, 2);
-- Result: NULL
```

```sql
SELECT shiftright(8, NULL);
-- Result: NULL
```

```sql
SELECT shiftright(-4, 2);
-- Result: -1
```

```sql
SELECT shiftright(1024, 10);  -- 1024 / 2^10 = 1
-- Result: 1
```

#### Notes

* `shiftright` is an arithmetic right shift that preserves the sign bit
* For positive numbers: shiftright(x, n) = floor(x / 2^n)
* For negative numbers, arithmetic right shift preserves the sign bit; the result remains negative
* Right shift is equivalent to integer division (floor)
* Difference from `shiftrightunsigned`:
  * `shiftright` is arithmetic right shift, preserving the sign bit
  * `shiftrightunsigned` is logical right shift, filling the most significant bit with 0
* Example: for -4 (binary representation: 11111111111111111111111111111100)
  * shiftright(-4, 2) = -1 (sign bit preserved)
  * shiftrightunsigned(-4, 2) = 1073741823 (most significant bit filled with 0)
* Bit-shift operations are faster than division
* Common use cases:
  * Fast division by powers of 2
  * Bit flag and bit mask operations
  * Data encoding and decoding
* Related functions:
  * `shiftleft` — left shift
  * `shiftrightunsigned` — logical right shift (does not preserve sign bit)
