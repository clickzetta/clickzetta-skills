# Array Explode and Flatten Guide

> **Scenario**: Expand nested data stored in arrays or JSON arrays into multiple rows, making it easier to aggregate, filter, and join for analysis.
>
> **Core functions**: `explode`, `explode_outer`, `posexplode`, `unnest`, `flatten`, `explode_json_array_string`, `explode_json_array_int`, `explode_json_array_json`.

---

## Quick Reference

| Function | Purpose | Empty Array Behavior | Use Case |
|---|---|---|---|
| `explode` | Expand array into multiple rows | Drops the row | Standard expansion when empty arrays don't need to be preserved |
| `explode_outer` | Expand array into multiple rows | Keeps a NULL row | When you need to preserve users/records with no data |
| `posexplode` | Expand array and return index | Drops the row | When you need to know each element's position in the original array |
| `unnest` | Expand multiple arrays in sync | Drops the row | Key-value pair arrays, multi-dimensional array expansion |
| `flatten` | Flatten a nested array | — | Convert a 2D array to a 1D array |
| `explode_json_array_string` | Expand a JSON string array | Drops the row | Tag arrays in JSON logs |
| `explode_json_array_int` | Expand a JSON integer array | Drops the row | ID lists in JSON |
| `explode_json_array_json` | Expand a JSON object array | Drops the row | Nested object arrays in JSON |

---

## Prerequisites

All examples in this guide use the following test data:

```sql
-- User tag table: each user has multiple tags stored as an array
CREATE TABLE user_tags (
  user_id BIGINT,
  tags ARRAY<VARCHAR>,
  scores ARRAY<INT>,
  metadata VARCHAR  -- JSON string: {"tags": ["a", "b"], "ids": [1, 2]}
);

INSERT INTO user_tags VALUES
  (1, ARRAY['vip', 'active', 'buyer'], ARRAY[100, 80, 90], '{"tags": ["a", "b"], "ids": [1, 2]}'),
  (2, ARRAY['new_user'], ARRAY[50], '{"tags": ["c"], "ids": [3]}'),
  (3, ARRAY[]::ARRAY<VARCHAR>, ARRAY[]::ARRAY<INT>, '{"tags": [], "ids": []}');
```

---

## Scenario 1: Basic Expansion (explode)

### Problem

Expand each user's tag array into multiple rows to count the number of users per tag.

### SQL Implementation

```sql
SELECT user_id, tag FROM user_tags
LATERAL VIEW explode(tags) t AS tag;
```

**Output**:

| user_id | tag |
|---------|-----|
| 1 | vip |
| 1 | active |
| 1 | buyer |
| 2 | new_user |

> ⚠️ **Note**: User 3's empty array causes that row to be dropped.

### Count Users per Tag

```sql
SELECT tag, COUNT(DISTINCT user_id) AS user_count
FROM user_tags
LATERAL VIEW explode(tags) t AS tag
GROUP BY tag
ORDER BY user_count DESC;
```

**Output**:

| tag | user_count |
|-----|------------|
| vip | 1 |
| active | 1 |
| buyer | 1 |
| new_user | 1 |

---

## Scenario 2: Preserving Empty Array Rows (explode_outer)

### Problem

You need to retain users with no tags for comparative analysis.

### SQL Implementation

```sql
SELECT user_id, tag FROM user_tags
LATERAL VIEW explode_outer(tags) t AS tag;
```

**Output**:

| user_id | tag |
|---------|-----|
| 1 | vip |
| 1 | active |
| 1 | buyer |
| 2 | new_user |
| 3 | NULL |

> **Key difference**: User 3 is preserved, with tag set to NULL.

---

## Scenario 3: Expansion with Index (posexplode)

### Problem

You need to know the position of each tag in the original array (e.g., for priority ordering).

### SQL Implementation

```sql
SELECT user_id, pos, tag FROM user_tags
LATERAL VIEW posexplode(tags) t AS pos, tag;
```

**Output**:

| user_id | pos | tag |
|---------|-----|-----|
| 1 | 0 | vip |
| 1 | 1 | active |
| 1 | 2 | buyer |
| 2 | 0 | new_user |

> **Index starts at 0**, reflecting each element's position in the original array.

### Joining Multiple Arrays

```sql
-- Tags and scores correspond by position
SELECT 
  u.user_id,
  t.tag,
  s.score
FROM user_tags u
LATERAL VIEW posexplode(u.tags) t AS pos, tag
LATERAL VIEW posexplode(u.scores) s AS spos, score
WHERE t.pos = s.spos;
```

**Output**:

| user_id | tag | score |
|---------|-----|-------|
| 1 | vip | 100 |
| 1 | active | 80 |
| 1 | buyer | 90 |
| 2 | new_user | 50 |

---

## Scenario 4: Synchronized Multi-Array Expansion (unnest)

### Problem

Expand key-value pair arrays in sync while preserving their correspondence.

### SQL Implementation

```sql
SELECT user_id, k, v FROM user_tags, unnest(tags, scores) AS t(k, v);
```

