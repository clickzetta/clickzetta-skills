# Unique Key (UNIQUE) in Lakehouse

## Overview

> **Important difference from traditional databases**
>
> The UNIQUE constraint in Singdata Lakehouse is an **informational constraint (declarative constraint)**, and its behavior differs fundamentally from traditional databases such as MySQL and PostgreSQL:
>
> - **Uniqueness is not enforced by default**: In the default mode (`DISABLE NOVALIDATE RELY`), the system does not validate uniqueness during SQL writes — duplicate values can be written normally.
> - **Primary purpose is query optimization**: The UNIQUE constraint is mainly used to declare the data semantics of a column (or set of columns) to the query optimizer, helping it produce better execution plans for deduplication elimination, row count estimation, and join optimization.
> - **Application layer must enforce uniqueness**: If strict uniqueness is required by the business, it must be guaranteed by the data writer — you cannot rely on the UNIQUE constraint to enforce it.

The `UNIQUE` constraint declares that the values in one column or a combination of columns in a table are unique. Unlike a primary key (`PRIMARY KEY`), a UNIQUE constraint:

- Allows NULL values in columns (primary key columns enforce NOT NULL);
- Allows multiple UNIQUE constraints on a single table (only one primary key is allowed);
- Is not used as the operation key for real-time writes (CDC UPSERT/DELETE).

A UNIQUE constraint can only be specified at table creation (`CREATE TABLE`). **Adding it via `ALTER TABLE` is not supported.**

## Syntax

The UNIQUE constraint supports both column-level and table-level syntax, and both forms can include constraint modifiers.

### Column-level syntax

```sql
CREATE TABLE t (
    id int UNIQUE,
    name string
);
```

### Table-level syntax

Table-level syntax supports single-column and multi-column composite unique keys:

```sql
-- Single column
CREATE TABLE t (
    id int,
    name string,
    UNIQUE(id)
);

-- Composite unique key
CREATE TABLE t (
    a int,
    b int,
    UNIQUE(a, b)
);
```

### Constraint modifiers

The UNIQUE constraint supports three groups of modifiers in a fixed order (consistent with PRIMARY KEY and FOREIGN KEY):

```
UNIQUE [ENABLE | DISABLE] [VALIDATE | NOVALIDATE] [RELY | NORELY]
```

| Modifier | Meaning | Default |
|----------|---------|---------|
| `ENABLE` / `DISABLE` | Whether to enforce validation on subsequent writes | `DISABLE` |
| `VALIDATE` / `NOVALIDATE` | Whether existing data is required to satisfy the constraint | `NOVALIDATE` |
| `RELY` / `NORELY` | Whether the optimizer trusts and uses this constraint for query optimization | `RELY` |

When no modifiers are specified, the default behavior of a UNIQUE constraint is **`DISABLE NOVALIDATE RELY`**.

## Default behavior: declarative constraint (no deduplication)

In the default `DISABLE NOVALIDATE RELY` mode, the UNIQUE constraint is recorded only as metadata and **does not prevent duplicate values from being written**:

```sql
CREATE TABLE uk_demo (id int UNIQUE, name string);

-- View the constraint
DESC EXTENDED uk_demo;
-- unique_keys: ((id) DISABLE NOVALIDATE RELY)

-- Duplicate id values can both be written
INSERT INTO uk_demo VALUES(1, 'a');
INSERT INTO uk_demo VALUES(1, 'b');

SELECT * FROM uk_demo;
-- 1 | a
-- 1 | b   (duplicate value was not blocked)

-- Multiple NULLs are allowed
INSERT INTO uk_demo VALUES(NULL, 'c');
INSERT INTO uk_demo VALUES(NULL, 'd');
-- Both writes succeed
```

## RELY and the optimizer

`RELY` (the default) tells the optimizer it can trust the constraint and optimize queries based on it, even if the constraint is not enforced during writes. The optimizer uses RELY unique keys for:

- Deduplication elimination (simplification of DISTINCT / GROUP BY);
- Row count and NDV (number of distinct values) estimation;
- Join cardinality estimation and plan selection.

