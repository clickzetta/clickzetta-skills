# MAP

`MAP` is a key-value pair data type used to store dynamic attributes and name-to-value mappings. Unlike `STRUCT` (which has fixed field names), MAP keys are determined at runtime, making it suitable for scenarios where the number of fields is not fixed.

Type selection reference for complex types:

| Type | Structure | Suitable Scenarios |
|------|------|---------|
| `MAP<K,V>` | Key-value pairs, uniform key type | Dynamic attributes, configuration items, name-to-value mappings |
| `STRUCT<f:T,...>` | Named fields, varying types | Fixed-structure objects where field names are determined at table creation |
| `ARRAY<T>` | Ordered list, uniform element type | Tags, scores, ID lists |

## Syntax and Definition

**Type Declaration**

```Plain
MAP<keyType, valueType>
```

- `keyType`: Key type, supports basic types (`STRING`, `INT`, `BIGINT`, `DOUBLE`, etc.), does not support `ARRAY`, `MAP`, or `STRUCT`
- `valueType`: Value type, supports both basic types and complex types

**Construction Methods**

```SQL
-- MAP() constructor: keys and values alternate, the number of arguments must be even
MAP(key1, value1, key2, value2, ...)

-- map_from_arrays(): provide keys and values from two separate arrays
map_from_arrays(keys_array, values_array)
```

**Element Access**: Returns `NULL` when the key does not exist, no error is thrown:

```SQL
MAP('a', 1, 'b', 2)['a']   -- 1
MAP('a', 1, 'b', 2)['z']   -- NULL
```

## Creating Tables and Writing Data

```SQL
CREATE TABLE doc_map_demo (
    id    INT,
    attrs MAP<STRING, INT>,
    meta  MAP<STRING, STRING>
);

INSERT INTO doc_map_demo VALUES
    (1, MAP('age', 25, 'score', 90), MAP('dept', 'Eng', 'level', 'senior')),
    (2, MAP('age', 30, 'score', 85), MAP('dept', 'HR',  'level', 'junior')),
    (3, MAP('age', 28),              MAP('dept', 'Eng'));
```

Query basic information:

```SQL
SELECT id,
       attrs['age']   AS age,
       attrs['score'] AS score,
       size(attrs)    AS attr_count
FROM doc_map_demo
ORDER BY id;
```

| id | age | score | attr_count |
|----|-----|-------|------------|
| 1 | 25 | 90 | 2 |
| 2 | 30 | 85 | 2 |
| 3 | 28 | NULL | 1 |

## Common Functions

| Function | Description |
|------|------|
| `size(m)` / `cardinality(m)` | Number of key-value pairs |
| `map_keys(m)` | Returns all keys as an ARRAY |
| `map_values(m)` | Returns all values as an ARRAY |
| `element_at(m, key)` | Get value by key, equivalent to `m[key]` |
| `map_from_arrays(keys, values)` | Construct a MAP from two arrays |
| `map_concat(m1, m2, ...)` | Merge multiple MAPs; for duplicate keys, the **latter** value wins |
| `map_filter(m, (k,v) -> cond)` | Retain key-value pairs that satisfy the condition |
| `transform_values(m, (k,v) -> expr)` | Apply a function to each value, keys unchanged |
| `transform_keys(m, (k,v) -> expr)` | Apply a function to each key, values unchanged |

### map_from_arrays Example

```SQL
SELECT map_from_arrays(['a', 'b', 'c'], [1, 2, 3]) AS m;
-- Returns: {"a":1,"b":2,"c":3}
```

### map_concat Example

For duplicate keys, the latter value wins:

```SQL
SELECT map_concat(MAP('a', 1, 'b', 2), MAP('b', 99, 'c', 3)) AS merged;
-- Returns: {"a":1,"b":99,"c":3}
```

### Higher-Order Function Examples

