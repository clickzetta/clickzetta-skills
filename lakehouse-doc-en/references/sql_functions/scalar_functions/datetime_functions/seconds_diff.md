# SECONDS_DIFF

## Overview

Returns the number of seconds between two timestamps. The result equals the first argument minus the second argument.

## Syntax

```Plain
SECONDS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, used as the minuend.
- `<start>`: DATE or TIMESTAMP type, used as the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT seconds_diff('2024-01-01 00:01:00', '2024-01-01 00:00:00');
-- 60

SELECT seconds_diff('2024-01-01 00:00:00', '2024-01-01 00:01:00');
-- -60

SELECT seconds_diff('2024-01-02', '2024-01-01');
-- 86400

SELECT seconds_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](sql_functions/scalar_functions/datetime_functions/datediff.md) — general-purpose date difference function supporting multiple time units
- [MILLISECONDS_DIFF](sql_functions/scalar_functions/datetime_functions/milliseconds_diff.md), [MINUTES_DIFF](sql_functions/scalar_functions/datetime_functions/minutes_diff.md), [HOURS_DIFF](sql_functions/scalar_functions/datetime_functions/hours_diff.md)
