# SHOW INDEX

Lists all indexes on the specified table.

## Syntax

```SQL
SHOW INDEX { IN | FROM } [schema.]table_name [LIMIT num];
```

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `IN \| FROM` | Yes | Keyword, both are equivalent |
| `schema` | No | The name of the Schema where the table resides. If not specified, the current Schema is used |
| `table_name` | Yes | The name of the table whose indexes to query |
| `LIMIT num` | No | Limits the number of indexes returned |

## Return Columns

| Column | Description |
|--------|-------------|
| `index_name` | The name of the index |
| `index_type` | The index type, such as `inverted` (inverted index), `bloom_filter` (Bloom filter), `vector` (vector index) |

## Examples

1. View all indexes on the `doc_test.employees` table:

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

2. View indexes on the `orders` table in the current Schema:

```SQL
SHOW INDEX FROM orders;
```

3. View indexes on a table, returning at most 5 results:

```SQL
SHOW INDEX IN doc_test.employees LIMIT 5;
```

4. If no indexes exist on the table, an empty result set is returned:

```SQL
SHOW INDEX FROM doc_test.departments;
-- Returns 0 rows
```

## Notes

- If no indexes have been created on the table, the command returns an empty result set without an error.
- Supported index types include: inverted index (`inverted`), Bloom filter (`bloom_filter`), and vector index (`vector`).
- To view index details (including indexed columns, properties, size, etc.), use the `DESC INDEX` or `DESC INDEX EXTENDED` command.
- To create an index, see [Create Inverted Index](create-inverted-index.md); to build an index on existing data, see [Build Index](build-index.md).
