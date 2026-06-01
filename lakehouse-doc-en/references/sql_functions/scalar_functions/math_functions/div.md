# DIV

## Overview

Performs integer division on two integers, returning the integer part of the quotient (truncating the decimal). Equivalent to `FLOOR(dividend / divisor)`, but only accepts integer inputs.

## Syntax

```Plain
<dividend> DIV <divisor>
```

## Parameters

- `<dividend>`: INT or BIGINT type, the dividend.
- `<divisor>`: INT or BIGINT type, the divisor. Returns NULL when `<divisor>` is 0.

## Usage Examples

```sql
SELECT 10 DIV 3;
-- 3

SELECT -10 DIV 3;
-- -3

SELECT 10 DIV 0;
-- NULL
```

## Related Documentation

- [MOD](mod.md) — Modulo operation
