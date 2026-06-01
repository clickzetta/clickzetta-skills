# HOURS_DIFF

## Overview

Returns the number of hours between two timestamps. Result = first argument - second argument (truncated toward zero).

## Syntax

```Plain
HOURS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, the minuend.
- `<start>`: DATE or TIMESTAMP type, the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT hours_diff('2024-01-01 23:00:00', '2024-01-01 00:00:00');
-- 23

SELECT hours_diff('2024-01-01 00:00:00', '2024-01-01 23:00:00');
-- -23

SELECT hours_diff('2024-01-02', '2024-01-01');
-- 24

SELECT hours_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](datediff.md) — general date difference function supporting multiple time units
- [DAYS_DIFF](days_diff.md), [MINUTES_DIFF](minutes_diff.md), [SECONDS_DIFF](seconds_diff.md)
