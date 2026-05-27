### SHIFTRIGHT
```sql
shiftright(value, n)
```
#### Description
Performs an arithmetic right bitwise shift on an integer value. Arithmetic right shift preserves the sign bit, meaning a negative number remains negative after the shift. Shifting right by n bits is equivalent to dividing by 2^n (rounded down). This function supports both int and bigint types.

#### Parameters
* `value`: int or bigint type, the value to be shifted
* `n`: int type, the number of bits to shift, must be greater than or equal to 0

#### Returns
* Same type as value (int or bigint)
* Returns the result after the right shift
* If value or n is NULL, returns NULL

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
* shiftright is an arithmetic right shift and preserves the sign bit.
* For positive numbers: shiftright(x, n) = floor(x / 2^n)
* For negative numbers, the arithmetic right shift preserves the sign bit, and the result remains negative after the shift.
* The right shift operation is equivalent to integer division (rounded down).
* Differences from `shiftrightunsigned`:
  * `shiftright` is an arithmetic right shift and preserves the sign bit.
  * `shiftrightunsigned` is a logical right shift and does not preserve the sign bit, filling the most significant bit with 0.
* Example: For -4 (binary representation: 11111111111111111111111111111100)
  * shiftright(-4, 2) = -1 (preserves the sign bit)
  * shiftrightunsigned(-4, 2) = 1073741823 (fills the most significant bit with 0)
* Bit shift operations are bitwise operations and have better performance than division.
* Common use cases:
  * Fast computation of division by powers of 2
  * Bit flags and bitmask operations
  * Data encoding and decoding
* Related functions:
  * `shiftleft` - Left shift
  * `shiftrightunsigned` - Logical right shift (does not preserve the sign bit)
