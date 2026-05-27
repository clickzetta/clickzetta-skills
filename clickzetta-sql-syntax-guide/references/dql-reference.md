# DQL Complete Syntax Reference

> Based on ClickZetta Lakehouse product documentation, with Snowflake / Spark SQL difference annotations

---

## SELECT Basic Syntax

```sql
[WITH cte_name AS (SELECT ...) [, ...]]
SELECT
    [/*+ HINTS */]
    [ALL | DISTINCT]
    select_expr [, ...]
    [EXCEPT (col1, col2, ...)]
FROM table_reference
[WHERE condition]
[GROUP BY [GROUPING SETS | ROLLUP | CUBE] {col | expr | position}]
[HAVING condition]
[ORDER BY col [ASC | DESC] [NULLS FIRST | NULLS LAST] [, ...]]
[LIMIT n [OFFSET m]]
```

---

## SELECT Extensions

### EXCEPT (Exclude Columns)

```sql
-- Exclude specified columns (ClickZetta-specific, Snowflake/Spark also support)
SELECT * EXCEPT(password, secret_key) FROM users;
SELECT * EXCEPT(meta, tags) FROM orders;
```

### DISTINCT

```sql
SELECT DISTINCT customer_id FROM orders;
SELECT ALL customer_id FROM orders;    -- default, keeps duplicates
```

### LIMIT / OFFSET

```sql
SELECT * FROM orders LIMIT 100;
SELECT * FROM orders LIMIT 100 OFFSET 200;   -- skip first 200 rows

-- ⚠️ ClickZetta does not support Snowflake's TOP N syntax
-- Snowflake: SELECT TOP 10 * FROM orders;
-- ClickZetta: SELECT * FROM orders LIMIT 10;
```

---

## FROM Clause

### JOIN

```sql
-- INNER JOIN
SELECT o.id, c.name FROM orders o
INNER JOIN customers c ON o.customer_id = c.id;

-- LEFT / RIGHT / FULL OUTER JOIN
SELECT o.id, c.name FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id;

-- CROSS JOIN
SELECT * FROM a CROSS JOIN b;

-- SELF JOIN
SELECT a.id, b.id FROM orders a JOIN orders b ON a.customer_id = b.customer_id;

-- USING syntax
SELECT * FROM orders JOIN customers USING (customer_id);

-- NATURAL JOIN
SELECT * FROM orders NATURAL JOIN customers;

-- SEMI JOIN (implemented with EXISTS or IN)
SELECT * FROM orders WHERE EXISTS (
    SELECT 1 FROM customers WHERE customers.id = orders.customer_id
);

-- ANTI JOIN (implemented with NOT EXISTS or NOT IN)
SELECT * FROM orders WHERE NOT EXISTS (
    SELECT 1 FROM customers WHERE customers.id = orders.customer_id
);
```

**Differences from Snowflake:**
- Snowflake supports `ASOF JOIN` (time-series join); ClickZetta does not
- Snowflake supports `MATCH_RECOGNIZE`; ClickZetta does not

### LATERAL VIEW (Expand Arrays/MAPs)

```sql
-- EXPLODE to expand array
SELECT e.id, s.skill
FROM employees e
LATERAL VIEW EXPLODE(e.skills) s AS skill;

-- POSEXPLODE with position index
SELECT e.id, ps.pos, ps.skill
FROM employees e
LATERAL VIEW POSEXPLODE(e.skills) ps AS pos, skill;

-- OUTER (preserves rows even for empty arrays)
SELECT e.id, s.skill
FROM employees e
LATERAL VIEW OUTER EXPLODE(e.skills) s AS skill;

-- Expand MAP
SELECT id, k, v
FROM t
LATERAL VIEW EXPLODE(meta_map) m AS k, v;
```

**Differences from Snowflake:**
- Snowflake uses `LATERAL FLATTEN(input => arr)`; ClickZetta uses `LATERAL VIEW EXPLODE(arr)`
- Snowflake `f.value::STRING`; ClickZetta uses column alias directly

**Differences from Spark SQL:**
- Syntax is identical (ClickZetta is compatible with Hive/Spark style)

### TABLESAMPLE

```sql
-- SYSTEM mode: sample by percentage (file-level)
SELECT * FROM orders TABLESAMPLE (10 PERCENT);

-- ROW mode: sample by row count
SELECT * FROM orders TABLESAMPLE (100 ROWS);
```

### SEQUENCE (Generate Sequences)

