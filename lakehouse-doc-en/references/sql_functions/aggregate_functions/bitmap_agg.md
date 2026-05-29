# BITMAP_AGG

## Overview

Aggregates a column of integer values into a single BITMAP object. Equivalent to calling `TO_BITMAP` on each value and then performing `BITMAP_UNION`. The return type is BITMAP (binary).

## Syntax

```Plain
BITMAP_AGG(<expr>)
```

## Parameters

- `<expr>`: A BIGINT expression or any expression that can be implicitly cast to an integer.

## Examples

```sql
-- Aggregate into a BITMAP and inspect the contents with bitmap_to_string
SELECT bitmap_to_string(bitmap_agg(v))
FROM (VALUES (1),(2),(3),(2)) t(v);
-- 1,2,3
```

## Related Documentation

- [BITMAP_UNION](sql_functions/aggregate_functions/bitmap_union.md) — performs a union aggregation over multiple BITMAP objects
- [TO_BITMAP](sql_functions/scalar_functions/bitmap_functions/to_bitmap.md)
- [BITMAP_TO_STRING](sql_functions/scalar_functions/bitmap_functions/bitmap_to_string.md)
