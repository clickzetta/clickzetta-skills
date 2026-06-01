# View Materialized View Structure (DESC MATERIALIZED VIEW)

## Description

The `DESC` command is used to view the column structure of a materialized view, including field names, data types, and comments. `DESC EXTENDED` can further display detailed metadata of the materialized view, such as creation time, query definition, source table information, and more.

For more details, see [Materialized View](materializedview.md).

## Syntax

```Plain
DESC [EXTENDED] [schema_name.]<mv_name>
```

## Parameter Description

| Parameter | Required | Description |
|---|---|---|
| `EXTENDED` | No | Display extended information, including materialized view metadata, query definition, source tables, and other details |
| `schema_name` | No | The name of the schema. If not specified, the current schema is used by default |
| `mv_name` | Yes | The name of the materialized view to view |

## Return Column Description

### Basic Mode (without EXTENDED)

| Column Name | Description |
|---|---|
| `column_name` | Column name |
| `data_type` | Data type |
| `comment` | Column comment |

### Extended Mode (with EXTENDED)

After the basic column information, the following metadata rows are also returned:

| Field | Description |
|---|---|
| `workspace` | Workspace name |
| `schema` | Schema name |
| `name` | Materialized view name |
| `creator` | Creator |
| `created_time` | Creation time |
| `last_modified_time` | Last modified time |
| `type` | Object type, value is `MATERIALIZED VIEW` |
| `view_text` | The full query statement of the materialized view (with schema prefix) |
| `view_original_text` | The original query statement of the materialized view |
| `is_materialized` | Whether it has been materialized, value is `true` |
| `source_tables` | List of dependent source tables |
| `format` | Storage format, e.g., `PARQUET` |
| `statistics` | Data statistics (row count and bytes) |

## Examples

### Example 1: View the column structure of a materialized view

```SQL
DESC doc_test.mv_test_sales;
```

Result:

```
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| id          | int       |         |
| name        | string    |         |
+-------------+-----------+---------+
```

### Example 2: View extended information of a materialized view

```SQL
DESC EXTENDED doc_test.mv_test_sales;
```

Result (partial):

```
+------------------------------+------------------------------------------+---------+
| column_name                  | data_type                                | comment |
+------------------------------+------------------------------------------+---------+
| id                           | int                                      |         |
| name                         | string                                   |         |
|                              |                                          |         |
| # detailed table information |                                          |         |
| workspace                    | quick_start                              |         |
| schema                       | doc_test                                 |         |
| name                         | mv_test_sales                            |         |
| creator                      | qiliang                                  |         |
| type                         | MATERIALIZED VIEW                        |         |
| view_original_text           | SELECT id, name FROM doc_test.employees; |         |
| is_materialized              | true                                     |         |
| format                       | PARQUET                                  |         |
| statistics                   | 5 rows 2610 bytes                        |         |
+------------------------------+------------------------------------------+---------+
```

## Notes

- `DESC` is equivalent to `DESCRIBE`; the two can be used interchangeably.
- The `DESC` syntax for materialized views is the same as for regular tables. See [DESC TABLE](desc-table.md) for details.
- The `source_tables` field returned by `DESC EXTENDED` records all source tables that the materialized view depends on, which can be used for data lineage analysis.

## Related Commands

- [DESC TABLE](desc-table.md): View regular table structure
- [SHOW TABLES WHERE is_materialized_view=true](show-materialized-view.md): List all materialized views
- [REFRESH MATERIALIZED VIEW](refresh-materialized-view.md): Refresh a materialized view
