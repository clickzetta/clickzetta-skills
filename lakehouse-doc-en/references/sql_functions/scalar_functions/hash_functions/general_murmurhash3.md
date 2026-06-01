# GENERAL_MURMURHASH3

## Overview

Computes a hash value for input data of any type using the MurmurHash3 algorithm and returns a BIGINT.

## Syntax

```Plain
GENERAL_MURMURHASH3(<expr>)
```

## Parameters

- `<expr>`: Any type. Supports strings, integers, floating-point numbers, DATE, TIMESTAMP, and more.

## Examples

```sql
SELECT general_murmurhash3('hello');
-- -8014657081559513573

SELECT general_murmurhash3(123);
-- 5808450433748234714

SELECT general_murmurhash3(3.14);
-- 9195935839840165100
```

## Related Documentation

- [GENERAL_COMPLEXHASH2](general_complexhash2.md) — variant that automatically selects the algorithm
- [MURMURHASH3_64](murmurhash3_64.md)
