# TOPN_ARRAY

## Overview

Returns the top N most frequently occurring values as an ARRAY, containing only the values themselves (no counts), ordered by frequency in descending order.

## Syntax

```Plain
TOPN_ARRAY(<expr>, <n>)
```

## Parameters

- `<expr>`: The column or expression to analyze. **Note: only string-compatible types (STRING/VARCHAR) are supported; numeric types are not.**
- `<n>`: INT type, the number of top values to return.

## Examples

```sql
-- Top 2 most frequent values (must be string type)
SELECT topn_array(v, 2)
FROM (VALUES ('a'),('a'),('a'),('b'),('b'),('c')) t(v);
-- ["a","b"]

-- Numeric types must be CAST to STRING first
SELECT topn_array(CAST(v AS STRING), 2)
FROM (VALUES (3),(3),(3),(2),(2),(1)) t(v);
-- ["3","2"]

-- With GROUP BY
SELECT k, topn_array(v, 2)
FROM (VALUES ('x','a'),('x','a'),('x','b'),('y','c'),('y','c'),('y','c')) t(k,v)
GROUP BY k;
-- x | ["a","b"]
-- y | ["c"]
```

## Related Documentation

- [TOPN](sql_functions/aggregate_functions/topn.md) — returns both values and their occurrence counts
- [APPROX_TOP_K](sql_functions/aggregate_functions/approx_top_k.md) — approximate top K, suitable for large datasets
