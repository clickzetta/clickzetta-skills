# BITMAP User Analysis

## Overview

BITMAP is an efficient set data structure that uses integer bits to represent set members. In user analysis scenarios, BITMAP's core advantage is: **computing intersection, union, and difference on large-scale user ID sets is significantly faster than JOIN or IN subqueries**.

Typical scenarios:
- Calculate DAU / MAU (daily/monthly active deduplicated user count)
- Multi-tag audience selection: users matching "VIP AND active in last 7 days"
- Retention analysis: users active for N consecutive days
- Funnel intersection: users who completed both step A and step B

### Core Function Reference

| Function | Input Type | Return Type | Description |
|------|---------|---------|------|
| `bitmap_build(array)` | `ARRAY<BIGINT>` | `bitmap` | Build a bitmap object from an array |
| `bitmap_count(bm)` | `bitmap` | `BIGINT` | Return the number of elements in the bitmap (cardinality) |
| `bitmap_to_array(bm)` | `bitmap` | `ARRAY<BIGINT>` | Convert the bitmap to an array to view members |
| `TO_BITMAP(n)` | `BIGINT` | `bitmap` | Build a bitmap containing a single element |
| `group_bitmap(id)` | `BIGINT` | `BIGINT` | Aggregate function, returns the cardinality of unique IDs within the group |
| `group_bitmap_state(id)` | `BIGINT` | `bitmap` | Aggregate function, returns a bitmap object (for two-phase aggregation) |
| `group_bitmap_or(bm)` | `bitmap` | `BIGINT` | Aggregate function, computes union cardinality of multiple bitmaps |
| `group_bitmap_and(bm)` | `bitmap` | `BIGINT` | Aggregate function, computes intersection cardinality of multiple bitmaps |
| `group_bitmap_xor(bm)` | `bitmap` | `BIGINT` | Aggregate function, computes XOR cardinality of multiple bitmaps |
| `group_bitmap_merge(bm)` | `bitmap` | `BIGINT` | Aggregate function, merges multiple bitmap states and returns union cardinality |
| `bm1 & bm2` | `bitmap` | `bitmap` | Intersection (AND) |
| `bm1 \| bm2` | `bitmap` | `bitmap` | Union (OR) |
| `bm1 ^ bm2` | `bitmap` | `bitmap` | XOR (symmetric difference) |

> `group_bitmap` returns `BIGINT` (cardinality), not a bitmap object, and cannot be used in further bitwise operations. Use `group_bitmap_state` when a bitmap object is needed.

---

## Prerequisite Data

```SQL
-- User tag table (one row per user-tag relationship)
CREATE TABLE IF NOT EXISTS doc_bitmap_user_tags (
  tag_name VARCHAR(50),
  user_id  BIGINT
);

INSERT INTO doc_bitmap_user_tags VALUES
  ('vip',       1001), ('vip',       1002), ('vip',       1003),
  ('vip',       1004), ('vip',       1005),
  ('active_7d', 1001), ('active_7d', 1003), ('active_7d', 1005),
  ('active_7d', 1007), ('active_7d', 1009),
  ('buyer',     1002), ('buyer',     1003), ('buyer',     1004),
  ('buyer',     1006), ('buyer',     1008);

-- Daily active user table (each row stores one day's active user ID array)
CREATE TABLE IF NOT EXISTS doc_bitmap_daily_active (
  dt       DATE,
  user_ids ARRAY<BIGINT>
);

INSERT INTO doc_bitmap_daily_active VALUES
  (CAST('2024-01-01' AS DATE), ARRAY(1001,1002,1003,1004,1005)),
  (CAST('2024-01-02' AS DATE), ARRAY(1001,1003,1005,1007,1009)),
  (CAST('2024-01-03' AS DATE), ARRAY(1002,1003,1004,1006,1008));
```

---

## Scenario 1: Daily Active Users (DAU)

```SQL
SELECT
  dt,
  BITMAP_COUNT(bitmap_build(user_ids)) AS dau
FROM doc_bitmap_daily_active
ORDER BY dt;
```

Results:

| dt         | dau |
|------------|-----|
| 2024-01-01 | 5   |
| 2024-01-02 | 5   |
| 2024-01-03 | 5   |

---

## Scenario 2: Multi-day Deduplicated Active Users (MAU)

Compute the deduplicated active user count across 3 days (union).

```SQL
SELECT group_bitmap_or(bitmap_build(user_ids)) AS mau_3days
FROM doc_bitmap_daily_active;
```

Results:

| mau_3days |
|-----------|
| 9         |

> `group_bitmap_or` computes the union of bitmaps across all rows and returns the union's cardinality (deduplicated user count).

---

## Scenario 3: Users Retained for N Consecutive Days

Compute users active on all 3 consecutive days (intersection).

```SQL
SELECT group_bitmap_and(bitmap_build(user_ids)) AS retained_3days
FROM doc_bitmap_daily_active;
```

Results:

| retained_3days |
|----------------|
| 1              |

