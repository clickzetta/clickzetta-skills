### SHIFTRIGHTUNSIGNED
```sql
shiftrightunsigned(value, n)
```
#### Description
Performs a logical right bitwise shift on an integer value. Logical right shift does not preserve the sign bit and fills the most significant bit with 0, meaning a negative number becomes positive after the shift. This function supports both int and bigint types.

#### Parameters
* `value`: int or bigint type, the value to be shifted
* `n`: int type, the number of bits to shift, must be greater than or equal to 0

#### Returns
* Same type as value (int or bigint)
* Returns the result after the right shift
* If `value` or `n` is NULL, returns NULL

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
* `shiftrightunsigned` is a logical right shift that does not preserve the sign bit and fills the most significant bit with 0.
* For positive numbers, the results of logical right shift and arithmetic right shift are identical.
* For negative numbers, logical right shift treats the sign bit as an ordinary bit and fills the most significant bit with 0.
* Differences from `shiftright`:
  * `shiftright` is an arithmetic right shift and preserves the sign bit.
  * `shiftrightunsigned` is a logical right shift and does not preserve the sign bit.
* Example: For -4 (int type, 32-bit binary representation `11111111111111111111111111111100`)
  * `shiftright(-4, 2)` = -1 (preserves the sign bit, result is `11111111111111111111111111111111`)
  * `shiftrightunsigned(-4, 2)` = 1073741823 (fills with 0, result is `00111111111111111111111111111111`)
* For bigint type (64-bit), the processing is identical, just with more bits.
* Common use cases:
  * Unsigned integer operations
  * Bitmask operations
  * Hash computation
  * Data encoding and decoding
* Related functions:
  * `shiftleft` - Left shift
  * `shiftright` - Arithmetic right shift (preserves the sign bit)
