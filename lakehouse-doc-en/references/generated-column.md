# Generated Column

## Generated Column

A Generated Column is a column in a Lakehouse table whose value is automatically computed from other columns in the table via an expression. The computation rule is defined at creation time and the system maintains the column value automatically — no explicit insert or update is required. Common use cases include performing field transformations at the database layer during data integration sync, or extracting JSON fields into standalone columns and building indexes to accelerate queries.

Generated columns support two storage modes:

| Mode | Keyword | Description |
| --- | --- | --- |
| **VIRTUAL** (default) | Omit or write `VIRTUAL` | Not written to Parquet files; computed dynamically at query time. No extra storage overhead. |
| **STORED** | `STORED` | Materialized into Parquet files at write time. Queries read the column directly; the optimizer can reuse it; supports CLUSTER BY. |

## Syntax

```sql
CREATE TABLE [ IF NOT EXISTS ] table_name
(
    column_definition,
    -- VIRTUAL (default): not written to file, computed at read time
    col_name data_type GENERATED ALWAYS AS ( expr ) [VIRTUAL],
    -- STORED: materialized at write time
    col_name data_type GENERATED ALWAYS AS ( expr ) STORED,
    [column_definition, ...]
)
[ PARTITIONED BY (column_name column_type | column_name) ];
```

**GENERATED ALWAYS AS (expr)**: Automatically generates the column value via expression `expr`. Expressions support constants and built-in deterministic scalar functions. The following are not supported:

* Non-deterministic functions: `current_date()`, `current_timestamp()`, `rand()`, etc.
* Aggregate functions: `sum()`, `count()`, `avg()`, etc.
* Window functions: `row_number()`, `rank()`, etc.
* Subqueries
* Self-references or circular dependencies

Using a generated column as a partition column is supported.

**Examples**:

```sql
-- VIRTUAL generated column (default): not persisted to disk, computed at read time
CREATE TABLE t_virtual (
    col1 TIMESTAMP,
    hour_col INT    GENERATED ALWAYS AS (hour(col1)),
    pt      STRING  GENERATED ALWAYS AS (date_format(col1, 'yyyy-MM-dd'))
) PARTITIONED BY (pt);

-- STORED generated column: materialized at write time, supports CLUSTER BY
CREATE TABLE t_stored (
    col1   INT,
    col2   INT GENERATED ALWAYS AS (col1 + 1) STORED
) CLUSTERED BY (col2) SORTED BY (col2) INTO 8 BUCKETS;

-- JSON extraction + inverted index (typical VIRTUAL use case)
CREATE TABLE t_json (
    id      INT,
    payload JSON,
    level   STRING GENERATED ALWAYS AS (json_extract_string(payload, '$.level')),
    INDEX idx_level(level) USING INVERTED
) USING PARQUET;
```

### Difference Between Generated Columns and Default Values

| Comparison | Default Value (DEFAULT) | Generated Column (GENERATED ALWAYS AS) |
| --- | --- | --- |
| Partition column support | Not supported | Supported |
| Non-deterministic functions | Supported (e.g. `current_timestamp()`) | Not supported |
| Can a value be specified at insert time? | Yes; if not specified, the default value is used | No; the value is entirely determined by the expression |
| Source of column value | Static constant or non-deterministic function | Computed result from other columns |
| Behavior of existing rows after ALTER TABLE ADD | Existing rows have the column filled with NULL | VIRTUAL: computed by expression at read time, immediately visible; STORED: existing rows are NULL (old files are not re-materialized) |

### Restrictions

* An explicit value cannot be specified for a generated column at insert time; doing so raises error `insert.generated.column`. Exception: specifying a static value for a partition field does not raise an error, but the specified value has no effect — the query result is still determined by the expression (Hive syntax compatibility).
* Writing via real-time interfaces and batch interfaces is not supported (including bulk import and real-time write in Studio data integration).
* A VIRTUAL generated column cannot be used in `CLUSTER BY` / `SORTED BY`; use STORED mode instead.
* Generated columns are not supported in column definitions of Dynamic Tables or materialized views.
* When executing `DROP COLUMN`, if the column being dropped is referenced by another generated column, error `column.dependency` is raised. Delete the dependent column first.

### Inserting Data

When inserting, provide only the base columns; generated columns are maintained automatically by the system:

```sql
-- Correct: insert only col1; pt is computed automatically by the expression
INSERT INTO t_virtual (col1) VALUES (TIMESTAMP '2024-09-26 10:00:00');

-- Incorrect: explicitly specifying a generated column value raises insert.generated.column
INSERT INTO t_virtual (col1, pt) VALUES (TIMESTAMP '2024-09-26 10:00:00', '2024-09-26');
```

---

# Adding a Generated Column via ALTER TABLE

## Syntax

```sql
ALTER TABLE table_name ADD COLUMN
    column_name data_type GENERATED ALWAYS AS ( expr )
    [FIRST | AFTER column_name]
    [COMMENT column_comment];
```

**Notes**:

* By default, only **VIRTUAL** generated columns can be added. After adding, existing data rows are computed dynamically by the expression at query time and are immediately visible.
* Adding a **STORED** generated column requires enabling the configuration `cz.sql.alter.table.add.generated.column.enable.stored=true`. The column value in existing Parquet files will be NULL (old files are not rewritten).
* Modifying an existing regular column into a generated column is not supported (`MODIFY COLUMN` does not support `GENERATED ALWAYS AS`).

## Examples

```sql
-- Add a VIRTUAL generated column (recommended, works out of the box)
ALTER TABLE my_table ADD COLUMN
    year_col INT GENERATED ALWAYS AS (year(event_time))
    AFTER event_time;

-- After adding, year_col for existing rows is computed automatically at query time
SELECT id, event_time, year_col FROM my_table LIMIT 5;
```
