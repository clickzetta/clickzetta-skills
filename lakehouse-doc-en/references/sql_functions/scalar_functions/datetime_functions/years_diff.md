# YEARS_DIFF

## Overview

Returns the number of years between two dates or timestamps. The result equals the first argument minus the second argument.

## Syntax

```Plain
YEARS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, used as the minuend.
- `<start>`: DATE or TIMESTAMP type, used as the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT years_diff('2026-01-01', '2024-01-01');
-- 2

SELECT years_diff('2024-01-01', '2026-01-01');
-- -2

SELECT years_diff('2024-12-31', '2024-01-01');
-- 0

SELECT years_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](sql_functions/scalar_functions/datetime_functions/datediff.md) — general-purpose date difference function supporting multiple time units
- [MONTHS_DIFF](sql_functions/scalar_functions/datetime_functions/months_diff.md), [WEEKS_DIFF](sql_functions/scalar_functions/datetime_functions/weeks_diff.md), [DAYS_DIFF](sql_functions/scalar_functions/datetime_functions/days_diff.md)
