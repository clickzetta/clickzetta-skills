# Create BLOOMFILTER Index

## Description

A Bloom Filter is a probabilistic data structure used to determine whether an element belongs to a set. This feature allows users to create Bloom Filter indexes in a table to improve query efficiency. For a detailed introduction, refer to [Bloomfilter Index](bloomfilter-summary.md)

## Syntax
```
CREATE BLOOMFILTER INDEX [IF NOT EXISTS] index_name ON TABLE 
[schema].table_name(column_name)
[COMMENT 'comment']
[PROPERTIES ('key'='value')]
```
**bloomfilter**: Index type, using the Bloom filter algorithm.

**index\_name**: The name of the index to be created, located under the schema of the target table. Index names cannot be duplicated within the same schema. The index must be in the same schema as the target table.

**schema**: Optional parameter, used to specify the schema name of the table.

**table\_name**: The name of the table to create the index on.

**column\_name**: The name of the column to create the index on, currently only single-column indexes are supported.

**COMMENT**: Optional parameter, used to add a description of the index.

**PROPERTIES**: Optional parameter, reserved properties for Lakehouse, facilitating the addition of properties in the future.

## Reference Documentation

* [Build Index](build-index.md)
* [Delete Index](drop-index.md)
* [List All Indexes](show-index.md)
* [View Index Details](desc-index.md)

## Usage Notes

1. After adding the BLOOMFILTER INDEX, it will only take effect for newly written data. Existing data requires `BUILD INDEX` to backfill the index.
2. A table can have multiple Bloom filter indexes.
3. Type restrictions: interval, struct, map, array, and other types are not supported. If unsupported types are used, the system will report an error.
4. The index must be in the same schema as the target table; creating an index across schemas will result in an error.

## Instructions

[BLOOMFILTER INDEX Instructions](bloomfilter-summary.md)

## Examples

1. Specify BLOOMFILTER index when creating a table
   ```
   DROP TABLE IF EXISTS t;
   CREATE    TABLE t (
             order_id INT,
             customer_id INT,
             amount DOUBLE,
             order_year string,
             order_month string,
             INDEX order_id_index (order_id) BLOOMFILTER COMMENT 'BLOOMFILTER'
             );         
   INSERT INTO t
   VALUES (1, 101, 100.0, '2023','01'),
          (2, 102, 200.0, '2023','02'),
          (3, 103, 300.0, '2023','03'),
          (4, 104, 400.0, '2023','04'),
          (5, 105, 500.0, '2023','04');
   SHOW INDEX FROM t;
   +----------------+--------------+
   |   index_name   |  index_type  |
   +----------------+--------------+
   | order_id_index | bloom_filter |
   +----------------+--------------+

   DESC INDEX order_id_index;
   +--------------------+-------------------------+
   |     info_name      |       info_value        |
   +--------------------+-------------------------+
   | name               | order_id_index          |
   | creator            | UAT_TEST                |
   | created_time       | 2024-12-26 21:20:43.914 |
   | last_modified_time | 2024-12-26 21:20:43.914 |
   | comment            | BLOOMFILTER             |
   | index_type         | bloom_filter            |
   | table_name         | t                       |
   | table_column       | order_id                |
   +--------------------+-------------------------+
   DROP INDEX order_id_index;

   ```
2. Add BLOOMFILTER Index to Existing Columns
```
   CREATE BLOOMFILTER INDEX customer_id_index
   ON TABLE public.t (customer_id)
   COMMENT 'xx';
   -- After the BLOOMFILTER INDEX is added, it will only take effect for newly written data.
   -- Existing data requires BUILD INDEX to backfill the index.
   BUILD INDEX customer_id_index ON public.t;
   DESC INDEX customer_id_index;
   +--------------------+-------------------------+
   |     info_name      |       info_value        |
   +--------------------+-------------------------+
   | name               | customer_id_index       |
   | creator            | UAT_TEST                |
   | created_time       | 2024-12-26 21:24:57.649 |
   | last_modified_time | 2024-12-26 21:24:57.649 |
   | comment            | xx                      |
   | index_type         | bloom_filter            |
   | table_name         | t                       |
   | table_column       | customer_id             |
   +--------------------+-------------------------+
   DROP INDEX customer_id_index;

   ```