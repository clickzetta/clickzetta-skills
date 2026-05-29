# BITMAP_UNION_COUNT

## Overview

Performs a union aggregation over a column of BITMAP objects and returns the cardinality (number of distinct elements) of the union directly. Equivalent to `BITMAP_COUNT(BITMAP_UNION(...))`, but more concise.

## Syntax

```Plain
BITMAP_UNION_COUNT(<bitmap_col>)
```

## Parameters

- `<bitmap_col>`: A column of BITMAP type.

## Examples

```sql
-- Count distinct elements in the union
SELECT bitmap_union_count(b)
FROM (
  VALUES (to_bitmap(1)), (to_bitmap(2)), (to_bitmap(1))
) t(b);
-- 2

-- With GROUP BY
SELECT k, bitmap_union_count(b)
FROM (
  VALUES ('x', to_bitmap(1)), ('x', to_bitmap(2)), ('y', to_bitmap(3))
) t(k, b)
GROUP BY k;
-- x | 2
-- y | 1
```

## Related Documentation

- [BITMAP_UNION](sql_functions/aggregate_functions/bitmap_union.md) — returns a BITMAP object instead of the cardinality
- [BITMAP_AGG](sql_functions/aggregate_functions/bitmap_agg.md)
