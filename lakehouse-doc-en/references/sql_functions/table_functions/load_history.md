#### LOAD_HISTORY Function

**Description**: The `LOAD_HISTORY` function is used to view the COPY job file import history of a table, with a retention period of 7 days. When executing, the Pipe uses `load_history` to avoid re-importing existing files, ensuring data uniqueness.

**Syntax**:

```SQL
load_history('schema_name.table_name')
```

**Parameters**:

* `schema_name.table_name`: Specifies the table for which to view the import history, in the format `schema_name.table_name`.

**Return Fields**:

| Field | Type | Description |
|------|------|------|
| `file_path` | STRING | Path of the imported file |
| `last_copy_time` | TIMESTAMP | Time of the most recent import operation |
| `file_size` | BIGINT | File size (bytes) |
| `status` | STRING | Import status, `LOADED` indicates success, `LOAD_FAILED` indicates failure |
| `first_error_message` | STRING | First error message encountered, `NULL` on success |

**Examples**:

Example 1: View all import history for a table

```SQL
SELECT * FROM load_history('myschema.mytable');
```

Example 2: View only successfully imported records

```SQL
SELECT file_path, last_copy_time, file_size
FROM load_history('myschema.mytable')
WHERE status = 'LOADED';
```

Example 3: View failed import records and error messages

```SQL
SELECT file_path, last_copy_time, first_error_message
FROM load_history('myschema.mytable')
WHERE status = 'LOAD_FAILED';
```

Example 4: Filter by time range

```SQL
SELECT * FROM load_history('myschema.mytable')
WHERE last_copy_time > '2026-05-01'
ORDER BY last_copy_time DESC;
```
