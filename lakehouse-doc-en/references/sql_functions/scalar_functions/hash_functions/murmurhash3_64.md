# MURMURHASH3_64

## Overview

Computes a 64-bit hash value for the input using the MurmurHash3 algorithm and returns a BIGINT.

## Syntax

```Plain
MURMURHASH3_64(<expr>)
```

## Parameters

- `<expr>`: A primitive data type. Supports strings, integers, floating-point numbers, and more.

## Examples

```sql
SELECT murmurhash3_64('hello');
-- -8014657081559513573

SELECT murmurhash3_64(123);
-- 5808450433748234714

SELECT murmurhash3_64('world');
-- -5394866185914414384
```

## Related Documentation

- [MURMURHASH3_32](sql_functions/scalar_functions/hash_functions/murmurhash3_32.md) — 32-bit variant
- [GENERAL_MURMURHASH3](sql_functions/scalar_functions/hash_functions/general_murmurhash3.md)
