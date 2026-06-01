# ARRAY

`ARRAY` is an ordered sequence of same-type elements that supports index access, slicing, set operations, and higher-order functions. It is well-suited for storing tag lists, score sequences, log paths, and similar data.

Type selection reference for complex types:

| Type | Structure | Best for |
|------|-----------|---------|
| `ARRAY<T>` | Ordered list, uniform element type | Tags, scores, ID lists |
| `MAP<K,V>` | Key-value pairs, uniform key type | Dynamic attributes, name-to-value mappings |
| `STRUCT<f:T,...>` | Named fields, heterogeneous types | Fixed-structure objects such as user information |

## Syntax and Definition

**Type declaration**

```Plain
ARRAY<elementType>
```

**Construction methods**

```SQL
-- Square bracket literal (recommended)
[value1, value2, ...]

-- ARRAY() constructor
ARRAY(value1, value2, ...)
```

**Literal type inference**: integer literals infer to `array<int>`, decimals infer to `array<decimal(p,s)>`:

```SQL
SELECT typeof([1, 2, 3]),     -- array<int>
       typeof([1.5, 2.5]),    -- array<decimal(2,1)>
       typeof(['a', 'b']);    -- array<string>
```

**Element access**: index starts at `0`; out-of-bounds or negative indices return `NULL`:

```SQL
SELECT [10, 20, 30][0],   -- 10
       [10, 20, 30][2],   -- 30
       [10, 20, 30][-1],  -- NULL (negative not supported)
       [10, 20, 30][5];   -- NULL (out of bounds)
```

## Creating Tables and Writing Data

```SQL
CREATE TABLE doc_array_demo (
    id     INT,
    tags   ARRAY<STRING>,
    scores ARRAY<INT>
);

INSERT INTO doc_array_demo VALUES
    (1, ['read', 'write', 'admin'], [95, 87, 92]),
    (2, ['read'],                   [78]),
    (3, ['read', 'write'],          [88, NULL, 91]);
```

Querying basic information:

```SQL
SELECT id, tags, tags[0] AS first_tag, size(tags) AS tag_count
FROM doc_array_demo
ORDER BY id;
```

| id | tags | first_tag | tag_count |
|----|------|-----------|-----------|
| 1 | ["read","write","admin"] | read | 3 |
| 2 | ["read"] | read | 1 |
| 3 | ["read","write"] | read | 2 |

## Common Functions

| Function | Description | Example Result |
|----------|-------------|---------------|
| `size(arr)` / `cardinality(arr)` | Number of elements | `size([1,2,3])` → `3` |
| `array_contains(arr, val)` | Whether a value is present | `array_contains([1,2,3], 2)` → `true` |
| `array_position(arr, val)` | First occurrence position (**1-based**); returns `0` if not found | `array_position([10,20,30,20], 20)` → `2` |
| `array_append(arr, val)` | Append to end | `array_append([1,2], 3)` → `[1,2,3]` |
| `array_prepend(arr, val)` | Prepend to start | `array_prepend([1,2], 0)` → `[0,1,2]` |
| `array_remove(arr, val)` | Remove all matching elements (returns NULL when val is NULL) | `array_remove([1,2,3,2], 2)` → `[1,3]` |
| `array_distinct(arr)` | Deduplicate, preserving first-occurrence order | `array_distinct([1,2,2,3])` → `[1,2,3]` |
| `array_sort(arr)` | Sort ascending, NULLs at end | `array_sort([3,1,NULL,2])` → `[1,2,3,null]` |
| `sort_array(arr, asc)` | Specify ascending/descending; NULLs always at end | `sort_array([3,1,2], false)` → `[3,2,1]` |
| `array_max(arr)` | Maximum value (ignores NULL) | `array_max([3,1,5,2])` → `5` |
| `array_min(arr)` | Minimum value (ignores NULL) | `array_min([3,1,5,2])` → `1` |
| `array_union(arr1, arr2)` | Merge and deduplicate | `array_union([1,2], [2,3])` → `[1,2,3]` |
| `array_intersect(arr1, arr2)` | Intersection | `array_intersect([1,2,3], [2,3,4])` → `[2,3]` |
| `array_except(arr1, arr2)` | Difference (elements in arr1 but not arr2) | `array_except([1,2,3], [2])` → `[1,3]` |
| `flatten(arr)` | Flatten one level of nesting | `flatten([[1,2],[3,4]])` → `[1,2,3,4]` |
| `slice(arr, start, length)` | Slice; **start is 1-based**, supports negative to count from end | `slice([10,20,30,40], 2, 2)` → `[20,30]` |
| `arrays_zip(arr1, arr2, ...)` | Merge element-by-element into a STRUCT array | See example below |
| `array_join(arr, sep)` | Convert elements to strings and concatenate | `array_join([1,2,3], ',')` → `'1,2,3'` |
| `array_join(arr, sep, nullReplacement)` | Fill NULL elements with replacement string | `array_join(['a',NULL,'c'], ',', 'N/A')` → `'a,N/A,c'` |

### Slice Example

```SQL
SELECT slice([10, 20, 30, 40, 50], 2, 3) AS mid,   -- [20,30,40]
       slice([10, 20, 30, 40, 50], -2, 2) AS tail; -- [30,40]
```

> ⚠️ **Note**: `slice` start position is **1-based**, which is inconsistent with index access (0-based).

### arrays_zip Example