```SQL
-- Retain key-value pairs where the value is greater than 1
SELECT map_filter(MAP('a', 1, 'b', 2, 'c', 3), (k, v) -> v > 1) AS filtered;
-- Returns: {"b":2,"c":3}

-- Multiply all values by 10
SELECT transform_values(MAP('a', 1, 'b', 2), (k, v) -> v * 10) AS scaled;
-- Returns: {"a":10,"b":20}

-- Convert keys to uppercase
SELECT transform_keys(MAP('a', 1, 'b', 2), (k, v) -> UPPER(k)) AS upper_keys;
-- Returns: {"A":1,"B":2}
```

## Aggregation and Expansion

### MAP_AGG — Rows to MAP

Aggregate key-value pairs from multiple rows into a single MAP:

```SQL
SELECT MAP_AGG(name, score) AS score_map
FROM (
    SELECT 'Alice' AS name, 95 AS score UNION ALL
    SELECT 'Bob',  87 UNION ALL
    SELECT 'Carol', 92
) t;
-- Returns: {"Alice":95,"Bob":87,"Carol":92}
```

Use with `GROUP BY` to aggregate by group:

```SQL
SELECT dept, MAP_AGG(name, score) AS scores
FROM (
    SELECT 'Alice' AS name, 95 AS score, 'Eng' AS dept UNION ALL
    SELECT 'Bob',  87, 'Eng' UNION ALL
    SELECT 'Carol', 92, 'HR'
) t
GROUP BY dept
ORDER BY dept;
```

| dept | scores |
|------|--------|
| Eng | {"Alice":95,"Bob":87} |
| HR | {"Carol":92} |

### EXPLODE — Expand MAP to Rows

`EXPLODE` expands a MAP into multiple rows, one row per key-value pair:

```SQL
SELECT id, k, v
FROM doc_map_demo
LATERAL VIEW EXPLODE(attrs) tmp AS k, v
ORDER BY id, k;
```

| id | k | v |
|----|---|---|
| 1 | age | 25 |
| 1 | score | 90 |
| 2 | age | 30 |
| 2 | score | 85 |
| 3 | age | 28 |

## Type Conversion

```SQL
-- Convert value type
SELECT CAST(MAP('a', 1, 'b', 2) AS MAP<STRING, BIGINT>) AS cast_map;
-- Returns: {"a":1,"b":2} (value type changed to bigint)
```

**Format difference between CAST to STRING and TO_JSON**:

```SQL
SELECT CAST(MAP('a', 1, 'b', 2) AS STRING);  -- {a -> 1, b -> 2} (not JSON format)
SELECT TO_JSON(MAP('a', 1, 'b', 2));          -- {"a":1,"b":2} (standard JSON)
```

> ⚠️ **Note**: The output format of MAP CAST to STRING is `{key -> value, ...}`, which is not JSON. Use `TO_JSON` if you need JSON format.

## NULL Handling

```SQL
-- NULL values are valid
SELECT MAP('a', NULL, 'b', 2) AS null_val;
-- Returns: {"a":null,"b":2}

-- Accessing a key with a NULL value returns NULL (indistinguishable from a missing key)
SELECT MAP('a', NULL, 'b', 2)['a'];  -- NULL
SELECT MAP('a', NULL, 'b', 2)['z'];  -- NULL
```

> ⚠️ **Note**: MAP keys cannot be NULL; a runtime error will be thrown: `the key of map cannot be null`.

## Notes

- MAP does not support the `=` comparison operator and cannot be used as `ORDER BY`, `GROUP BY`, or JOIN keys.
- All keys within the same MAP must be of the same type, and all values must also be of the same type.
- Neither `MAP()` nor `map_from_arrays()` automatically deduplicates duplicate keys. Behavior with duplicate keys: `map_keys` retains all duplicate keys, `m[key]` returns the first matching value, `TO_JSON` retains all duplicate keys (e.g., `{"k":1,"k":2}`). Ensure keys are unique before constructing a MAP.
- The order of arrays returned by `map_keys` and `map_values` is consistent with the insertion order, but is not guaranteed to be stable across versions.

## Related Documentation

- [ARRAY](../../../array.md): Ordered list of elements of the same type
- [STRUCT](../../../struct.md): Named structure with multiple fields and types
- [Data Type Conversion](../../../datatype-conversion.md): Complex type conversion rules
