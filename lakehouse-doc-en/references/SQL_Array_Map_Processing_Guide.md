# Array and Map Processing Guide

> **Scenario**: Process Array and Map type data directly in SQL — filter, transform, and aggregate without exploding into multiple rows.
>
> **Core techniques**: Lambda expressions `(x) -> expr`, `(k, v) -> expr`, `(acc, x) -> expr`, used with functions such as `transform`, `filter`, `exists`, `forall`, `array_aggregate`, `zip_with`, `map_filter`, and more.

---

## Quick Reference

| Function | Purpose | Input | Output |
|---|---|---|---|
| `transform` | Transform each array element | Array + lambda | New array |
| `filter` | Filter array elements by condition | Array + lambda | Sub-array |
| `exists` | Check if any element satisfies a condition | Array + lambda | BOOLEAN |
| `forall` | Check if all elements satisfy a condition | Array + lambda | BOOLEAN |
| `array_aggregate` | Aggregate within an array | Array + initial value + lambda | Any type |
| `zip_with` | Pair two arrays element-by-element | Array1 + Array2 + lambda | New array |
| `map_filter` | Filter Map entries by condition | Map + lambda | New Map |
| `transform_values` | Transform Map values | Map + lambda | New Map |
| `transform_keys` | Transform Map keys | Map + lambda | New Map |
| `map_zip_with` | Merge two Maps | Map1 + Map2 + lambda | New Map |

---

## Prerequisites

All examples in this guide use the following test data:

```sql
-- User event log table: each user has multiple events stored as arrays
CREATE TABLE user_events (
  user_id BIGINT,
  event_types ARRAY<VARCHAR>,   -- event type array: ['view', 'click', 'purchase']
  durations ARRAY<INT>,         -- corresponding event duration array: [10, 25, 100]
  tags ARRAY<VARCHAR>           -- user tag array: ['vip', 'new_user']
);

INSERT INTO user_events VALUES
  (1, ARRAY['view', 'click', 'view', 'purchase', 'view'], ARRAY[10, 25, 15, 100, 8], ARRAY['vip', 'active']),
  (2, ARRAY['click', 'view', 'click'], ARRAY[5, 30, 12], ARRAY['new_user']),
  (3, ARRAY['view', 'view', 'view'], ARRAY[20, 25, 15], ARRAY['vip', 'inactive']);
```

> ⚠️ **Note**: In Singdata Lakehouse, arrays are displayed as colon-separated strings (e.g., `10:25:15`), not in JSON array format.

---

## Scenario 1: Filtering Event Arrays from Logs

### Problem

Filter events of a specific type from the event type array and retrieve the corresponding durations.

### SQL Implementation

```sql
SELECT 
  user_id,
  event_types,
  durations,
  -- Filter durations for 'view' events (lambda supports an index parameter, 1-based)
  filter(durations, (d, i) -> event_types[i] = 'view') AS view_durations,
  -- Filter durations for 'purchase' events
  filter(durations, (d, i) -> event_types[i] = 'purchase') AS purchase_durations
FROM user_events;
```

**Output**:

| user_id | event_types | durations | view_durations | purchase_durations |
|---------|-------------|-----------|----------------|-------------------|
| 1 | view:click:view:purchase:view | 10:25:15:100:8 | 10:15:8 | 100 |
| 2 | click:view:click | 5:30:12 | 30 | — |
| 3 | view:view:view | 20:25:15 | 20:25:15 | — |

### Key Notes

- The `filter` lambda supports two parameters: `(element, index)`, where the index starts at **1**
- You can correlate multiple arrays using the index (e.g., `event_types[i]` paired with `durations[i]`)

---

## Scenario 2: Conditional Checks (exists / forall)

### Problem

Determine whether a user has performed a specific action, or whether all actions match a certain pattern.

### SQL Implementation

```sql
SELECT 
  user_id,
  event_types,
  -- Whether there is a 'purchase' event
  exists(event_types, t -> t = 'purchase') AS has_purchase,
  -- Whether all events are 'view'
  forall(event_types, t -> t = 'view') AS all_views,
  -- Whether any event has a duration greater than 20
  exists(durations, d -> d > 20) AS has_long_session
FROM user_events;
```

**Output**:

| user_id | event_types | has_purchase | all_views | has_long_session |
|---------|-------------|--------------|-----------|------------------|
| 1 | view:click:view:purchase:view | true | false | true |
| 2 | click:view:click | false | false | true |
| 3 | view:view:view | false | true | true |

---

## Scenario 3: Transforming Array Elements (transform)

### Problem

Apply a uniform transformation to every element in an array, such as unit conversion or formatting.

### SQL Implementation

