# JSON_OBJECT_AGG

## Overview

Aggregates key-value pairs into a single JSON object and returns a STRING.

## Syntax

```Plain
JSON_OBJECT_AGG(<key>, <value>)
```

## Parameters

- `<key>`: STRING type, the key of the JSON object.
- `<value>`: Any type, the value of the JSON object.

## Examples

```sql
-- Basic usage
SELECT json_object_agg(k, v)
FROM (VALUES ('a',1),('b',2)) t(k,v);
-- {"a":1,"b":2}

-- With GROUP BY
SELECT grp, json_object_agg(k, v)
FROM (VALUES ('g1','a',1),('g1','b',2),('g2','c',3)) t(grp,k,v)
GROUP BY grp;
-- g1 | {"a":1,"b":2}
-- g2 | {"c":3}
```

## Related Documentation

- [JSON_ARRAY_AGG](sql_functions/aggregate_functions/json_array_agg.md) — aggregates into a JSON array
- [JSON_MERGE_AGG](sql_functions/aggregate_functions/json_merge_agg.md)
- [MAP_AGG](sql_functions/aggregate_functions/map_agg.md) — aggregates into a MAP type
