# SHIFTLEFT

```sql
shiftleft(value, n)
```

#### Function

Performs a left bit-shift operation on an integer value. Shifting left by n bits is equivalent to multiplying by 2^n. Supports int and bigint types.

#### Parameters

* `value`: int or bigint type, the value to shift
* `n`: int type, the number of bit positions to shift; must be greater than or equal to 0

#### Return Value

* The same type as `value` (int or bigint)
* Returns the result after the left shift
* Returns NULL if `value` or `n` is NULL

#### Examples

```sql
SELECT shiftleft(1, 2);
-- Result: 4
```

```sql
SELECT shiftleft(8, 2);
-- Result: 32
```

```sql
SELECT shiftleft(0, 2);
-- Result: 0
```

```sql
SELECT shiftleft(1L, 2);
-- Result: 4
```

```sql
SELECT shiftleft(8L, 2);
-- Result: 32
```

```sql
SELECT shiftleft(NULL, 2);
-- Result: NULL
```

```sql
SELECT shiftleft(1, NULL);
-- Result: NULL
```

```sql
SELECT shiftleft(-4, 2);
-- Result: -16
```

```sql
SELECT shiftleft(1, 10);  -- 2^10 = 1024
-- Result: 1024
```

#### Notes

* Shifting left by n bits is equivalent to multiplying by 2^n
* For positive numbers: shiftleft(x, n) = x * 2^n
* For negative numbers, the left shift preserves the sign bit
* Shift operations can cause overflow:
  * int range: -2,147,483,648 to 2,147,483,647
  * bigint range: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
* If the result exceeds the type range, overflow occurs (result is undefined)
* Bit-shift operations are faster than multiplication
* Common use cases:
  * Fast computation of powers of 2
  * Bit flag and bit mask operations
  * Data encoding and decoding
* Related functions:
  * shiftright — arithmetic right shift (preserves sign bit)
  * shiftrightunsigned — logical right shift (does not preserve sign bit)
