# UNDROP TABLE

Use the UNDROP TABLE statement to restore deleted tables, dynamic tables, and materialized views. Therefore, this article uses UNDROP TABLE to restore deleted materialized views. Whether the deleted object can be restored depends on the data [retention period](timetravel.md).
**Data Retention Period**:
The ability to restore historical objects depends on the data retention period. The current preview version has a default data retention period of 7 days, which will be adjusted to 1 day in the future. You can adjust the retention period by executing the [ALTER command](timetravel.md). Please note that modifying the retention period may increase storage costs. Supported objects include tables (TABLE), dynamic tables (DYNAMIC TABLE), and materialized views.

## Syntax
```sql
UNDROP TABLE tablename;
```
## Parameter Description

* **tablename**: Specifies the name of the table to be deleted. Supports dynamic tables, internal tables, materialized views.
## Example
**Restore Materialized View**
```SQL
DROP      TABLE mv_base_a;

DROP MATERIALIZED VIEW mv1;

-- Create a base table
CREATE    TABLE mv_base_a (i int, j int);

INSERT    INTO mv_base_a
VALUES    (1, 10),
          (2, 20),
          (3, 30),
          (4, 40);

-- Use dynamic table for processing
CREATE MATERIALIZED VIEW mv1 (i, j) AS
SELECT    *
FROM      mv_base_a;

-- Refresh dynamic table
REFRESH   MATERIALIZED VIEW mv1;

-- Query data
SELECT    *
FROM      mv1;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
DROP materialized VIEW mv1;

SHOW      TABLES history
WHERE     table_name = 'mv1';
+-------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| schema_name | table_name |       create_time       | creator  | rows | bytes | comment | retention_time |       delete_time       |
+-------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
| public      | mv1        | 2024-12-18 16:57:35.916 | UAT_TEST | 4    | 2467  |         | 1              | 2024-12-18 16:57:58.427 |
+-------------+------------+-------------------------+----------+------+-------+---------+----------------+-------------------------+
UNDROP TABLE mv1;

SELECT    *
FROM      mv1;
+---+----+
| i | j  |
+---+----+
| 1 | 10 |
| 2 | 20 |
| 3 | 30 |
| 4 | 40 |
+---+----+
```
## Precautions

* Please ensure that the recovery operation is performed within the data retention period, otherwise the deleted table cannot be restored.
* Before restoring the table, make sure that there are no tables with the same name. If there are tables with the same name, please rename or delete the tables with the same name.
