# MILLISECONDS_DIFF

## Overview

Returns the number of milliseconds between two timestamps. Result = first argument - second argument.

## Syntax

```Plain
MILLISECONDS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, the minuend.
- `<start>`: DATE or TIMESTAMP type, the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT milliseconds_diff('2024-01-01 00:00:01.500', '2024-01-01 00:00:00');
-- 1500

SELECT milliseconds_diff('2024-01-01 00:00:00', '2024-01-01 00:00:01.500');
-- -1500

SELECT milliseconds_diff('2024-01-02', '2024-01-01');
-- 86400000

SELECT milliseconds_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](sql_functions/scalar_functions/datetime_functions/datediff.md) — general date difference function supporting multiple time units
- [SECONDS_DIFF](sql_functions/scalar_functions/datetime_functions/seconds_diff.md), [MINUTES_DIFF](sql_functions/scalar_functions/datetime_functions/minutes_diff.md)
