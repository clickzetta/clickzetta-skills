# BITMAP User Profiling Reference

> Source: https://www.yunqi.tech/documents/bitmap-type

BITMAP is a data type in ClickZetta for efficiently storing and processing integer sets, based on the Roaring Bitmap compression algorithm. It is particularly suited for data science use cases such as user profiling, audience segmentation, and UV counting.

---

## Core Limitations

- Supports **64-bit unsigned integers** (0 to 2^64-1)
- **Does not support** comparison operators (<, >, =)
- **Does not support** ORDER BY, GROUP BY, DISTINCT
- **Cannot** be used as PRIMARY KEY, PARTITION KEY, or CLUSTER KEY

---

## Building User Tag BITMAPs

```sql
-- Option 1: Aggregate from row data (most common)
CREATE TABLE ds_workspace.user_tags AS
SELECT
    tag_name,
    group_bitmap_state(user_id) AS user_bitmap
FROM (
    -- High-value users
    SELECT 'high_value' AS tag_name, user_id
    FROM my_schema.orders
    WHERE total_amount_30d > 1000
    UNION ALL
    -- Active in last 30 days
    SELECT 'active_30d' AS tag_name, user_id
    FROM my_schema.events
    WHERE event_date >= CURRENT_DATE - INTERVAL 30 DAY
    UNION ALL
    -- Churned users (inactive for 90 days)
    SELECT 'churned' AS tag_name, user_id
    FROM my_schema.users
    WHERE last_active_date < CURRENT_DATE - INTERVAL 90 DAY
) t
GROUP BY tag_name;

-- Option 2: Build from an array
INSERT INTO ds_workspace.user_tags VALUES
    ('vip', bitmap_build(ARRAY(1001, 1002, 1003, 1004)));
```

---

## Audience Segmentation Operations

```sql
-- Intersection: users matching all tags (AND)
SELECT bitmap_count(
    bitmap_and(
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'high_value'),
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'active_30d')
    )
) AS target_count;

-- Union: users matching any tag (OR)
SELECT bitmap_count(
    bitmap_or(
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'high_value'),
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'active_30d')
    )
) AS reach_count;

-- Difference: exclude a group (ANDNOT)
SELECT bitmap_count(
    bitmap_andnot(
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'high_value'),
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'churned')
    )
) AS targetable_count;

-- Get target user ID list
SELECT bitmap_to_array(
    bitmap_andnot(
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'high_value'),
        (SELECT user_bitmap FROM ds_workspace.user_tags WHERE tag_name = 'churned')
    )
) AS target_user_ids;
```

---

## UV Counting (Distinct Count)

```sql
-- Daily active users (DAU)
SELECT
    event_date,
    bitmap_count(group_bitmap_state(user_id)) AS dau
FROM my_schema.events
GROUP BY event_date
ORDER BY event_date;

-- Weekly active users (WAU) — deduplicated across days
SELECT
    DATE_TRUNC('week', event_date) AS week_start,
    bitmap_count(
        bitmap_or_agg(daily_bitmap)  -- merge multiple days' bitmaps
    ) AS wau
FROM (
    SELECT event_date,
           group_bitmap_state(user_id) AS daily_bitmap
    FROM my_schema.events
    GROUP BY event_date
) t
GROUP BY 1;

-- User retention analysis (new vs. returning users)
SELECT
    bitmap_count(
        bitmap_and(new_users.user_bitmap, return_users.user_bitmap)
    ) AS retained_users,
    bitmap_count(
        bitmap_andnot(new_users.user_bitmap, return_users.user_bitmap)
    ) AS lost_users
FROM
    (SELECT group_bitmap_state(user_id) AS user_bitmap
     FROM my_schema.events WHERE event_date = '2024-01-01') AS new_users,
    (SELECT group_bitmap_state(user_id) AS user_bitmap
     FROM my_schema.events WHERE event_date = '2024-01-08') AS return_users;
```

---

## BITMAP Function Quick Reference

| Function | Description | Example |
|---|---|---|
| `group_bitmap_state(col)` | Aggregate to build a BITMAP | `GROUP BY tag` |
| `bitmap_count(bm)` | Count elements (UV) | `bitmap_count(user_bm)` |
| `bitmap_and(a, b)` | Intersection | Users in both A and B |
| `bitmap_or(a, b)` | Union | Users in A or B |
| `bitmap_andnot(a, b)` | Difference | In A but not in B |
| `bitmap_xor(a, b)` | Symmetric difference | Exclusive to either A or B |
| `bitmap_to_array(bm)` | Convert to integer array | Get user ID list |
| `bitmap_build(arr)` | Build from array | `bitmap_build(ARRAY(1,2,3))` |
| `bitmap_contains(bm, val)` | Check if value is present | `bitmap_contains(bm, user_id)` |
| `bitmap_min(bm)` | Minimum element | — |
| `bitmap_max(bm)` | Maximum element | — |
| `to_bitmap(val)` | Convert single value to BITMAP | `to_bitmap(user_id)` |
