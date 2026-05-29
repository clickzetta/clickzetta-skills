## Build Index

Builds an index on existing data in a table. Currently, inverted indexes and vector indexes are supported. Bloom filters are not supported.

## Syntax

```SQL
-- Syntax 1: Build an index on all existing data in the table
BUILD INDEX index_name ON [schema.]table_name;

-- Syntax 2: Build an index only on specified partitions. Supports =, !=, >, >=, <, <= operators.
BUILD INDEX index_name ON [schema.]table_name
  WHERE partition_col1 = 'value1' [AND partition_col2 = 'value2' ...];
```

## Parameter Description

| Parameter | Required | Description |
|------|------|------|
| `index_name` | Yes | The name of the index to build. The index must have been defined previously via `CREATE INVERTED INDEX` or during table creation. |
| `schema` | No | The schema name where the table resides. If not specified, the current schema is used. |
| `table_name` | Yes | The name of the target table. |
| `WHERE` clause | No | Specifies partition conditions. The index is built only on matching partitions. One or more partition columns can be specified. |

## Description

`CREATE INVERTED INDEX` only takes effect for data written after the index is created; existing data is not automatically indexed. Executing `BUILD INDEX` retroactively builds the index on existing data.

`BUILD INDEX` is an asynchronous task. It returns immediately after submission, and the actual build process runs in the background, consuming compute resources. You can monitor the build progress via `SHOW JOBS` or the Job Profile.

## Examples

1. Build an inverted index on all existing data in the `doc_test.employees` table:

First, confirm that the index exists:

```SQL
SHOW INDEX FROM doc_test.employees;
```

```
+---------------+------------+
| index_name    | index_type |
+---------------+------------+
| idx_emp_name  | inverted   |
+---------------+------------+
```

Then build the index on the existing data (switch to the corresponding schema first):

```SQL
USE SCHEMA doc_test;
BUILD INDEX idx_emp_name ON doc_test.employees;
```

2. Build an index on a specified partition of a partitioned table:

```SQL
BUILD INDEX order_year_index ON public.t WHERE order_year = '2023';
```

3. Build an index with multiple partition conditions:

```SQL
BUILD INDEX order_year_index ON public.t
  WHERE order_year = '2023' AND order_month = '01';
```

## Notes

- After submission, `BUILD INDEX` runs asynchronously. Use `SHOW JOBS` to check the task status.
- Building an index on a table with a large data volume consumes significant compute resources. It is recommended to execute during off-peak hours.
- For partitioned tables, it is recommended to build indexes in batches by partition to avoid oversized single tasks.
- Index names must be unique within a schema. The `index_name` used with `BUILD INDEX` does not require a schema prefix, but ensure that the current schema matches the table's schema, or switch schemas using `USE SCHEMA`.
- Related commands: [Create Inverted Index](create-inverted-index.md), [Show Index](SHOW-INDEX.md), [Drop Index](DROP-INDEX.md)
