# ACOS

## Overview

Calculate the arc cosine of the input value, returning a value in radians in the range [0, π].

## Syntax

```Plain
ACOS(<expr>)
```

## Parameters

- `<expr>`: DOUBLE type, value range [-1, 1]; other numeric types are implicitly converted to DOUBLE. Returns NaN if out of range. Returns NULL if `<expr>` is NULL.

## Usage Examples

```sql
SELECT acos(-1);
-- 3.141592653589793

SELECT acos(0);
-- 1.5707963267948966

SELECT acos(1);
-- 0

SELECT acos(2);
-- NaN
```

## Related Documentation

- [ASIN](sql_functions/scalar_functions/math_functions/asin.md) — Arc sine
- [ATAN](sql_functions/scalar_functions/math_functions/atan.md) — Arc tangent
- [COS](sql_functions/scalar_functions/math_functions/cos.md) — Cosine