```sql
-- Generate integer sequence (returns ARRAY)
SELECT SEQUENCE(1, 5);                -- [1,2,3,4,5]
SELECT SEQUENCE(0, 10, 2);            -- [0,2,4,6,8,10]

-- Expand to rows (ClickZetta uses EXPLODE(SEQUENCE(...)), no GENERATE_SERIES)
SELECT EXPLODE(SEQUENCE(1, 5)) AS n;  -- 5 rows: 1,2,3,4,5
```

### EXPLODE Directly in SELECT

```sql
-- Spark style: EXPLODE directly in SELECT
SELECT EXPLODE(ARRAY(1, 2, 3)) AS val;
SELECT POSEXPLODE(ARRAY('a', 'b', 'c')) AS (pos, val);

-- Equivalent LATERAL VIEW syntax
SELECT val FROM (SELECT ARRAY(1,2,3) AS arr) t
LATERAL VIEW EXPLODE(arr) lv AS val;
```



## WHERE Clause

```sql
-- Basic conditions
WHERE amount > 100 AND status = 'completed'
WHERE status IN ('pending', 'processing')
WHERE status NOT IN ('cancelled', 'refunded')
WHERE amount BETWEEN 100 AND 1000
WHERE name LIKE '%Alice%'
WHERE name NOT LIKE '%test%'
WHERE tags IS NULL
WHERE tags IS NOT NULL

-- Regex matching
WHERE name RLIKE '^[A-Z].*'
WHERE name REGEXP '^[A-Z].*'    -- same as RLIKE

-- Subquery
WHERE customer_id IN (SELECT id FROM customers WHERE tier = 'VIP')
WHERE EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id)
```

**Differences from Snowflake:**
- Snowflake `ILIKE` (case-insensitive LIKE) → ClickZetta `ILIKE` ✅ also supported
- Snowflake `RLIKE` → ClickZetta also supports `RLIKE` / `REGEXP`

---

## GROUP BY Extensions

```sql
-- Basic grouping
SELECT region, SUM(amount) FROM orders GROUP BY region;
SELECT region, SUM(amount) FROM orders GROUP BY 1;    -- by position

-- GROUP BY ALL (auto-infer all non-aggregate columns)
SELECT year, month, region, SUM(amount) FROM orders GROUP BY ALL;

-- GROUPING SETS (multi-dimensional grouping)
SELECT region, product, SUM(sales)
FROM orders
GROUP BY GROUPING SETS ((region, product), (region), (product), ());

-- ROLLUP (hierarchical subtotals)
SELECT region, city, SUM(amount)
FROM orders
GROUP BY ROLLUP (region, city);
-- equivalent to GROUPING SETS ((region, city), (region), ())

-- CUBE (all-combination subtotals)
SELECT region, product, channel, SUM(amount)
FROM orders
GROUP BY CUBE (region, product, channel);

-- HAVING
SELECT customer_id, SUM(amount) AS total
FROM orders
GROUP BY customer_id
HAVING total > 10000;
```

**Differences from Snowflake:**
- `GROUP BY ALL` both support
- `GROUPING SETS / ROLLUP / CUBE` both support

---

## ORDER BY

```sql
SELECT * FROM orders ORDER BY amount DESC;
SELECT * FROM orders ORDER BY amount DESC NULLS LAST;
SELECT * FROM orders ORDER BY amount ASC NULLS FIRST;
SELECT * FROM orders ORDER BY 1 DESC, 2 ASC;    -- by position
```

---

## CTE (Common Table Expressions)

```sql
-- Basic CTE
WITH
    monthly AS (
        SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount) AS total
        FROM orders GROUP BY 1
    ),
    ranked AS (
        SELECT *, RANK() OVER (ORDER BY total DESC) AS rnk FROM monthly
    )
SELECT * FROM ranked WHERE rnk <= 5;

-- ⚠️ Recursive CTE (ClickZetta does NOT support)
-- Snowflake/Databricks/Spark SQL support:
WITH RECURSIVE org_tree AS (
    SELECT id, name, parent_id, 0 AS level
    FROM employees WHERE parent_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.parent_id, t.level + 1
    FROM employees e JOIN org_tree t ON e.parent_id = t.id
)
SELECT * FROM org_tree ORDER BY level, id;

-- ClickZetta alternative: use Python/ZettaPark for iteration
-- Or use multi-level CTEs to simulate limited-depth recursion
WITH
    level0 AS (SELECT id, name, parent_id, 0 AS level FROM employees WHERE parent_id IS NULL),
    level1 AS (SELECT e.id, e.name, e.parent_id, 1 AS level FROM employees e JOIN level0 t ON e.parent_id = t.id),
    level2 AS (SELECT e.id, e.name, e.parent_id, 2 AS level FROM employees e JOIN level1 t ON e.parent_id = t.id)
SELECT * FROM level0 UNION ALL SELECT * FROM level1 UNION ALL SELECT * FROM level2;
```

