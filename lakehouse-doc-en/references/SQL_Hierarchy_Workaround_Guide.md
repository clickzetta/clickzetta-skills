# Hierarchy Query Workaround Guide

> **Problem**: Singdata Lakehouse does not support `WITH RECURSIVE` recursive CTEs, so you cannot directly expand hierarchical relationships (org charts, product categories, BOM bills of materials, etc.).
>
> **Solution**: This guide provides three battle-tested workaround approaches covering different business scenarios.

---

## Quick Selection

| Approach | Best For | Max Depth | Write Complexity | Query Performance |
|---|---|---|---|---|
| Fixed-depth JOIN | Known maximum depth (e.g., org ≤ 10 levels) | Fixed | Low (adjacency list) | Medium |
| Materialized Path | Flexible queries across any level | Unlimited | Medium (maintain path) | High |
| Closure Table | Frequent hierarchy queries | Unlimited | High (maintain closure) | Highest |

---

## Sample Data

All examples in this guide are based on the following 6-level org chart:

```
CEO (1)
├── VP Eng (2)
│   └── Eng Lead (4)
│       └── Senior Dev (5)
│           └── Junior Dev (6)
│               └── Intern (9)
├── VP Sales (3)
│   └── Sales Lead (7)
│       └── Sales Rep (8)
└── VP Product (10)
```

---

## Approach 1: Fixed-Depth Multi-Level LEFT JOIN

### Best For

- Known maximum depth (most enterprise orgs have ≤ 10 levels)
- Simple adjacency list table structure (`id`, `parent_id`)
- No changes to the existing data model

### Look Up All Ancestors

```sql
SELECT 
  e.emp_id,
  e.name AS employee,
  m1.name AS manager_l1,
  m2.name AS manager_l2,
  m3.name AS manager_l3,
  m4.name AS manager_l4,
  m5.name AS manager_l5,
  m6.name AS manager_l6
FROM org e
LEFT JOIN org m1 ON e.manager_id = m1.emp_id
LEFT JOIN org m2 ON m1.manager_id = m2.emp_id
LEFT JOIN org m3 ON m2.manager_id = m3.emp_id
LEFT JOIN org m4 ON m3.manager_id = m4.emp_id
LEFT JOIN org m5 ON m4.manager_id = m5.emp_id
LEFT JOIN org m6 ON m5.manager_id = m6.emp_id
ORDER BY e.emp_id;
```

**Sample output**:

| emp_id | employee   | manager_l1 | manager_l2 | manager_l3 | manager_l4 | manager_l5 |
|--------|------------|------------|------------|------------|------------|------------|
| 1      | CEO        | NULL       | NULL       | NULL       | NULL       | NULL       |
| 5      | Senior Dev | Eng Lead   | VP Eng     | CEO        | NULL       | NULL       |
| 9      | Intern     | Junior Dev | Senior Dev | Eng Lead   | VP Eng     | CEO        |

### Calculate Hierarchy Depth

```sql
SELECT 
  e.emp_id,
  e.name,
  -- Determine actual depth from the first non-NULL manager column
  CASE 
    WHEN m6.name IS NOT NULL THEN 6
    WHEN m5.name IS NOT NULL THEN 5
    WHEN m4.name IS NOT NULL THEN 4
    WHEN m3.name IS NOT NULL THEN 3
    WHEN m2.name IS NOT NULL THEN 2
    WHEN m1.name IS NOT NULL THEN 1
    ELSE 0
  END AS depth
FROM org e
LEFT JOIN org m1 ON e.manager_id = m1.emp_id
LEFT JOIN org m2 ON m1.manager_id = m2.emp_id
LEFT JOIN org m3 ON m2.manager_id = m3.emp_id
LEFT JOIN org m4 ON m3.manager_id = m4.emp_id
LEFT JOIN org m5 ON m4.manager_id = m5.emp_id
LEFT JOIN org m6 ON m5.manager_id = m6.emp_id;
```

### Pros and Cons

| Pros | Cons |
|---|---|
| No schema changes required | Fixed JOIN depth — cannot expand beyond the limit |
| Simple, readable SQL | Performance degrades with many JOIN levels |
| Good for one-off queries | Not suitable for dynamic hierarchies |

---

## Approach 2: Materialized Path

### Best For

- Flexible queries across any level (up, down, or sideways)
- You can maintain a path column at write time
- Hierarchy depth is unknown or variable

### Table Design

```sql
CREATE TABLE org_path (
  emp_id BIGINT,
  name VARCHAR,
  manager_id BIGINT,
  path VARCHAR  -- Format: '/0001/0002/0004/', padded with LPAD to ensure correct lexicographic order
);
```

> **Key point**: IDs in the path must be padded to a fixed width using `LPAD` (e.g., 4 digits). Without padding, lexicographic sorting breaks — `/1/10/` sorts before `/1/2/`.

### Maintaining the Path at Write Time

```sql
-- Insert the root node
INSERT INTO org_path VALUES (1, 'CEO', 0, '/0001/');

-- Insert a child node (path = parent path + own ID)
INSERT INTO org_path 
SELECT 2, 'VP Eng', 1, path || '/0002/' FROM org_path WHERE emp_id = 1;
```

