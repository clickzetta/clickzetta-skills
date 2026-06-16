# BITMAP_UNION

## Overview

Performs a union aggregation over a column of BITMAP objects and returns the merged BITMAP. Commonly used together with `BITMAP_TO_STRING` or `BITMAP_COUNT` to inspect the result.

## Syntax

```Plain
BITMAP_UNION(<bitmap_col>)
```

## Parameters

- `<bitmap_col>`: A column of BITMAP type.

## Examples

```sql
-- Merge multiple BITMAPs and inspect the result
SELECT bitmap_to_string(bitmap_union(b))
FROM (
  VALUES (to_bitmap(1)), (to_bitmap(2)), (to_bitmap(1))
) t(b);
-- 1,2

-- With GROUP BY
SELECT k, bitmap_to_string(bitmap_union(b))
FROM (
  VALUES ('x', to_bitmap(1)), ('x', to_bitmap(2)), ('y', to_bitmap(3))
) t(k, b)
GROUP BY k;
-- x | 1,2
-- y | 3
```

## Related Documentation

- [BITMAP_UNION_COUNT](bitmap_union_count.md) — returns the cardinality of the union directly
- [BITMAP_AGG](bitmap_agg.md) — aggregates an integer column into a BITMAP
- [TO_BITMAP](../scalar_functions/bitmap_functions/to_bitmap.md)