If the data does not actually satisfy uniqueness but the constraint is declared as RELY, the optimizer may produce incorrect results. In this case, use `NORELY` to tell the optimizer to ignore the constraint:

```sql
CREATE TABLE uk_demo (id int UNIQUE NORELY, name string);
-- unique_keys: ((id) DISABLE NOVALIDATE NORELY)
```

## Actual behavior of modifier combinations

The following table shows observed behavior for each modifier combination:

| Declaration | DESC EXTENDED shows | Write behavior |
|-------------|---------------------|----------------|
| `UNIQUE` (default) | `DISABLE NOVALIDATE RELY` | Duplicates allowed, multiple NULLs allowed |
| `UNIQUE ENABLE` | `ENABLE NOVALIDATE RELY` | Duplicates allowed (no VALIDATE means no check) |
| `UNIQUE NORELY` | `DISABLE NOVALIDATE NORELY` | Duplicates allowed; optimizer ignores constraint |
| Multiple `UNIQUE` | Each is `DISABLE NOVALIDATE RELY` | Allowed |

> ⚠️ **Enforced uniqueness (`ENABLE VALIDATE`) is currently not usable**
>
> When `UNIQUE ... ENABLE VALIDATE` is declared, table creation succeeds (DESC shows `ENABLE VALIDATE RELY` and HASH bucketing with sort keys is auto-generated), but executing `INSERT` on the table produces a compiler error:
>
> ```
> CZLH-65000: ... Table should have primary keys/unique keys
> ```
>
> This limitation is unrelated to whether the column is declared NOT NULL. **If you need to enforce deduplication at write time, use a primary key (PRIMARY KEY) rather than a UNIQUE constraint.** See [Primary Key](primary-key.md) for details.

## Relationship with PRIMARY KEY

- A table's primary key is also recorded as a unique key, so `DESC EXTENDED`'s `unique_keys` field will include the primary key columns.
- A table can define both a primary key and multiple (non-enforced) UNIQUE constraints.
- A table **can have at most one enforced constraint**. If the primary key is already enforced (which is the default), declaring `UNIQUE ... ENABLE VALIDATE` will produce an error at table creation:

```sql
CREATE TABLE t (id int PRIMARY KEY, code int UNIQUE ENABLE VALIDATE);
-- CZLH-42000: cannot enforce UNIQUE constraint with an enforced PRIMARY KEY
```

| Comparison | PRIMARY KEY | UNIQUE |
|------------|-------------|--------|
| Count per table | At most 1 | Multiple allowed |
| Column nullability | Enforces NOT NULL | Allows NULL (multiple NULLs allowed) |
| Real-time write (CDC) dedup key | Yes | No |
| Default modifiers | `ENABLE VALIDATE RELY` | `DISABLE NOVALIDATE RELY` |
| Primary purpose | CDC dedup + query optimization | Query optimization (declarative) |

## Validation rules at table creation

The system performs the following checks on UNIQUE constraints when creating a table:

- **No duplicate column names within a single constraint**: `UNIQUE(a, a)` produces an error.
- **No redundant constraints**: If a UNIQUE constraint is identical to the primary key, or is a superset of another unique key (or the primary key), an `unnecessary unique key` error is reported.
- **At most one enforced constraint**: Multiple `ENABLE VALIDATE` constraints (including the primary key) produce an error.

## Usage recommendations

- Treat UNIQUE as a **hint to the optimizer**: If you know that a column is unique in practice (for example, a business primary key synced from an upstream system), declaring UNIQUE can help the optimizer generate better plans.
- If the declared column may actually contain duplicates, use `NORELY` to prevent the optimizer from making incorrect simplifications based on the constraint.
- When you need to **truly enforce deduplication at write time**, use a primary key (PRIMARY KEY) together with a real-time write interface — not a UNIQUE constraint.

## References

- [Primary Key](primary-key.md)
- [CREATE TABLE Syntax](create-table-ddl.md)
