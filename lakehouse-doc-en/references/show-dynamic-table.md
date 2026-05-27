# List Dynamic Tables Command Documentation

## Description
`SHOW TABLES` is an SQL command used to display a list of all tables in the database. When combined with the condition `WHERE is_dynamic=true`, this command is specifically used to list all dynamic tables.

## Syntax

### Basic Syntax
```SQL
SHOW TABLES [IN schema_name] WHERE is_dynamic=true;
```
### Parameter Description

* **schema\_name**: (Optional) Specifies the name of the schema whose tables are to be listed. If specified, the command will only list dynamic tables within the specified schema.
* **is\_dynamic**: A boolean condition used to filter dynamic tables.

## Example

List all dynamic tables
```SQL
SHOW TABLES WHERE is_dynamic=true;
+-------------+--------------+---------+----------------------+-------------+------------+
| schema_name |  table_name  | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+--------------+---------+----------------------+-------------+------------+
| public      | aa           | false   | false                | false       | true       |
| public      | base_a_dt    | false   | false                | false       | true       |
| public      | base_a_dt01  | false   | false                | false       | true       |
| public      | change_table | false   | false                | false       | true       |
| public      | dt_agg       | false   | false                | false       | true       |
| public      | dt_line      | false   | false                | false       | true       |
| public      | dt_tran      | false   | false                | false       | true       |
+-------------+--------------+---------+----------------------+-------------+------------+

```
List all dynamic tables under a specific schema
```SQL
SHOW TABLES IN public WHERE is_dynamic=true;
+-------------+--------------+---------+----------------------+-------------+------------+
| schema_name |  table_name  | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+--------------+---------+----------------------+-------------+------------+
| public      | aa           | false   | false                | false       | true       |
| public      | base_a_dt    | false   | false                | false       | true       |
| public      | base_a_dt01  | false   | false                | false       | true       |
| public      | change_table | false   | false                | false       | true       |
| public      | dt_agg       | false   | false                | false       | true       |
| public      | dt_line      | false   | false                | false       | true       |
| public      | dt_tran      | false   | false                | false       | true       |
+-------------+--------------+---------+----------------------+-------------+------------+
```
Using where condition to filter
```
SHOW TABLES IN public WHERE table_name='aa';
+-------------+------------+---------+----------------------+-------------+------------+
| schema_name | table_name | is_view | is_materialized_view | is_external | is_dynamic |
+-------------+------------+---------+----------------------+-------------+------------+
| public      | aa         | false   | false                | false       | true       |
+-------------+------------+---------+----------------------+-------------+------------+
```

^
