# Description

`SHOW PARTITIONS` is a command in SQL used to display partition information of a specified table. Partitioned tables are a common data organization method in data warehouses, optimizing query performance and management efficiency by distributing data across different partitions. Using `SHOW PARTITIONS` allows you to quickly view the partition structure of a table and detailed information about each partition.

# Usage Restrictions

* Currently, partitions written using the [real-time SDK](java_reference/realtime-upload.md) cannot be viewed immediately. You need to wait for the real-time written data to be committed to view the partition size.

# Syntax
```SQL
SHOW PARTITIONS [EXTENDED] table_name [ PARTITION ( partition_col_name = partition_col_val [ , ... ] ) ]
[WHERE <expr>]
```
## Parameter Description

* **EXTENDED**: Adding this keyword allows you to view the number of files, size, number of rows, and modification time of the partition.
* **table\_name**: The name of the table for which partition information needs to be queried. Supports tables, dynamic tables, and materialized views.
* **PARTITION ( partition\_col\_name = partition\_col\_val** \[ , ... ] ): Optional parameter used to specify specific conditions for the partition to be viewed. By specifying the value of the partition key, specific partition information can be filtered out.
* **where \<expr**>: Optional, can filter based on displayed fields. Supports filtering based on total\_rows, bytes, total\_files, created\_time. Expr supports =, !=, >, <, >=, <=, is null, is not null, between ...and, or, not, <>, in.

# Usage Scenarios

* **View Partition Structure**: Understand the partition strategy of the table and the current partition situation. View partition size and modification time.
* **Data Management**: When importing, exporting, or maintaining data, understanding partition information helps manage data more efficiently.

# Examples

## View All Partitions
```SQL
DROP TABLE IF EXISTS pt_table;
CREATE TABLE pt_table (order_id INT, customer_id INT, amount DOUBLE) PARTITIONED BY (pt1 string,pt2 string);
INSERT INTO pt_table
VALUES (1, 101, 100.0, '2023','01'),
       (2, 102, 200.0, '2023','02'),
       (3, 103, 300.0, '2023','03'),
       (4, 104, 400.0, '2023','04');

SHOW PARTITIONS pt_table;
+-----------------+
|   partitions    |
+-----------------+
| pt1=2023/pt2=01 |
| pt1=2023/pt2=02 |
| pt1=2023/pt2=03 |
| pt1=2023/pt2=04 |
+-----------------+
SHOW PARTITIONS EXTENDED pt_table;
+-----------------+------------+-------+-------------+-------------------------+
|   partitions    | total_rows | bytes | total_files |      created_time       |
+-----------------+------------+-------+-------------+-------------------------+
| pt1=2023/pt2=01 | 1          | 3101  | 1           | 2024-12-20 14:25:34.99  |
| pt1=2023/pt2=02 | 1          | 3102  | 1           | 2024-12-20 14:25:34.99  |
| pt1=2023/pt2=03 | 1          | 3102  | 1           | 2024-12-20 14:25:34.99  |
| pt1=2023/pt2=04 | 2          | 3119  | 1           | 2024-12-20 14:25:34.99  |
+-----------------+------------+-------+-------------+-------------------------+
```
The above command will return all partition information of the `sales_data` table.

## View Specific Partition
```SQL
SHOW PARTITIONS pt_table PARTITION (pt1 = '2023');
+-----------------+
|   partitions    |
+-----------------+
| pt1=2023/pt2=01 |
| pt1=2023/pt2=02 |
| pt1=2023/pt2=03 |
| pt1=2023/pt2=04 |
+-----------------+
SHOW PARTITIONS pt_table PARTITION (pt1 = '2023',pt2='01');
+-----------------+
|   partitions    |
+-----------------+
| pt1=2023/pt2=01 |
+-----------------+
```
## Use where to filter based on displayed fields
```SQL
--Filter partitions with total rows greater than 1
SHOW PARTITIONS EXTENDED pt_table WHERE total_rows>1;
+-----------------+------------+-------+-------------+-------------------------+
|   partitions    | total_rows | bytes | total_files |      created_time       |
+-----------------+------------+-------+-------------+-------------------------+
| pt1=2023/pt2=04 | 2          | 3119  | 1           | 2024-12-20 14:25:34.99  |
+-----------------+------------+-------+-------------+-------------------------+
```


