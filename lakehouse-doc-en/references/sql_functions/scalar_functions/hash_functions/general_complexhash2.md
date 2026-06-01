# GENERAL_COMPLEXHASH2

## Overview

Computes a hash value for input data of any type and returns a BIGINT. The function automatically selects a more efficient computation method based on the type of the input.

## Syntax

```Plain
GENERAL_COMPLEXHASH2(<expr>)
```

## Parameters

- `<expr>`: Any type. Supports strings, integers, floating-point numbers, DATE, TIMESTAMP, and more.

## Examples

```sql
SELECT general_complexhash2('hello');
-- -5436999610281751320

SELECT general_complexhash2(123);
-- 9208534749291869864

SELECT general_complexhash2(3.14);
-- -3844631488065270338
```

## Related Documentation

- [GENERAL_MURMURHASH3](general_murmurhash3.md) — variant that always uses the MurmurHash3 algorithm
- [MURMURHASH3_64](murmurhash3_64.md)
