# POWER

## Overview

Computes `base` raised to the power of `exponent`. Returns a DOUBLE value.

## Syntax

```Plain
POWER(<base>, <exponent>)
```

## Parameters

- `<base>`: Numeric type. The base value.
- `<exponent>`: Numeric type. The exponent value.

## Examples

```sql
SELECT power(2, 10);
-- 1024

SELECT power(3.0, 2);
-- 9

-- Fractional exponent (square root)
SELECT power(4, 0.5);
-- 2
```

## Related Documentation

- [SQRT](sql_functions/scalar_functions/math_functions/sqrt.md) — square root (equivalent to `POWER(x, 0.5)`)
- [EXP](sql_functions/scalar_functions/math_functions/exp.md) — exponential function with base e
