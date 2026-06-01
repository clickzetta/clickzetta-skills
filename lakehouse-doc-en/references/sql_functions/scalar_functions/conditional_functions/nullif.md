# NULLIF

## Overview

Compares two expressions and returns NULL if they are equal; otherwise returns the value of the first expression. Commonly used to avoid division-by-zero errors or to replace a specific value with NULL.

## Syntax

```Plain
NULLIF(<expr1>, <expr2>)
```

## Parameters

- `<expr1>`: The first expression; this is the value that gets replaced with NULL when the two expressions are equal.
- `<expr2>`: The second expression, used for comparison.

The two parameters must have compatible types.

## Examples

```sql
-- Returns NULL when equal
SELECT nullif(1, 1);
-- NULL

-- Returns the first parameter when not equal
SELECT nullif(1, 2);
-- 1

-- String comparison
SELECT nullif('a', 'b');
-- a

-- Avoid division by zero: returns NULL when the denominator is 0
SELECT 10 / nullif(0, 0);
-- NULL
```

## Related Documentation

- [NVL](nvl.md) — NULL replacement function
- [NVL2](nvl2.md)
- [COALESCE](coalesce.md)