**Output**:

| user_id | k | v |
|---------|---|---|
| 1 | vip | 100 |
| 1 | active | 80 |
| 1 | buyer | 90 |
| 2 | new_user | 50 |

> **Advantage**: More concise than `posexplode` + `WHERE`; automatically pairs elements by position.

---

## Scenario 5: Flattening Nested Arrays (flatten)

### Problem

Flatten a 2D array (e.g., tags from multiple users merged together) into a 1D array.

### SQL Implementation

```sql
SELECT flatten(ARRAY[ARRAY['vip', 'active'], ARRAY['buyer'], ARRAY['new_user']]) AS all_tags;
```

**Output**:

| all_tags |
|----------|
| vip:active:buyer:new_user |

### Using flatten with explode

```sql
-- Flatten first, then explode
SELECT tag FROM (
  SELECT flatten(ARRAY[ARRAY['vip', 'active'], ARRAY['buyer']]) AS all_tags
)
LATERAL VIEW explode(all_tags) t AS tag;
```

**Output**:

| tag |
|-----|
| vip |
| active |
| buyer |

---

## Scenario 6: Expanding JSON Arrays

### Problem

Extract and expand array fields from a JSON string.

### SQL Implementation

```sql
-- You need to PARSE_JSON first to convert to a JSON type
WITH parsed AS (
  SELECT user_id, PARSE_JSON(metadata) AS meta FROM user_tags
)
SELECT user_id, tag FROM parsed
LATERAL VIEW explode_json_array_string(meta.tags) t AS tag;
```

**Output**:

| user_id | tag |
|---------|-----|
| 1 | a |
| 1 | b |
| 2 | c |

### Expanding a JSON Integer Array

```sql
WITH parsed AS (
  SELECT user_id, PARSE_JSON(metadata) AS meta FROM user_tags
)
SELECT user_id, id FROM parsed
LATERAL VIEW explode_json_array_int(meta.ids) t AS id;
```

**Output**:

| user_id | id |
|---------|----|
| 1 | 1 |
| 1 | 2 |
| 2 | 3 |

---

## Common Issues

### 1. Choosing between `explode` and `explode_outer`

```sql
-- explode: rows with empty arrays are dropped
SELECT user_id, tag FROM user_tags
LATERAL VIEW explode(tags) t AS tag;
-- User 3 is not in the result

-- explode_outer: rows with empty arrays are kept as NULL
SELECT user_id, tag FROM user_tags
LATERAL VIEW explode_outer(tags) t AS tag;
-- User 3 is in the result, with tag = NULL
```

### 2. `explode_json_array_*` requires a JSON type

```sql
-- Wrong: passing a string directly
LATERAL VIEW explode_json_array_string('["a", "b"]') t AS tag

-- Correct: use PARSE_JSON first
LATERAL VIEW explode_json_array_string(PARSE_JSON('["a", "b"]')) t AS tag
```

### 3. `unnest` requires arrays of equal length

```sql
-- If arrays have different lengths, the shorter one determines the row count; extra elements are ignored
SELECT unnest(ARRAY['a', 'b', 'c'], ARRAY[1, 2]) AS t(k, v);
-- Only 2 rows are expanded: (a,1), (b,2)
```

### 4. `posexplode` index starts at 0

```sql
-- Index is 0-based, not 1-based
SELECT pos, tag FROM user_tags
LATERAL VIEW posexplode(tags) t AS pos, tag;
-- pos = 0, 1, 2 ...
```

### 5. Cartesian product from multiple LATERAL VIEWs

```sql
-- Wrong: two explodes produce a Cartesian product
SELECT user_id, tag, score FROM user_tags
LATERAL VIEW explode(tags) t AS tag
LATERAL VIEW explode(scores) s AS score;
-- User 1 produces 3 x 3 = 9 rows

-- Correct: use unnest or posexplode + WHERE
SELECT user_id, k, v FROM user_tags, unnest(tags, scores) AS t(k, v);
```

---

## Performance Optimization Tips

| Scenario | Optimization Strategy |
|---|---|
| Expanding large arrays | Use `filter` to shrink the array before expanding |
| Aggregating after expansion | Apply `WHERE` filtering immediately after LATERAL VIEW |
| Expanding JSON arrays | Avoid complex JSON parsing before expansion |
| Multi-column expansion | Prefer `unnest` over multiple `posexplode` + `WHERE` |

```sql
-- Recommended: filter before expanding
SELECT user_id, tag FROM user_tags
LATERAL VIEW explode(filter(tags, t -> t != 'inactive')) t AS tag;

-- Not recommended: expand then filter (produces more intermediate rows)
SELECT user_id, tag FROM user_tags
LATERAL VIEW explode(tags) t AS tag
WHERE tag != 'inactive';
```

---

## Related Documentation

* [ARRAY Type](array.md)
* [JSON Type](json.md)
* [Table Functions Reference](table_function.md)
* [Higher-Order Functions Guide](high_order_function.md)
* [JSON Data Parsing](sql_json_parsing_guide.md)