```sql
SELECT 
  user_id,
  durations,
  -- Convert milliseconds to seconds (assuming raw data is in milliseconds)
  transform(durations, d -> d * 1000) AS durations_ms,
  -- Classify durations into levels
  transform(durations, d -> 
    CASE 
      WHEN d >= 30 THEN 'long'
      WHEN d >= 10 THEN 'medium'
      ELSE 'short'
    END
  ) AS duration_levels
FROM user_events;
```

**Output**:

| user_id | durations | durations_ms | duration_levels |
|---------|-----------|--------------|-----------------|
| 1 | 10:25:15:100:8 | 10000:25000:15000:100000:8000 | medium:long:medium:long:short |
| 2 | 5:30:12 | 5000:30000:12000 | short:long:medium |
| 3 | 20:25:15 | 20000:25000:15000 | medium:long:medium |

---

## Scenario 4: Aggregating Within an Array (array_aggregate)

### Problem

Perform aggregation calculations within an array — such as sum, maximum, or count — without exploding into multiple rows.

### SQL Implementation

```sql
SELECT 
  user_id,
  durations,
  -- Total duration
  array_aggregate(durations, 0, (acc, x) -> acc + x) AS total_duration,
  -- Maximum duration
  array_aggregate(durations, 0, (acc, x) -> CASE WHEN x > acc THEN x ELSE acc END) AS max_duration,
  -- Event count (array length)
  array_aggregate(durations, 0, (acc, x) -> acc + 1) AS event_count
FROM user_events;
```

**Output**:

| user_id | durations | total_duration | max_duration | event_count |
|---------|-----------|----------------|--------------|-------------|
| 1 | 10:25:15:100:8 | 158 | 100 | 5 |
| 2 | 5:30:12 | 47 | 30 | 3 |
| 3 | 20:25:15 | 60 | 25 | 3 |

### Key Notes

- The three-parameter form `array_aggregate(array, initial, (acc, x) -> expr)` is the most stable
- The four-parameter form (with a finish lambda) may have codegen limitations for string operations; numeric aggregation is recommended

---

## Scenario 5: Pairing Two Arrays (zip_with)

### Problem

Pair two equal-length arrays by position and perform element-wise calculations.

### SQL Implementation

```sql
SELECT 
  user_id,
  event_types,
  durations,
  -- Calculate the "value per unit duration" for each event
  -- (assuming purchase = 100, click = 10, view = 1)
  zip_with(
    event_types, 
    durations, 
    (t, d) -> d * CASE t WHEN 'purchase' THEN 100 WHEN 'click' THEN 10 ELSE 1 END
  ) AS event_values
FROM user_events;
```

**Output**:

| user_id | event_values |
|---------|--------------|
| 1 | 10:250:15:10000:8 |
| 2 | 50:30:120 |
| 3 | 20:25:15 |

---

## Scenario 6: Filtering and Transforming Map Data

### Problem

Process key-value pair data (such as user profile tags or configuration parameters) by filtering or transforming based on conditions.

### SQL Implementation

```sql
-- Use MAP_FROM_ARRAYS to create a Map (recommended)
WITH user_profiles AS (
  SELECT 1 AS user_id, MAP_FROM_ARRAYS(ARRAY['age', 'city', 'tier'], ARRAY[25, 1, 3]) AS profile UNION ALL
  SELECT 2, MAP_FROM_ARRAYS(ARRAY['age', 'city', 'tier'], ARRAY[30, 2, 1]) UNION ALL
  SELECT 3, MAP_FROM_ARRAYS(ARRAY['age', 'city', 'tier'], ARRAY[22, 1, 2])
)
SELECT 
  user_id,
  profile,
  -- Filter profile entries where tier > 1
  map_filter(profile, (k, v) -> k = 'tier' AND v > 1) AS high_tier_filter,
  -- Double the age value
  transform_values(profile, (k, v) -> 
    CASE WHEN k = 'age' THEN v * 2 ELSE v END
  ) AS doubled_age,
  -- Convert keys to uppercase
  transform_keys(profile, (k, v) -> UPPER(k)) AS upper_keys
FROM user_profiles;
```

**Output**:

| user_id | profile | high_tier_filter | doubled_age | upper_keys |
|---------|---------|------------------|-------------|------------|
| 1 | age=25:city=1:tier=3 | tier=3 | age=50:city=1:tier=3 | AGE=25:CITY=1:TIER=3 |
| 2 | age=30:city=2:tier=1 | — | age=60:city=2:tier=1 | AGE=30:CITY=2:TIER=1 |
| 3 | age=22:city=1:tier=2 | tier=2 | age=44:city=1:tier=2 | AGE=22:CITY=1:TIER=2 |

---

## Scenario 7: Merging Two Maps (map_zip_with)

### Problem

Merge two Maps and aggregate values for matching keys (e.g., sum or take the maximum).

### SQL Implementation

