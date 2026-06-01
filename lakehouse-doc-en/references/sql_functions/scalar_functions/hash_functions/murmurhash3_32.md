# MURMURHASH3_32

## Overview

Computes a 32-bit hash value for the input using the MurmurHash3 algorithm and returns an INT.

## Syntax

```Plain
MURMURHASH3_32(<expr>)
```

## Parameters

- `<expr>`: A primitive data type. Supports strings, integers, floating-point numbers, and more.

## Examples

```sql
SELECT murmurhash3_32('hello');
-- 613153351

SELECT murmurhash3_32(123);
-- 941089142

SELECT murmurhash3_32('world');
-- -74040069
```

## Related Documentation

- [MURMURHASH3_64](murmurhash3_64.md) — 64-bit variant with higher precision
- [GENERAL_MURMURHASH3](general_murmurhash3.md)