`arrays_zip` merges multiple arrays element-by-element into a STRUCT array; field names are auto-generated as `"0"`, `"1"`, `"2"`:

```SQL
SELECT arrays_zip([1, 2, 3], ['a', 'b', 'c']) AS zipped;
-- Returns: [{"0":1,"1":"a"},{"0":2,"1":"b"},{"0":3,"1":"c"}]
```

## Higher-Order Functions

`TRANSFORM` and `FILTER` support lambda expressions for element-by-element processing:

```SQL
-- TRANSFORM: apply a function to each element
SELECT TRANSFORM([1, 2, 3, 4, 5], x -> x * x) AS squares;
-- Returns: [1,4,9,16,25]

-- FILTER: keep elements that satisfy a condition
SELECT FILTER([1, 2, 3, 4, 5, 6], x -> x % 2 = 0) AS evens;
-- Returns: [2,4,6]
```

Combined example — filter then transform:

```SQL
SELECT TRANSFORM(
  FILTER([1, 2, 3, 4, 5, 6], x -> x % 2 = 0),
  x -> x * 10
) AS result;
-- Returns: [20,40,60]
```

## Aggregation and Expansion

### ARRAY_AGG — Rows to Array

Aggregate multiple row values into a single array; supports `ORDER BY` and `DISTINCT` (cannot be used together):

```SQL
SELECT dept, ARRAY_AGG(name ORDER BY name) AS members
FROM (
    SELECT 'Alice' AS name, 'Eng' AS dept UNION ALL
    SELECT 'Bob',  'Eng' UNION ALL
    SELECT 'Carol','HR'  UNION ALL
    SELECT 'Dave', 'HR'
) t
GROUP BY dept
ORDER BY dept;
```

| dept | members |
|------|---------|
| Eng | ["Alice","Bob"] |
| HR | ["Carol","Dave"] |

```SQL
-- DISTINCT deduplication (cannot be combined with ORDER BY)
SELECT ARRAY_AGG(DISTINCT x) AS deduped
FROM (SELECT 1 AS x UNION ALL SELECT 2 UNION ALL SELECT 1 UNION ALL SELECT 3) t;
-- Returns: [1,2,3]
```

### EXPLODE — Array to Rows

`EXPLODE` expands an array into multiple rows; use with `LATERAL VIEW` to retain other fields from the original row:

```SQL
SELECT id, tag
FROM doc_array_demo
LATERAL VIEW EXPLODE(tags) tmp AS tag
ORDER BY id, tag;
```

| id | tag |
|----|-----|
| 1 | admin |
| 1 | read |
| 1 | write |
| 2 | read |
| 3 | read |
| 3 | write |

`POSEXPLODE` additionally returns the element's position in the array (0-based):

```SQL
SELECT id, pos, tag
FROM doc_array_demo
LATERAL VIEW POSEXPLODE(tags) tmp AS pos, tag
WHERE id = 1;
```

| id | pos | tag |
|----|-----|-----|
| 1 | 0 | read |
| 1 | 1 | write |
| 1 | 2 | admin |

## Type Conversion

```SQL
-- Convert element type using angle-bracket syntax to specify target type
SELECT CAST([1, 2, 3] AS ARRAY<BIGINT>);   -- [1,2,3] (bigint)
SELECT CAST([1, 2, 3] AS ARRAY<STRING>);   -- ["1","2","3"]

-- Nested array type conversion (element types converted to string representation of target type)
SELECT CAST(ARRAY(ARRAY(1, 2), ARRAY(3, 4)) AS ARRAY<ARRAY<BIGINT>>);
-- Returns: [["1","2"],["3","4"]]
```

**Difference between CAST to STRING and TO_JSON**:

```SQL
SELECT CAST([1, 2, 3] AS STRING);  -- [1, 2, 3] (space after comma)
SELECT TO_JSON([1, 2, 3]);         -- [1,2,3] (no space, standard JSON)
```

> ⚠️ **Note**: The string `'[1,2,3]'` cannot be directly CAST to ARRAY; it must be processed with functions like `SPLIT` before constructing.

## NULL Handling

```SQL
-- ARRAY can contain NULL elements
SELECT [1, 2, NULL, 3];
-- Returns: [1,2,null,3]

-- array_contains searching for NULL returns NULL, not true or false
SELECT array_contains([1, 2, NULL], NULL);
-- Returns: null

-- array_remove removing NULL returns NULL (not the array with NULL elements removed)
SELECT array_remove([1, NULL, 2], NULL);
-- Returns: null

-- array_distinct keeps one NULL
SELECT array_distinct([1, NULL, 2, NULL, 3]);
-- Returns: [1,null,2,3]
```

## Notes

- Index starts at `0`; `slice` start position starts at `1`. These are inconsistent — be careful to distinguish them.
- ARRAY supports `=` equality comparison but does not support `>`, `<`, or other ordering comparisons, and cannot be used as a GROUP BY key or JOIN key.
- `TRANSFORM` and `FILTER` are lambda higher-order functions; `AGGREGATE`/`REDUCE` are not yet supported.
- `ARRAY_AGG`'s `DISTINCT` and `ORDER BY` cannot be used together.
- `array_position` returns a 1-based position; returns `0` when not found, which differs from index access (0-based).

## Related Documents

- [MAP](map.md): key-value pair type
- [STRUCT](struct.md): named structure with multiple fields and types
- [Data Type Conversion](datatype-conversion.md): complex type conversion rules
