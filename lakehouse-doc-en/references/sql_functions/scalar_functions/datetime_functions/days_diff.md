# DAYS_DIFF

## Overview

Returns the number of days between two dates or timestamps. Result = first argument - second argument. Equivalent to `DATEDIFF(DAY, ...)` but with a more concise syntax.

## Syntax

```Plain
DAYS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, the minuend.
- `<start>`: DATE or TIMESTAMP type, the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT days_diff('2024-02-01', '2024-01-01');
-- 31

SELECT days_diff('2024-01-01', '2024-02-01');
-- -31

SELECT days_diff('2024-01-01 18:00:00', '2024-01-01 00:00:00');
-- 0

SELECT days_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](sql_functions/scalar_functions/datetime_functions/datediff.md) — general date difference function supporting multiple time units
- [HOURS_DIFF](sql_functions/scalar_functions/datetime_functions/hours_diff.md), [MINUTES_DIFF](sql_functions/scalar_functions/datetime_functions/minutes_diff.md), [SECONDS_DIFF](sql_functions/scalar_functions/datetime_functions/seconds_diff.md)
