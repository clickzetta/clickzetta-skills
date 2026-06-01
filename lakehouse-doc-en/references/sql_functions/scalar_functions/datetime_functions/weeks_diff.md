# WEEKS_DIFF

## Overview

Returns the number of complete weeks between two dates or timestamps. The result equals the first argument minus the second argument, truncated toward zero (no rounding).

## Syntax

```Plain
WEEKS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, used as the minuend.
- `<start>`: DATE or TIMESTAMP type, used as the subtrahend.

Returns NULL if either argument is NULL. Any remaining days that do not form a complete week are truncated, not rounded.

## Examples

```sql
SELECT weeks_diff('2024-01-14', '2024-01-01');
-- 1

SELECT weeks_diff('2024-01-07', '2024-01-01');
-- 0

SELECT weeks_diff('2024-01-01', '2024-01-14');
-- -1

SELECT weeks_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](datediff.md) — general-purpose date difference function supporting multiple time units
- [DAYS_DIFF](days_diff.md), [MONTHS_DIFF](months_diff.md), [YEARS_DIFF](years_diff.md)