### Query Pattern 1: Find All Descendants (Subtree)

```sql
-- Find all reports under CEO
SELECT emp_id, name, path,
  (LENGTH(path) - LENGTH(REPLACE(path, '/', '')) - 1) AS depth
FROM org_path
WHERE path LIKE '/0001/%' AND emp_id != 1
ORDER BY path;
```

### Query Pattern 2: Find All Ancestors

```sql
-- Find all ancestors of Intern (emp_id=9)
WITH levels AS (
  SELECT 1 AS lvl UNION ALL SELECT 2 UNION ALL SELECT 3 
  UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6
)
SELECT 
  l.lvl AS level,
  CAST(SPLIT_PART('/0001/0002/0004/0005/0006/0009/', '/', l.lvl + 1) AS BIGINT) AS ancestor_id
FROM levels l
WHERE SPLIT_PART('/0001/0002/0004/0005/0006/0009/', '/', l.lvl + 1) != ''
ORDER BY l.lvl;
```

### Query Pattern 3: Formatted Tree Output

```sql
SELECT 
  emp_id,
  REPEAT('  ', (LENGTH(path) - LENGTH(REPLACE(path, '/', '')) - 2)) || 
    CASE WHEN (LENGTH(path) - LENGTH(REPLACE(path, '/', '')) - 1) > 1 THEN '└─ ' ELSE '' END || 
    name AS tree_view,
  (LENGTH(path) - LENGTH(REPLACE(path, '/', '')) - 1) AS level
FROM org_path
ORDER BY path;
```

> ⚠️ **Note**: The depth formula `(LENGTH(path) - LENGTH(REPLACE(path, '/', '')) - 1)` counts `/` characters and works for both LPAD-padded paths (`/0001/`) and unpadded paths (`/1/`). Using LPAD padding is recommended to ensure `ORDER BY path` sorts correctly.

**Output**:

```
emp_id | tree_view
-------+-----------------------
1      | CEO
2      |   └─ VP Eng
4      |     └─ Eng Lead
5      |       └─ Senior Dev
6      |         └─ Junior Dev
9      |           └─ Intern
3      |   └─ VP Sales
7      |     └─ Sales Lead
8      |       └─ Sales Rep
10     |   └─ VP Product
```

### Query Pattern 4: Find Direct Children

```sql
-- Find direct reports of VP Eng (emp_id=2)
SELECT emp_id, name
FROM org_path
WHERE path LIKE '/0001/0002/%'
  AND emp_id != 2
  AND (LENGTH(path) - LENGTH(REPLACE(path, '/', '')) - 1) = 3;  -- parent depth + 1
```

### Pros and Cons

| Pros | Cons |
|---|---|
| Single table, flexible queries | Requires maintaining the path column |
| Subtree queries use only `LIKE` | Moving a subtree requires updating all descendant paths |
| Natural sort order preserves hierarchy | Path length is limited by VARCHAR size |

---

## Approach 3: Closure Table

### Best For

- Frequent hierarchy queries (e.g., permission checks, reporting line lookups)
- Acceptable additional storage overhead
- Efficient hierarchical aggregation is needed

### Table Design

```sql
-- Original adjacency list
CREATE TABLE org (
  emp_id BIGINT,
  name VARCHAR,
  manager_id BIGINT
);

-- Closure table: stores all (ancestor, descendant, depth) relationships
CREATE TABLE org_closure (
  ancestor BIGINT,    -- Ancestor node ID
  descendant BIGINT,  -- Descendant node ID
  depth INT           -- Hierarchy depth (0 = self)
);
```

### Building the Closure Table (SQL Expansion)

```sql
-- Expand all hierarchy relationships through repeated self-JOINs
WITH 
l0 AS (SELECT emp_id AS ancestor, emp_id AS descendant, 0 AS depth FROM org),
l1 AS (SELECT manager_id AS ancestor, emp_id AS descendant, 1 AS depth FROM org WHERE manager_id > 0),
l2 AS (SELECT l1a.ancestor, l1b.descendant, 2 AS depth FROM l1 l1a JOIN l1 l1b ON l1a.descendant = l1b.ancestor),
l3 AS (SELECT l1a.ancestor, l2b.descendant, 3 AS depth FROM l1 l1a JOIN l2 l2b ON l1a.descendant = l2b.ancestor),
l4 AS (SELECT l1a.ancestor, l3b.descendant, 4 AS depth FROM l1 l1a JOIN l3 l3b ON l1a.descendant = l3b.ancestor),
l5 AS (SELECT l1a.ancestor, l4b.descendant, 5 AS depth FROM l1 l1a JOIN l4 l4b ON l1a.descendant = l4b.ancestor)
INSERT INTO org_closure
SELECT * FROM l0 UNION ALL SELECT * FROM l1 UNION ALL SELECT * FROM l2
UNION ALL SELECT * FROM l3 UNION ALL SELECT * FROM l4 UNION ALL SELECT * FROM l5;
```

> ⚠️ **Note**: The number of expansion levels must be greater than or equal to the maximum hierarchy depth. Each additional level requires one more JOIN CTE.