**Differences from Snowflake:**
- Snowflake supports `WITH RECURSIVE`; ClickZetta ❌ does not support recursive CTE
- ClickZetta only supports non-recursive CTE (regular WITH clause)
- For recursive scenarios, use Python/ZettaPark iteration, or multi-level CTEs to simulate limited depth

---

## Window Functions

```sql
-- Basic syntax
function_name() OVER (
    [PARTITION BY col1, col2]
    [ORDER BY col3 [ASC|DESC]]
    [ROWS|RANGE BETWEEN start AND end]
)

-- Ranking functions
ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)
RANK() OVER (ORDER BY score DESC)
DENSE_RANK() OVER (ORDER BY score DESC)
NTILE(4) OVER (ORDER BY amount)
PERCENT_RANK() OVER (ORDER BY amount)
CUME_DIST() OVER (ORDER BY amount)

-- Aggregate windows
SUM(amount) OVER (PARTITION BY customer_id)
AVG(amount) OVER (PARTITION BY dept ORDER BY date
                  ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
COUNT(*) OVER (PARTITION BY region)
MAX(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)

-- Analytic functions
LAG(amount, 1, 0) OVER (ORDER BY date)          -- 1 row before, default 0
LEAD(amount, 1) OVER (ORDER BY date)             -- 1 row after
FIRST_VALUE(amount) OVER (ORDER BY date)
LAST_VALUE(amount) OVER (ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
NTH_VALUE(amount, 3) OVER (ORDER BY date)

-- Window Frame
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW    -- from start to current row
ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING            -- 3 rows before and after
RANGE BETWEEN INTERVAL 7 DAY PRECEDING AND CURRENT ROW  -- within 7 days
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING    -- current row to end
```

**Differences from Snowflake:**
- ClickZetta also supports `QUALIFY` to directly filter window function results:
  ```sql
  -- Both support
  SELECT * FROM orders QUALIFY ROW_NUMBER() OVER (PARTITION BY cust ORDER BY dt DESC) = 1;
  -- Subquery approach also works
  SELECT * FROM (
      SELECT *, ROW_NUMBER() OVER (PARTITION BY cust ORDER BY dt DESC) AS rn FROM orders
  ) t WHERE rn = 1;
  ```

---

## Subqueries

```sql
-- Scalar subquery
SELECT id, (SELECT MAX(amount) FROM orders) AS max_amount FROM orders;

-- IN subquery
SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE tier = 'VIP');

-- EXISTS subquery
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- Correlated subquery
SELECT * FROM orders o
WHERE amount > (SELECT AVG(amount) FROM orders WHERE customer_id = o.customer_id);

-- FROM subquery (derived table)
SELECT t.region, t.total FROM (
    SELECT region, SUM(amount) AS total FROM orders GROUP BY region
) t WHERE t.total > 100000;
```

---

## JSON Queries

```sql
-- Access JSON fields (use [] instead of Snowflake's :)
SELECT data['address']['city'] AS city FROM users;
SELECT data['phoneNumbers'][0]['number'] AS phone FROM users;
SELECT data['scores'][2] AS third_score FROM users;

-- Build JSON
SELECT PARSE_JSON('{"name":"Alice","age":30}') AS info;
SELECT TO_JSON(STRUCT(name, age)) AS json_str FROM users;

-- Type conversion
SELECT CAST(data['age'] AS INT) AS age FROM users;
SELECT data['amount']::DOUBLE AS amount FROM orders;    -- :: syntax also supported

-- JSON aggregation
SELECT customer_id, TO_JSON(COLLECT_LIST(STRUCT(id, amount))) AS orders_json
FROM orders GROUP BY customer_id;
```

**Differences from Snowflake:**
- Snowflake `data:key` colon syntax → ClickZetta `data['key']` bracket syntax
- Snowflake `data:key::STRING` → ClickZetta `CAST(data['key'] AS STRING)` or `data['key']::STRING`
- Snowflake `OBJECT_CONSTRUCT(k, v)` → ClickZetta `MAP_AGG(k, v)` or `STRUCT(...)` + `TO_JSON`
- Snowflake `PARSE_JSON` → ClickZetta same

---

## STRUCT / ARRAY / MAP Operations