```sql
SELECT map_zip_with(
  MAP_FROM_ARRAYS(ARRAY['a', 'b'], ARRAY[1, 2]),
  MAP_FROM_ARRAYS(ARRAY['a', 'c'], ARRAY[10, 30]),
  (k, v1, v2) -> COALESCE(v1, 0) + COALESCE(v2, 0)
) AS merged;
```

**Output**:

| merged |
|--------|
| a=11:b=2:c=30 |

---

## Scenario 8: End-to-End Example — User Behavior Tagging

### Problem

Based on user event arrays, compute user behavior tags:
- Whether the user made a purchase
- Average session duration
- Whether the user is high-frequency (event count ≥ 4)
- Primary behavior type (most frequent event)

### SQL Implementation

```sql
SELECT 
  user_id,
  event_types,
  durations,
  -- Purchase flag
  CASE WHEN exists(event_types, t -> t = 'purchase') THEN 'buyer' ELSE 'non_buyer' END AS buyer_flag,
  -- Average duration (total duration / event count)
  array_aggregate(durations, 0, (acc, x) -> acc + x) / 
    array_aggregate(durations, 0, (acc, x) -> acc + 1) AS avg_duration,
  -- High-frequency flag
  CASE WHEN array_aggregate(durations, 0, (acc, x) -> acc + 1) >= 4 
       THEN 'high_freq' ELSE 'low_freq' END AS freq_flag,
  -- Prefix each tag in the tag array
  transform(tags, t -> CONCAT('tag_', t)) AS prefixed_tags
FROM user_events;
```

**Output**:

| user_id | buyer_flag | avg_duration | freq_flag | prefixed_tags |
|---------|------------|--------------|-----------|---------------|
| 1 | buyer | 31 | high_freq | tag_vip:tag_active |
| 2 | non_buyer | 15 | low_freq | tag_new_user |
| 3 | non_buyer | 20 | low_freq | tag_vip:tag_inactive |

---

## Common Issues

### 1. Type error when creating a Map with `MAP()`

```sql
-- Wrong: MAP(ARRAY, ARRAY) creates map<array<string>, array<int>>
MAP(ARRAY['a', 'b'], ARRAY[1, 2])  -- incorrect type

-- Correct: use MAP_FROM_ARRAYS
MAP_FROM_ARRAYS(ARRAY['a', 'b'], ARRAY[1, 2])  -- correct type: map<string, int>
```

### 2. Lambda index starts at 1

```sql
-- The index parameter in filter starts at 1, not 0
filter(durations, (d, i) -> event_types[i] = 'view')  -- i=1 refers to the first element
```

### 3. Codegen limitation with `array_aggregate` finish function

```sql
-- May error: string operations in the finish function (CONCAT not supported in codegen)
array_aggregate(ARRAY['a', 'b'], '', (acc, x) -> acc || x, s -> CONCAT('[', s, ']'))

-- Recommended: numeric aggregation is stable; use transform for string operations after aggregation
array_aggregate(ARRAY[1, 2, 3], 0, (acc, x) -> acc + x)  -- stable
```

### 4. Short-circuit logic in `exists` vs `forall`

- `exists`: returns true as soon as the first element satisfying the condition is found
- `forall`: returns false as soon as the first element not satisfying the condition is found
- Empty array: `exists` returns false, `forall` returns true

### 5. `zip_with` requires arrays of equal length

```sql
-- If arrays have different lengths, extra elements may be dropped or filled with NULL (implementation-dependent)
zip_with(ARRAY[1, 2], ARRAY[10, 20, 30], (x, y) -> x + y)  -- the third element may be lost
```

---

## Performance Optimization Tips

| Scenario | Optimization Strategy |
|---|---|
| Filtering large arrays | Use `filter` to shrink the array first, then apply `transform` or aggregation |
| Frequent `exists` checks | Consider extracting high-frequency check fields into separate columns to avoid scanning the array each time |
| Array aggregation | `array_aggregate` is more efficient than `explode` + `GROUP BY` (no shuffle required) |
| Map operations | Use `map_filter` to filter first, then process, to reduce unnecessary key-value pair computation |

```sql
-- Recommended: filter first, then transform (fewer elements to process)
transform(filter(durations, d -> d > 10), d -> d * 2)

-- Not recommended: transform first, then filter (all elements go through transform)
filter(transform(durations, d -> d * 2), d -> d > 20)
```

---

## Related Documentation

* [ARRAY Type](ARRAY.md)
* [MAP Type](MAP.md)
* [Nested Data Type Conversion](sql_data_transfom_NestedDataTypes.md)
* [Array Explode and Flatten Guide](SQL_Array_Explode_Guide.md)
* [Higher-Order Functions Reference](sql_functions/scalar_functions/high_order_functions/)
