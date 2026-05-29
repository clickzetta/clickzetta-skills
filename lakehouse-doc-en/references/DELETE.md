# DELETE

Deletes one or more rows from a specified table. Supports filtering target rows precisely using a `WHERE` clause, as well as subqueries as the delete condition.

## Syntax

```Plain
DELETE FROM table_name
[WHERE condition]
```

## Parameter Description

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `table_name` | Identifier | Required | The name of the target table from which to delete data. Can include a schema prefix, e.g., `schema_name.table_name` |
| `WHERE condition` | Expression | Optional | Filter condition, supporting comparison operators, logical operators, subqueries, etc. **When omitted, deletes all rows in the table** |

## Examples

### Example 1: Delete Rows by Condition

Delete all products in the `doc_test.products` table where `category` is `'Furniture'`:

```SQL
DELETE FROM doc_test.products
WHERE category = 'Furniture';
```

Verify after execution:

```SQL
SELECT * FROM doc_test.products;
```

```
product_id | name   | price   | stock | category
-----------+--------+---------+-------+------------
1          | Laptop | 5999.00 | 50    | Electronics
2          | Phone  | 2999.00 | 120   | Electronics
5          | Tablet | 3499.00 | 60    | Electronics
```

The original 2 Furniture records (Desk, Chair) have been deleted, leaving 3 Electronics records.

### Example 2: Use a Subquery as the Delete Condition

Delete all employees in the `doc_test.employees` table where `is_active = false`:

```SQL
DELETE FROM doc_test.employees
WHERE id IN (
    SELECT id FROM doc_test.employees WHERE is_active = false
);
```

Verify after execution:

```SQL
SELECT * FROM doc_test.employees;
```

```
id | name    | dept        | salary   | hire_date  | is_active
---+---------+-------------+----------+------------+----------
1  | Alice   | Engineering | 12000.00 | 2021-03-15 | true
2  | Bob     | Marketing   | 8500.00  | 2020-07-01 | true
3  | Charlie | Engineering | 11000.00 | 2022-01-10 | true
5  | Eve     | Marketing   | 9000.00  | 2023-05-08 | true
```

The employee Diana (id=4) with `is_active = false` has been deleted.

### Example 3: Delete All Rows in a Table

Omitting the `WHERE` clause deletes all rows in the table, effectively clearing it. In practice, using `WHERE 1=1` is recommended to explicitly express intent (some client tools may warn or refuse to execute a DELETE without WHERE):

```SQL
DELETE FROM doc_test.products WHERE 1=1;
```

Verify after execution:

```SQL
SELECT COUNT(*) AS row_count FROM doc_test.products;
```

```
row_count
---------
0
```

All rows in the table have been deleted, but the table structure is preserved.

## DELETE vs. TRUNCATE

| Comparison | DELETE | TRUNCATE |
|------------|--------|----------|
| Syntax | `DELETE FROM table [WHERE ...]` | `TRUNCATE TABLE table` |
| Supports WHERE condition | Yes, precise filtering | No, always clears the entire table |
| Operation granularity | Row-by-row deletion | Whole-table clearance |
| Typical scenario | Delete partial rows by condition | Quickly clear the entire table |

If the goal is to clear the entire table, use `TRUNCATE TABLE` for clearer semantics.

## Notes

- **The WHERE clause is optional, but omitting it deletes all rows in the table**. Always verify the condition before execution.
- DELETE operations are irreversible. It is recommended to use a `SELECT` statement to verify the rows filtered by the WHERE condition before executing DELETE.
- Executing DELETE requires **DELETE permission** on the target table.
- Subqueries are supported as WHERE conditions, and subqueries can reference other tables.
- Some client tools (such as cz-cli) have safety interception for DELETE without WHERE; use `WHERE 1=1` or the corresponding parameter to bypass.
