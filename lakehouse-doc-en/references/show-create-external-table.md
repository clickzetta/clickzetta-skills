# View Object Creation Statement (SHOW CREATE TABLE)

## Description

The `SHOW CREATE TABLE` command is used to obtain the DDL creation statement of a specified Lakehouse object, supporting regular tables, external tables, materialized views, dynamic tables, and views.

## Syntax

```Plain
SHOW CREATE TABLE [schema_name.]<object_name>
```

## Parameters

| Parameter | Required | Description |
|---|---|---|
| `schema_name` | No | Specifies the schema name. If not specified, defaults to the current schema |
| `object_name` | Yes | The name of the object to query, which can be a table, external table, materialized view, dynamic table, or view |

## Return Columns

| Column | Description |
|---|---|
| `sql` | The complete DDL creation statement of the object, including workspace and schema prefixes |

## Examples

### Example 1: View the Creation Statement of an External Table

```SQL
SHOW CREATE TABLE doc_test.ext_orders_v2;
```

Result:

```
+------------------------------------------------------------------+
| sql                                                              |
+------------------------------------------------------------------+
| CREATE EXTERNAL TABLE quick_start.doc_test.ext_orders_v2(       |
|   `order_id` int,                                                |
|   `customer_id` int,                                             |
|   `amount` decimal(10,2))                                        |
| USING PARQUET                                                    |
| LOCATION "oss://czlakehouse/doc_test/orders/"                    |
| CONNECTION quick_start.oss_sh_conn_ak                            |
| COMMENT 'External orders table'                                  |
| TBLPROPERTIES(                                                   |
|   'key1'='value1');                                              |
+------------------------------------------------------------------+
```

### Example 2: View the Creation Statement of a Materialized View

```SQL
SHOW CREATE TABLE doc_test.mv_test_sales;
```

Result:

```
+------------------------------------------------------------------+
| sql                                                              |
+------------------------------------------------------------------+
| CREATE MATERIALIZED VIEW quick_start.doc_test.mv_test_sales(    |
|   `id` ,                                                         |
|   `name` )                                                       |
| REFRESH ON DEMAND                                                |
| USING PARQUET                                                    |
| AS SELECT id, name FROM doc_test.employees;                      |
+------------------------------------------------------------------+
```

### Example 3: View the Creation Statement of a Regular View

```SQL
SHOW CREATE TABLE doc_test.v_test_employees;
```

Result:

```
+------------------------------------------------------------------+
| sql                                                              |
+------------------------------------------------------------------+
| CREATE VIEW quick_start.doc_test.v_test_employees(              |
|   `id` ,                                                         |
|   `name` )                                                       |
| AS SELECT 1 AS id, 'Alice' AS name                               |
| ;                                                                |
+------------------------------------------------------------------+
```

## Notes

- The returned DDL statement includes the full three-level namespace of `workspace.schema.object_name`, and can be used directly to recreate the object in another workspace or schema (with the corresponding namespace modified).
- For external tables, the returned statement includes `LOCATION` and `CONNECTION` information. When migrating, ensure that the corresponding connection configuration exists in the target environment.
- This command does not support viewing creation statements for regular internal tables; it only supports external tables, views, materialized views, and dynamic tables.

## Related Commands

- [CREATE EXTERNAL TABLE](create-external-table.md): Create an external table
- [CREATE VIEW](create-view.md): Create a view
- [CREATE MATERIALIZED VIEW](create-materialized-view.md): Create a materialized view
- [SHOW TABLES WHERE is_external=true](show-external-table.md): List all external tables