### Query Pattern 1: Find a Subtree

```sql
SELECT c.descendant, d.name, c.depth
FROM org_closure c
JOIN org d ON c.descendant = d.emp_id
WHERE c.ancestor = 1 AND c.depth > 0
ORDER BY c.depth, c.descendant;
```

### Query Pattern 2: Find the Ancestor Chain

```sql
SELECT c.ancestor, a.name, c.depth
FROM org_closure c
JOIN org a ON c.ancestor = a.emp_id
WHERE c.descendant = 9
ORDER BY c.depth;
```

### Query Pattern 3: Hierarchical Aggregation

```sql
-- Count total direct and indirect reports for each manager
SELECT 
  c.ancestor,
  a.name AS manager_name,
  COUNT(DISTINCT c.descendant) AS total_reports
FROM org_closure c
JOIN org a ON c.ancestor = a.emp_id
GROUP BY c.ancestor, a.name
ORDER BY total_reports DESC;
```

**Output**:

| ancestor | manager_name | total_reports |
|----------|--------------|---------------|
| 1        | CEO          | 10            |
| 2        | VP Eng       | 5             |
| 4        | Eng Lead     | 4             |
| 5        | Senior Dev   | 3             |

### Maintaining the Closure Table

```sql
-- Update the closure table when inserting a new node
-- Example: new employee (emp_id=11) reports to Senior Dev (emp_id=5)
INSERT INTO org_closure
SELECT c.ancestor, 11, c.depth + 1
FROM org_closure c
WHERE c.descendant = 5
UNION ALL
SELECT 11, 11, 0;  -- Self-relationship

-- Clean up the closure table when deleting a node
DELETE FROM org_closure 
WHERE descendant IN (
  SELECT descendant FROM org_closure WHERE ancestor = 6
);
```

### Pros and Cons

| Pros | Cons |
|---|---|
| Best query performance (single JOIN) | Requires additional storage for the closure table |
| Supports efficient hierarchical aggregation | Inserts and deletes require maintaining closure relationships |
| No depth limit | Moving a subtree requires bulk updates |

---

## Approach Comparison Summary

| Dimension | Fixed-Depth JOIN | Materialized Path | Closure Table |
|---|---|---|---|
| Schema changes | None | Add `path` column | Add closure table |
| Write complexity | Low | Medium | High |
| Subtree query | Multiple JOINs | `LIKE` single-table scan | Single JOIN |
| Ancestor query | Multiple LEFT JOINs | `SPLIT_PART` expansion | Single WHERE |
| Hierarchical aggregation | Complex | Medium | Simple |
| Moving a subtree | Change `manager_id` | Update all descendant paths | Bulk update closure |
| Best for | One-off analytical queries | Moderate-frequency queries | High-frequency permission/reporting queries |

---

## Common Issues

### 1. Incorrect Path Lexicographic Order

```sql
-- Wrong: /1/10/ sorts before /1/2/
path = '/1/10/'  -- lexicographic order < '/1/2/'

-- Correct: pad with LPAD
path = '/0001/0010/'  -- lexicographic order > '/0001/0002/'
```

### 2. Insufficient Closure Table Expansion Levels

If the maximum depth is 6 but you only expand to l4, relationships at levels 5 and 6 will be missing. Expand to at least the expected maximum depth + 1.

### 3. Moving a Subtree with the Path Method

```sql
-- Wrong: only updating manager_id without updating the path
UPDATE org_path SET manager_id = 3 WHERE emp_id = 4;

-- Correct: update both the node and all descendant paths
UPDATE org_path 
SET path = REPLACE(path, '/0001/0002/', '/0001/0003/')
WHERE path LIKE '/0001/0002/%';
```

### 4. `WITH RECURSIVE` Is Not Supported

```sql
-- Not supported
WITH RECURSIVE tree AS (...) SELECT * FROM tree;

-- Alternative: use one of the three approaches in this guide
```

---

## Real-World Application: Product Category Tree

```sql
-- Product category table (Materialized Path approach)
CREATE TABLE product_category (
  category_id BIGINT,
  name VARCHAR,
  parent_id BIGINT,
  path VARCHAR,
  sort_order INT
);

-- Query all products under a category (including subcategories)
SELECT p.*
FROM products p
JOIN product_category c ON p.category_id = c.category_id
WHERE c.path LIKE (
  SELECT path FROM product_category WHERE category_id = 100
) || '%'
ORDER BY c.path, p.sort_order;
```

## Real-World Application: BOM Bill of Materials

```sql
-- BOM closure table
CREATE TABLE bom_closure (
  parent_part_id BIGINT,
  child_part_id BIGINT,
  depth INT,
  quantity DECIMAL(10,2)  -- Quantity per level
);

-- Calculate total raw material quantities needed for a finished product
SELECT 
  bc.child_part_id,
  p.name AS part_name,
  SUM(bc.quantity) AS total_quantity
FROM bom_closure bc
JOIN parts p ON bc.child_part_id = p.part_id
WHERE bc.parent_part_id = 1001  -- Finished product ID
  AND bc.depth > 0
GROUP BY bc.child_part_id, p.name;
```
