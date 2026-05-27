# Modify External Table (ALTER EXTERNAL TABLE)

Use the `ALTER TABLE` command to modify the metadata of an external table, including renaming, setting comments, adding/dropping columns, and modifying properties.

## Supported Operations

| Operation | External Table | Regular Table |
|------|--------|--------|
| Rename (RENAME) | Supported | Supported |
| Set Comment (SET COMMENT) | Supported | Supported |
| Add Column (ADD COLUMN) | Supported | Supported |
| Drop Column (DROP COLUMN) | Supported | Supported |
| Set Properties (SET PROPERTIES) | Supported | Supported |
| Set Location (SET LOCATION) | **Not Supported** | -- |
| Refresh Metadata (REFRESH METADATA) | **Not Supported** | -- |
| Modify Bucket/Sort Keys | **Not Supported** | Not Supported |

## Syntax

### Rename Table

```SQL
ALTER TABLE [schema.]table_name RENAME TO new_table_name;
```

### Set Table Comment

```SQL
ALTER TABLE [schema.]table_name SET COMMENT 'comment_text';
```

### Add Column

```SQL
ALTER TABLE [schema.]table_name ADD COLUMN col_name data_type [COMMENT 'comment'];
```

### Drop Column

```SQL
ALTER TABLE [schema.]table_name DROP COLUMN col_name;
```

### Set Table Properties

```SQL
ALTER TABLE [schema.]table_name SET PROPERTIES('key' = 'value' [, 'key2' = 'value2' ...]);
```

## Parameters

| Parameter | Required | Description |
|------|------|------|
| `schema` | No | The schema where the table resides. If not specified, uses the current schema |
| `table_name` | Yes | The name of the external table to modify |
| `new_table_name` | Required for RENAME | The new table name, without a schema prefix |
| `col_name` | Required for ADD/DROP COLUMN | The column name |
| `data_type` | Required for ADD COLUMN | The data type of the column |
| `key` / `value` | Required for SET PROPERTIES | Key-value pairs for table properties, currently reserved parameters |

## Examples

1. Rename the external table `ext_orders` to `ext_orders_v2`:

```SQL
ALTER TABLE doc_test.ext_orders RENAME TO ext_orders_v2;
```

2. Add a comment to an external table, and verify with `DESC EXTENDED`:

```SQL
ALTER TABLE doc_test.ext_orders_v2 SET COMMENT 'External orders table from OSS';

DESC EXTENDED doc_test.ext_orders_v2;
```

```
+------------------------------+--------------------------------------------+---------+
| column_name                  | data_type                                  | comment |
+------------------------------+--------------------------------------------+---------+
| order_id                     | int                                        |         |
| customer_id                  | int                                        |         |
| amount                       | decimal(10,2)                              |         |
|                              |                                            |         |
| # detailed table information |                                            |         |
| schema                       | doc_test                                   |         |
| name                         | ext_orders_v2                              |         |
| comment                      | External orders table from OSS             |         |
| external                     | true                                       |         |
| format                       | PARQUET                                    |         |
| location                     | "oss://czlakehouse/doc_test/orders/"       |         |
| connection                   | quick_start.oss_sh_conn_ak                 |         |
+------------------------------+--------------------------------------------+---------+
```

3. Add a column to an external table:

```SQL
ALTER TABLE doc_test.ext_orders_v2 ADD COLUMN region STRING COMMENT 'Region of the order';
```

4. Drop a column from an external table:

```SQL
ALTER TABLE doc_test.ext_orders_v2 DROP COLUMN region;
```

5. Modify the properties of an external table:

```SQL
ALTER TABLE doc_test.ext_orders_v2 SET PROPERTIES('owner' = 'data_team');
```

## Notes

- `ALTER TABLE` operations on external tables only modify the metadata within the Lakehouse and **do not affect the actual data files in the underlying storage (OSS/S3/COS)**.
- External tables **do not support** `SET LOCATION` (changing storage path) and `REFRESH METADATA` (refreshing metadata) operations. Executing these will result in a syntax error.
- `ADD COLUMN` / `DROP COLUMN` modifies the Lakehouse-side schema definition of the external table; the actual structure of the underlying files is not affected. If the underlying file format (e.g., Parquet) does not have the corresponding column, querying that column will return NULL.
- The new table name after `RENAME TO` does not need a schema prefix; the table remains in the original schema.
- For external tables in Delta/Iceberg and other formats, schema evolution should preferably be handled through the native format's Schema Evolution mechanism rather than the Lakehouse-side `ALTER TABLE`.
