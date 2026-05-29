# View Dynamic Table Structure (DESC DYNAMIC TABLE)

## Description

The `DESC` command is used to view the structural information of a Dynamic Table. By default, it returns only column names, data types, and comments. Adding the `EXTENDED` keyword reveals the full table metadata, including refresh configuration, source tables, query definitions, and more.

## Syntax

```sql
DESC [TABLE] [EXTENDED] <dt_name>;
-- or
DESCRIBE [TABLE] [EXTENDED] <dt_name>;
```

### Parameter Description

| Parameter | Description |
|-----------|-------------|
| `DESC` / `DESCRIBE` | Both are equivalent and interchangeable |
| `TABLE` | Optional keyword |
| `EXTENDED` | Optional. When specified, returns full table metadata |
| `dt_name` | The name of the dynamic table, which may include a schema prefix |

## Usage Examples

### Example 1: View column structure of a dynamic table

```sql
DESC dt_agg;
+-------------+-----------+---------+
| column_name | data_type | comment |
+-------------+-----------+---------+
| j           | int       | NULL    |
| cnt         | bigint    | NULL    |
+-------------+-----------+---------+
```

### Example 2: View full information of a dynamic table

```sql
DESC EXTENDED dt_agg;
+------------------------+-------------------------------------------+
| column_name            | data_type                                 |
+------------------------+-------------------------------------------+
| j                      | int                                       |
| cnt                    | bigint                                    |
|                        |                                           |
| # detailed table info  |                                           |
| workspace              | quick_start                               |
| schema                 | public                                    |
| name                   | dt_agg                                    |
| creator                | qiliang                                   |
| created_time           | 2024-07-23 18:02:15.774                   |
| last_modified_time     | 2024-07-24 11:01:11.289                   |
| comment                | NULL                                      |
| properties             | ()                                        |
| type                   | DYNAMIC TABLE                             |
| view_text              | SELECT j, COUNT(*) AS cnt FROM dt_tran... |
| view_original_text     | (select j,count(*) as cnt from dt_tran...) |
| source_tables          | [...]                                     |
| refresh_type           | on schedule                               |
| refresh_start_time     | 2024-07-23 18:02:15.725                   |
| refresh_interval_second| 60                                        |
| refresh_vcluster       | quick_start.DEFAULT                       |
| format                 | PARQUET                                   |
| statistics             | 5 rows 2729 bytes                         |
+------------------------+-------------------------------------------+
```

Key fields returned in `EXTENDED` mode:

| Field | Description |
|-------|-------------|
| `type` | Object type; dynamic tables display `DYNAMIC TABLE` |
| `view_text` | The query definition of the dynamic table (formatted) |
| `view_original_text` | The original query definition |
| `source_tables` | List of source tables |
| `refresh_type` | Refresh type (`on schedule` indicates scheduled refresh) |
| `refresh_interval_second` | Refresh interval in seconds |
| `refresh_vcluster` | The compute cluster used for refreshes |
| `refresh_start_time` | The start time for refreshes |
| `format` | Storage format (typically `PARQUET`) |
| `statistics` | Row count and byte count statistics |

## Notes

- Without `EXTENDED`, only column structure is returned (column name, data type, comment).
- With `EXTENDED`, full metadata is returned, including refresh configuration, source tables, query definitions, etc.
- Dynamic tables do not support `DESC TABLE ... HISTORY` syntax. Use `DESC HISTORY <dt_name>` to view historical versions.

## Related Documents

- [CREATE DYNAMIC TABLE](create-dynamic-table.md)
- [DESC HISTORY](desc-history.md)
- [SHOW DYNAMIC TABLE REFRESH HISTORY](refresh-history.md)