> `group_bitmap_and` computes the intersection of bitmaps across all rows and returns the intersection's cardinality. Only user_id=1003 appears on all three days.

---

## Scenario 4: Retention Between Two Days (Date-specific Intersection)

Compute the count of users active on both Jan 1 and Jan 2.

```SQL
SELECT
  BITMAP_COUNT(
    bitmap_build(d1.user_ids) & bitmap_build(d2.user_ids)
  ) AS day1_day2_common
FROM
  (SELECT user_ids FROM doc_bitmap_daily_active WHERE dt = CAST('2024-01-01' AS DATE)) d1,
  (SELECT user_ids FROM doc_bitmap_daily_active WHERE dt = CAST('2024-01-02' AS DATE)) d2;
```

Results:

| day1_day2_common |
|------------------|
| 3                |

> Jan 1 active users: 1001,1002,1003,1004,1005; Jan 2 active users: 1001,1003,1005,1007,1009; Intersection: 1001,1003,1005 (3 users).

---

## Scenario 5: Multi-tag Audience Selection (Intersection / Union / Difference)

### 5.1 Intersection: Users meeting multiple tags simultaneously

```SQL
SELECT
  BITMAP_COUNT(
    bitmap_build(a.user_ids) & bitmap_build(b.user_ids)
  ) AS vip_and_active
FROM
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'vip') a,
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'active_7d') b;
```

Results:

| vip_and_active |
|----------------|
| 3              |

View which specific users:

```SQL
SELECT
  bitmap_to_array(
    bitmap_build(a.user_ids) & bitmap_build(b.user_ids)
  ) AS vip_and_active_users
FROM
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'vip') a,
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'active_7d') b;
```

Results:

| vip_and_active_users    |
|-------------------------|
| ["1001", "1003", "1005"] |

### 5.2 Union: Users meeting either tag (deduplicated)

```SQL
SELECT
  BITMAP_COUNT(
    bitmap_build(a.user_ids) | bitmap_build(b.user_ids)
  ) AS vip_or_active
FROM
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'vip') a,
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'active_7d') b;
```

Results:

| vip_or_active |
|---------------|
| 7             |

### 5.3 Difference: Users in A but not in B

Singdata Lakehouse does not support the `~` negation operator. The difference set is implemented equivalently as `A XOR (A AND B)`:

```SQL
SELECT
  BITMAP_COUNT(
    bitmap_build(a.user_ids) ^ (bitmap_build(a.user_ids) & bitmap_build(b.user_ids))
  ) AS vip_not_active
FROM
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'vip') a,
  (SELECT COLLECT_LIST(user_id) AS user_ids FROM doc_bitmap_user_tags WHERE tag_name = 'active_7d') b;
```

Results:

| vip_not_active |
|----------------|
| 2              |

> Among VIP users (1001-1005), those not in active_7d (1001,1003,1005,1007,1009) are 1002 and 1004, totaling 2 users.

---

## Scenario 6: User Count Per Tag (GROUP_BITMAP)

```SQL
SELECT tag_name, GROUP_BITMAP(user_id) AS user_count
FROM doc_bitmap_user_tags
GROUP BY tag_name
ORDER BY tag_name;
```

Results:

| tag_name  | user_count |
|-----------|------------|
| active_7d | 5          |
| buyer     | 5          |
| vip       | 5          |

> `GROUP_BITMAP` directly returns the cardinality (BIGINT), suitable for scenarios where only the count is needed.

---

## Scenario 7: Two-phase Aggregation (Big Data Optimization)

When data volume is large, use `group_bitmap_state` to generate intermediate bitmaps by partition first, then use `group_bitmap_merge` to combine them, reducing memory pressure on individual aggregations.

```SQL
-- Build bitmap state by day first, then merge to compute 3-day MAU
SELECT group_bitmap_merge(daily_state) AS mau_3days
FROM (
  SELECT dt, group_bitmap_state(user_id) AS daily_state
  FROM (
    SELECT dt, EXPLODE(user_ids) AS user_id
    FROM doc_bitmap_daily_active
  ) t
  GROUP BY dt
) agg;
```

Results:

| mau_3days |
|-----------|
| 9         |

> Two-phase aggregation yields the same result as direct `group_bitmap_or`, but is better suited for pre-aggregation optimization in distributed scenarios.

---

## Notes

- **`group_bitmap` returns BIGINT, not a bitmap object**: you cannot apply `&`, `|`, `^` operations to its result. Use `group_bitmap_state` when a bitmap object is needed.
- **No direct difference operator**: the `~` negation is not supported. Compute the difference `A - B` as `A ^ (A & B)`.
- **`bitmap_build` accepts `ARRAY<BIGINT>`**: if data consists of user IDs stored row-by-row, first aggregate them into an array with `COLLECT_LIST`, then pass to `bitmap_build`.
- **User IDs must be non-negative integers**: BITMAP is based on integer bitmaps and does not support negative or non-integer IDs.
- **`bitmap_to_array` result is a string array**: the returned array element type is `STRING`; use `CAST` if numeric comparison is needed.
