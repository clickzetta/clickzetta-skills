# Row-Level Security (Row Filter)
> [Preview Release] This feature is currently in an invite-only preview stage. To use it, please contact our technical support team for assistance.

## Overview

Row-level security (Row Filter, also known as Row Access Policy) lets you bind a filter function that returns BOOLEAN to a table. The system automatically applies this function during queries and DML operations — only rows where the function returns `true` are visible to the current operation. It is commonly used for multi-tenant isolation and data permission control by user or role.

Key characteristics of row filters:

- Filter logic is encapsulated in a SQL function and can be reused across multiple tables.
- The function can use security context functions such as `current_user()` and `current_roles()` to dynamically filter based on the current login identity.
- Takes full effect for `SELECT`, `UPDATE`, `DELETE`, and aggregate queries.
- `UPDATE` / `DELETE` only affects visible rows (those that pass the filter); invisible rows are unaffected.
- Can be removed at any time via `ALTER TABLE ... DROP ROW FILTER` without affecting the underlying data.

## Usage Steps

### Step 1: Create a Filter Function

A filter function is a SQL scalar function that returns `BOOLEAN` (see [CREATE FUNCTION(SQL)](create-sql-function.md)), with parameters corresponding to the columns in the table to be evaluated.

The most typical use of row-level security is combining it with `current_user()` to filter by the current logged-in user — each user can only see rows that belong to them:

```sql
-- Each user can only see rows where the owner column equals their own login name
CREATE FUNCTION my_schema.owner_only(owner STRING)
RETURNS BOOLEAN
AS owner = current_user();
```

You can also combine `current_roles()` (which returns an array of the current user's roles) to do role-based filtering:

```sql
-- The admin role can see all rows; other users can only see rows where region = 'east'
CREATE FUNCTION my_schema.role_based(region STRING)
RETURNS BOOLEAN
AS array_contains(current_roles(), 'admin') OR region = 'east';
```

The filter condition can also be fixed logic unrelated to identity:

```sql
-- Only rows where region = 'east' are visible
CREATE FUNCTION my_schema.only_east(region STRING)
RETURNS BOOLEAN
AS region = 'east';
```

The function can also accept multiple parameters to implement multi-column combined evaluation:

```sql
-- Only rows where region = 'east' AND amount >= 200 are visible
CREATE FUNCTION my_schema.east_big(region STRING, amt INT)
RETURNS BOOLEAN
AS region = 'east' AND amt >= 200;
```

> The security context function `current_user()` returns the current logged-in username; `current_roles()` returns an array of the current user's roles (case-sensitive).

### Step 2: Bind to a Table

#### Bind at Table Creation

```sql
CREATE TABLE my_schema.docs (
    id      INT,
    owner   STRING,
    content STRING
) ROW FILTER my_schema.owner_only ON (owner);
```

#### Bind to an Existing Table

```sql
ALTER TABLE my_schema.docs SET ROW FILTER my_schema.owner_only ON (owner);
```

The columns listed in `ON (...)` are passed as arguments to the filter function in order. The column types and count must match the function definition.

> It is recommended to use **schema-qualified names** when referencing filter functions (e.g., `my_schema.owner_only`). Without schema qualification, the system resolves based on the current schema, which may result in a `function not found` error.

### Step 3: Verify the Binding

```sql
DESC EXTENDED my_schema.docs;
```

A `# Row Filter` section will appear at the end of the output:

```
# Row Filter
Function           quick_start.my_schema.owner_only
Bound Parameters   owner
```

## Behavior Examples

Using `owner_only` (based on `current_user()`) as an example, assuming the current logged-in user is `alice`:

```sql
INSERT INTO my_schema.docs VALUES
  (1, 'alice', 'alice doc'), (2, 'bob', 'bob doc'), (3, 'alice', 'another alice doc');

-- alice queries: only returns rows where owner = 'alice'
SELECT * FROM my_schema.docs ORDER BY id;
-- 1 | alice | alice doc
-- 3 | alice | another alice doc
```

The same SQL returns different data depending on who is logged in — when `bob` logs in, they only see the row with id=2. This is how row-level security dynamically filters by identity.

Row filter effects on various operations:

| Operation | Behavior |
|-----------|----------|
| `SELECT` | Returns only visible rows (rows where the filter function returns true) |
| Aggregates (`COUNT`/`SUM`, etc.) | Only aggregates visible rows |
| `UPDATE` | Only updates visible rows; invisible rows are unaffected |
| `DELETE` | Only deletes visible rows; invisible rows are retained |

For example, if `alice` executes `UPDATE my_schema.docs SET content = 'updated' WHERE id IN (1,2,3)`, only visible id=1 and id=3 are updated. Bob's id=2 is unaffected.

## Multi-Column Filter Function Example

```sql
CREATE FUNCTION my_schema.east_big(region STRING, amt INT)
RETURNS BOOLEAN
AS region = 'east' AND amt >= 200;

CREATE TABLE my_schema.o2 (id INT, region STRING, amt INT)
ROW FILTER my_schema.east_big ON (region, amt);

INSERT INTO my_schema.o2 VALUES (1,'east',100), (2,'east',300), (3,'west',300);

SELECT * FROM my_schema.o2 ORDER BY id;
-- 2 | east | 300   (only the row where region='east' AND amt>=200 is visible)
```

## Removing a Row Filter

```sql
ALTER TABLE my_schema.o2 DROP ROW FILTER;
```

After removal, all data in the table becomes visible again. The underlying data is not affected in any way.

```sql
SELECT * FROM my_schema.o2 ORDER BY id;
-- 1 | east | 100
-- 2 | east | 300
-- 3 | west | 300
```

## Notes

- The filter function must return `BOOLEAN`, and the column types and count in `ON (...)` must match the function parameters.
- Use schema-qualified names when referencing filter functions to avoid resolution failures.
- Row filters do not intercept data during writes (INSERT) — data is written to the underlying storage normally; visibility is only controlled during queries, updates, and deletes. If write-side constraints are also needed, combine with application-level logic.
- A table can have one row filter bound at a time. To rebind, run `ALTER TABLE ... SET ROW FILTER` again; to remove, use `ALTER TABLE ... DROP ROW FILTER`.

## References

- [CREATE FUNCTION(SQL)](create-sql-function.md): SQL scalar function syntax used to create filter functions
- [Column-Level Security (Dynamic Masking)](dynamic-mask.md): Column-level data protection, complementary to row-level security
- [CREATE TABLE DDL Syntax](create-table-ddl.md)
