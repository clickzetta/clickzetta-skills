# NVL2

## Overview

Returns different values depending on whether the first argument is NULL: returns the second argument when the first is not NULL, and returns the third argument when the first is NULL.

## Syntax

```Plain
NVL2(<expr>, <value_if_not_null>, <value_if_null>)
```

## Parameters

- `<expr>`: The expression to test for NULL.
- `<value_if_not_null>`: The value returned when `<expr>` is not NULL.
- `<value_if_null>`: The value returned when `<expr>` is NULL.

Note: `NVL2` only tests whether the first argument is NULL, not whether it is truthy. Non-NULL values such as `0` and empty strings all take the second argument path.

## Examples

```sql
-- Returns the second argument when not NULL
SELECT nvl2(1, 'not null', 'null result');
-- not null

-- Returns the third argument when NULL
SELECT nvl2(NULL, 'not null', 'null result');
-- null result

-- 0 is a non-NULL value, so the second argument is returned
SELECT nvl2(0, 'not null', 'null result');
-- not null
```

## Related Documentation

- [NVL](sql_functions/scalar_functions/conditional_functions/nvl.md) — two-argument version that returns a default value when NULL
- [NULLIF](sql_functions/scalar_functions/conditional_functions/nullif.md)
- [COALESCE](sql_functions/scalar_functions/conditional_functions/coalesce.md)