```sql
-- Build STRUCT
SELECT STRUCT(name, age, email) AS user_info FROM users;              -- ✅ supported (no field names, defaults to col1, col2...)
SELECT named_struct('name', name, 'age', age, 'email', email) AS user_info FROM users;  -- ✅ supported (with field names)
-- ⚠️ SELECT STRUCT(name AS n, age AS a) does not support AS syntax (Snowflake/Spark support it)

-- Build ARRAY / MAP
SELECT ARRAY(1, 2, 3) AS nums;
SELECT MAP('k1', 1, 'k2', 2) AS m;

-- Access
SELECT address.city FROM users;                    -- STRUCT field
SELECT skills[0] FROM employees;                   -- ARRAY index (0-based)
SELECT meta_map['key'] FROM t;                     -- MAP access

-- Array functions
SELECT SIZE(skills) AS cnt FROM employees;
SELECT ARRAY_CONTAINS(skills, 'Python') FROM employees;
SELECT ARRAY_AGG(order_id) FROM orders GROUP BY customer_id;
SELECT COLLECT_LIST(order_id) FROM orders GROUP BY customer_id;   -- same as ARRAY_AGG
SELECT COLLECT_SET(status) FROM orders GROUP BY customer_id;      -- deduplicated
SELECT SORT_ARRAY(skills) FROM employees;
SELECT ARRAY_DISTINCT(tags) FROM articles;
SELECT ARRAY_UNION(a, b) FROM t;
SELECT ARRAY_INTERSECT(a, b) FROM t;
SELECT ARRAY_EXCEPT(a, b) FROM t;
SELECT FLATTEN(nested_array) FROM t;               -- flatten nested array

-- Higher-order functions
SELECT TRANSFORM(skills, x -> UPPER(x)) FROM employees;
SELECT FILTER(scores, x -> x > 90) FROM students;
-- ⚠️ AGGREGATE(arr, init, (acc,x)->...) not supported, use ARRAY_AGG + SUM instead
-- ⚠️ REDUCE(arr, init, (acc,x)->...) not supported (Spark name)
SELECT EXISTS(scores, x -> x > 100) FROM students;
SELECT FORALL(scores, x -> x >= 0) FROM students;
SELECT ZIP_WITH(a, b, (x, y) -> x + y) FROM t;

-- MAP functions
SELECT MAP_KEYS(meta) FROM t;
SELECT MAP_VALUES(meta) FROM t;
SELECT MAP_ENTRIES(meta) FROM t;
SELECT MAP_CONCAT(m1, m2) FROM t;
SELECT MAP_FILTER(meta, (k, v) -> v > 0) FROM t;
SELECT MAP_TRANSFORM_VALUES(meta, (k, v) -> v * 2) FROM t;
```

**Differences from Snowflake:**
- Snowflake `ARRAY_SIZE` → ClickZetta `SIZE`
- Snowflake `ARRAY_CONTAINS(val, arr)` parameter order reversed → ClickZetta `ARRAY_CONTAINS(arr, val)`
- Snowflake `OBJECT_KEYS(obj)` → ClickZetta `MAP_KEYS(map)`
- Snowflake has no higher-order functions (TRANSFORM/FILTER); ClickZetta supports them

---

## PIVOT / UNPIVOT

```sql
-- ClickZetta does not support native PIVOT syntax
-- Use CASE WHEN for row-to-column transformation
SELECT
    product,
    SUM(CASE WHEN month = 'Jan' THEN amount ELSE 0 END) AS Jan,
    SUM(CASE WHEN month = 'Feb' THEN amount ELSE 0 END) AS Feb,
    SUM(CASE WHEN month = 'Mar' THEN amount ELSE 0 END) AS Mar
FROM sales
GROUP BY product;

-- UNPIVOT implemented with LATERAL VIEW + STACK
SELECT id, month, amount
FROM sales
LATERAL VIEW STACK(3,
    'Jan', jan_amount,
    'Feb', feb_amount,
    'Mar', mar_amount
) t AS month, amount;
```

**Differences from Snowflake:**
- Snowflake natively supports `PIVOT` / `UNPIVOT` syntax; ClickZetta does not, requires manual implementation

---

## SET Operations

```sql
-- ClickZetta supports UNION / UNION ALL / INTERSECT / EXCEPT set operations
SELECT id FROM orders_2023
UNION ALL
SELECT id FROM orders_2024;

SELECT id FROM orders_2023
UNION
SELECT id FROM orders_2024;

SELECT id FROM orders_2023
INTERSECT
SELECT id FROM orders_2024;

SELECT id FROM orders_2023
EXCEPT
SELECT id FROM orders_2024;
```

---

## HINTS (Query Hints)

```sql
-- MAPJOIN (force broadcast small table)
SELECT /*+ MAPJOIN(small_table) */ *
FROM large_table l JOIN small_table s ON l.id = s.id;

-- Vector index search factor
SET cz.vector.index.search.ef = 128;
```
