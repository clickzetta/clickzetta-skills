# TOPN

## Overview

Returns the top N most frequently occurring values as a JSON object in the format `{"value": count, ...}`, ordered by frequency in descending order.

## Syntax

```Plain
TOPN(<expr>, <n>)
```

## Parameters

- `<expr>`: The column or expression to analyze. **Note: only string-compatible types (STRING/VARCHAR) are supported; numeric types are not.**
- `<n>`: INT type, the number of top values to return.

## Examples

```sql
-- Top 2 most frequent values (must be string type)
SELECT topn(v, 2)
FROM (VALUES ('a'),('a'),('a'),('b'),('b'),('c')) t(v);
-- {"a":3,"b":2}

-- Numeric types must be CAST to STRING first
SELECT topn(CAST(v AS STRING), 2)
FROM (VALUES (3),(3),(3),(2),(2),(1)) t(v);
-- {"3":3,"2":2}

-- With GROUP BY
SELECT k, topn(v, 2)
FROM (VALUES ('x','a'),('x','a'),('x','b'),('y','c'),('y','c'),('y','c')) t(k,v)
GROUP BY k;
-- x | {"a":2,"b":1}
-- y | {"c":3}
```

## Related Documentation

- [TOPN_ARRAY](topn_array.md) — returns only the top N value list without counts
- [APPROX_TOP_K](approx_top_k.md) — approximate top K, suitable for large datasets
