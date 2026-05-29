# ARRAY_AGG

## Overview

Aggregates a set of values into an ARRAY. Supports DISTINCT deduplication and WITHIN GROUP ORDER BY ordering. Functionally identical to `COLLECT_LIST`; `ARRAY_AGG` is the SQL-standard spelling.

## Syntax

```Plain
ARRAY_AGG([DISTINCT] <expr> [WITHIN GROUP (ORDER BY <expr> [ASC|DESC])])
```

## Parameters

- `<expr>`: The column or expression to aggregate.
- `DISTINCT`: Deduplicate values before aggregating.
- `WITHIN GROUP (ORDER BY ...)`: Specify the ordering of elements in the resulting array.

> ⚠️ **Note:** DISTINCT and ORDER BY cannot be used together.

## Examples

```sql
-- Basic usage
SELECT array_agg(v)
FROM (VALUES (1),(2),(3)) t(v);
-- [1,2,3]

-- With ordering
SELECT array_agg(v WITHIN GROUP (ORDER BY v DESC))
FROM (VALUES (3),(1),(2)) t(v);
-- [3,2,1]

-- DISTINCT deduplication
SELECT array_agg(DISTINCT v)
FROM (VALUES (1),(2),(1),(3)) t(v);
-- [1,2,3]

-- With GROUP BY
SELECT k, array_agg(v)
FROM (VALUES ('x',1),('x',2),('y',3)) t(k,v)
GROUP BY k;
-- x | [1,2]
-- y | [3]
```

## Related Documentation

- [COLLECT_LIST](sql_functions/aggregate_functions/collect_list.md) — alias function with identical behavior
- [JSON_ARRAY_AGG](sql_functions/aggregate_functions/json_array_agg.md) — aggregates into a JSON array string
