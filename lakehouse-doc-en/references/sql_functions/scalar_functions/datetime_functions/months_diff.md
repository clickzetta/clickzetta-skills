# MONTHS_DIFF

## Overview

Returns the number of months between two dates or timestamps. Result = first argument - second argument.

## Syntax

```Plain
MONTHS_DIFF(<end>, <start>)
```

## Parameters

- `<end>`: DATE or TIMESTAMP type, the minuend.
- `<start>`: DATE or TIMESTAMP type, the subtrahend.

Returns NULL if either argument is NULL.

## Examples

```sql
SELECT months_diff('2025-03-01', '2024-01-01');
-- 14

SELECT months_diff('2024-01-01', '2025-03-01');
-- -14

SELECT months_diff('2024-02-01', '2024-01-01');
-- 1

SELECT months_diff(NULL, '2024-01-01');
-- NULL
```

## Related Documentation

- [DATEDIFF](datediff.md) — general date difference function supporting multiple time units
- [WEEKS_DIFF](weeks_diff.md), [YEARS_DIFF](years_diff.md), [DAYS_DIFF](days_diff.md)
