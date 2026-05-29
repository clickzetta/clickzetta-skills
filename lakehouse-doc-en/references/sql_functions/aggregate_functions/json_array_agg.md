# JSON_ARRAY_AGG

## Overview

Aggregates a set of values into a JSON array and returns a STRING. Supports DISTINCT deduplication and ORDER BY ordering.

## Syntax

```Plain
JSON_ARRAY_AGG([DISTINCT] <expr> [WITHIN GROUP (ORDER BY <expr> [ASC|DESC])])
```

## Parameters

- `<expr>`: The column or expression to aggregate.
- `DISTINCT`: Deduplicate values before aggregating. The order of results is not guaranteed.
- `WITHIN GROUP (ORDER BY ...)`: Specify the ordering of elements in the resulting array.

## Examples

```sql
-- Basic usage
SELECT json_array_agg(v)
FROM (VALUES (1),(2),(3)) t(v);
-- [1,2,3]

-- With ordering
SELECT json_array_agg(v WITHIN GROUP (ORDER BY v DESC))
FROM (VALUES (3),(1),(2)) t(v);
-- [3,2,1]

-- DISTINCT deduplication (result order is not guaranteed)
SELECT json_array_agg(DISTINCT v)
FROM (VALUES (1),(2),(1),(3)) t(v);
-- [2,1,3]

-- With GROUP BY
SELECT k, json_array_agg(v)
FROM (VALUES ('x',1),('x',2),('y',3)) t(k,v)
GROUP BY k;
-- x | [1,2]
-- y | [3]
```

## Related Documentation

- [JSON_OBJECT_AGG](sql_functions/aggregate_functions/json_object_agg.md) — aggregates into a JSON object
- [COLLECT_LIST](sql_functions/aggregate_functions/collect_list.md) — aggregates into an ARRAY type
- [JSON_ARRAY_GET](sql_functions/scalar_functions/json_functions/json_array_get.md)
