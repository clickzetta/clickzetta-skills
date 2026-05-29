# MINUTES_DIFF

## Overview

Returns the number of minutes between two timestamps. Result = first argument - second argument (truncated toward zero).

## Syntax

```Plain
MINUTES_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, the minuend.
- `<start>`: DATE or TIMESTAMP type, the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT minutes_diff('2024-01-01 01:30:00', '2024-01-01 00:00:00');
-- 90

SELECT minutes_diff('2024-01-01 00:00:00', '2024-01-01 01:30:00');
-- -90

SELECT minutes_diff('2024-01-02', '2024-01-01');
-- 1440

SELECT minutes_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](sql_functions/scalar_functions/datetime_functions/datediff.md) — general date difference function supporting multiple time units
- [DAYS_DIFF](sql_functions/scalar_functions/datetime_functions/days_diff.md), [HOURS_DIFF](sql_functions/scalar_functions/datetime_functions/hours_diff.md), [SECONDS_DIFF](sql_functions/scalar_functions/datetime_functions/seconds_diff.md)
