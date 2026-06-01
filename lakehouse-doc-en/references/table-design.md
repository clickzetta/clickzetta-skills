# Table Design and Data Type Operations

Create a table that covers all table structure data types supported by Singdata Lakehouse, and use this table as the base table to create a regular view.

## Create Schema

```
CREATE SCHEMA IF NOT EXISTS lakehouse_demo_table_design_schema;
USE SCHEMA lakehouse_demo_table_design_schema;
SELECT current_schema();
```

## Create Tables and Views

-- Singdata Lakehouse supported data types

```
CREATE TABLE IF NOT EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes
(
    c_bigint BIGINT,
    c_boolean BOOLEAN,
    c_binary BINARY,
    c_char CHAR,
    c_date DATE,
    c_decimal DECIMAL(20,6),
    c_double DOUBLE,
    c_float FLOAT,
    c_int INT,
    c_interval INTERVAL DAY,
    c_smallint SMALLINT,
    c_string STRING,
    c_timestamp TIMESTAMP,
    c_tinyint TINYINT,
    c_array ARRAY<STRUCT<a: INT, b: STRING>>,
    c_map MAP<STRING, STRING>,
    c_struct STRUCT<a: INT, b: STRING, c: DOUBLE>,
    c_varchar VARCHAR(1024),
    c_json JSON
);
-- The LIKE statement can create another table, making the target table have the same structure as the source table. However, the table created by this statement does not copy data.
CREATE  TABLE IF NOT EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes_like LIKE lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- The AS statement can be used to synchronously or asynchronously query the original table and create a new table based on the query results, then insert the query results into the new table, but it will not copy partition information.
CREATE  TABLE IF NOT EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes_as AS select* from lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- Create a regular view
CREATE VIEW  IF NOT EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes_view as select* from lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- Check the created tables and views
show tables like 'clickzetta_datatypes%' in lakehouse_demo_table_design_schema;
```

![](.topwrite/assets/image_1718700694135.png)

## Insert Records into the Table

```
INSERT INTO lakehouse_demo_table_design_schema.clickzetta_datatypes VALUES
(1, true, X'01', 'a', DATE'2022-02-01', 1000.123456, 2.0, 1.5, 42, INTERVAL 1 DAY, 103, 'test string 1',TIMESTAMP '2022-02-01 20:00:00', 11, ARRAY(STRUCT(1, 'A')), MAP('key1', 'value1'), STRUCT(1, 'A', 2.0), 'varchar example 1',JSON '{"id": 1, "value": "100", "comment": "JSON Sample data"}' ),
(2, false, X'02', 'b', DATE'2022-02-02', 2000.234567, 4.0, 2.5, 84, INTERVAL 2 DAY, 104,'test string 2',TIMESTAMP '2022-02-02 21:00:00', 12, ARRAY(STRUCT(2, 'B')), MAP('key2', 'value2'), STRUCT(2, 'B', 4.0), 'varchar example 2',JSON '{"id": 2, "value": "200", "comment": "JSON Sample data"}' );
```

## Query Date, Timestamp, and Interval Type Data

```
-- 1. Filter by date
SELECT * FROM lakehouse_demo_table_design_schema.clickzetta_datatypes WHERE c_date >= DATE '2022-02-02';

-- 2. Select records within a specific time range
SELECT * FROM lakehouse_demo_table_design_schema.clickzetta_datatypes WHERE c_timestamp BETWEEN TIMESTAMP '2022-02-01 20:00:00' AND TIMESTAMP '2022-02-02 21:00:00';

-- 3. Add days to a date
SELECT c_date, c_date + INTERVAL 7 DAY as plus_7_days FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 4. Calculate the difference in days between two dates
SELECT c_date, DATEDIFF((SELECT c_date FROM lakehouse_demo_table_design_schema.clickzetta_datatypes WHERE c_bigint = 2), c_date) as days_difference FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 5. Extract the year, month, and day from a date
SELECT EXTRACT(YEAR FROM c_date) as year, EXTRACT(MONTH FROM c_date) as month, EXTRACT(DAY FROM c_date) as day FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 6. Calculate the difference between a timestamp and the current time (in minutes)
SELECT c_timestamp, TIMESTAMPDIFF(MINUTE, c_timestamp, NOW()) as minutes_difference FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 7. Compare two intervals
SELECT  INTERVAL 10 DAY, c_interval, INTERVAL 10 DAY > c_interval from lakehouse_demo_table_design_schema.clickzetta_datatypes;
```

## Working with Complex Data Types: Map, Array, Struct, JSON

```
-- 1. Extract values from a map
SELECT
  c_int,
  c_map['key1'] AS map_key1_value, 
  c_map['key2'] AS map_key2_value
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 2. Calculate map length
SELECT
  c_int,
  cardinality(c_map) AS map_length
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 3. Extract struct fields from an array
SELECT
  c_int,
  c_array[0].a AS array_col1_value, 
  c_array[0].b AS array_col2_value
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 4. Calculate array length
SELECT
  c_int,
  array_size(c_array) AS array_length
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 5. Extract values from a struct
SELECT
  c_int,
  c_struct.a AS struct_col1_value,
  c_struct.b AS struct_col2_value,
  c_struct.c AS struct_col3_value
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 6. Combine results into one cell
SELECT
  c_int,
  concat_ws(
    'Map Value Key1: ', c_map['key1'], ', ',
    'Map Value Key2: ', c_map['key2'], ', ',
    'Array Struct: (', c_array[0].a, ', ', c_array[0].b, ')'
  ) AS combined_result
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 7. Extract JSON fields
SELECT
  json_extract_int(c_json,"$.id") as id,
  json_extract_bigint(c_json,"$.value") as value,
  json_extract_string(c_json,"$.comment") as comment
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;
```

## Query MAP Type Data

Below are some examples of SELECT statements for the c_map type column in the clickzetta_datatypes table:

```
-- 1. Extract values from a map
SELECT
  c_int,
  c_map['key1'] AS map_key1_value, 
  c_map['key2'] AS map_key2_value
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 2. Calculate map length
SELECT
  c_int,
  cardinality(c_map) AS map_length
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 3. Check if a specified key exists in the map
SELECT
  c_int,
  c_map['key_to_check'] IS NOT NULL AS key_exists
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 4. Filter using values in the map
SELECT
  c_int,
  c_map
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes
WHERE c_map['key1'] = 'value_to_match';

-- 5. Return the row with the maximum key value
SELECT
  c_int,
  c_map
FROM clickzetta_datatypes
WHERE c_map['key_with_max_value'] = (
  SELECT MAX(c_map['key_with_max_value'])
  FROM lakehouse_demo_table_design_schema.clickzetta_datatypes
);

-- 6. Convert the map to an array and extract the key and value of the first element
SELECT
  c_int,
  map_keys(c_map)[0] AS first_key,
  map_values(c_map)[0] AS first_value
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;
```

## Query Array Type Data

Below are some examples of SELECT statements for the c_array type column in the clickzetta_datatypes table:

```
-- 1. Extract values from an array
SELECT
  c_int,
  c_array[0] AS array_element_1, 
  c_array[1] AS array_element_2
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 2. Calculate array length
SELECT
  c_int,
  cardinality(c_array) AS array_length
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;
```

## Query Struct Type Data

Below are some examples of SELECT statements for the c_struct type column in the clickzetta_datatypes table, including various operations on the c_struct column.

```
-- 1. Select all attributes of c_struct
SELECT c_struct.a, c_struct.b, c_struct.c
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 2. Perform operations on the c_struct column

-- 2.1 Multiply the a attribute in the c_struct column by a value (e.g., 2)
SELECT c_struct.a * 2 as multiplied_a
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 2.2 Calculate the average of the a and c attributes in the c_struct column
SELECT (c_struct.a + c_struct.c) / 2 as avg_a_c
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 2.3 Sort results by the b attribute in the c_struct column
SELECT c_struct.a, c_struct.b, c_struct.c
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes
ORDER BY c_struct.b;

-- 3. Use aggregate functions on the c_struct column

-- 3.1 Calculate the sum of the a attribute in the c_struct column
SELECT SUM(c_struct.a) as total_a
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 3.2 Calculate the average of the c attribute in the c_struct column
SELECT AVG(c_struct.c) as avg_c
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;

-- 3.3 Get the maximum value of the a attribute in the c_struct column
SELECT MAX(c_struct.a) as max_a
FROM lakehouse_demo_table_design_schema.clickzetta_datatypes;
```

## Cleanup

```
DROP TABLE IF EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes;
DROP TABLE IF EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes_like;
DROP TABLE IF EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes_as;
DROP VIEW IF EXISTS lakehouse_demo_table_design_schema.clickzetta_datatypes_view;
DROP SCHEMA IF EXISTS lakehouse_demo_table_design_schema;
```

## Congratulations, Task Complete!

Please enjoy the learning process and learn more!

## Appendix

### Download Zeppelin Notebook Source File

The code in this document is also available in a version that runs on [Zeppelin](eco_integration/zeppelin.md). If you want to run the code directly, please follow the documentation to install [Zeppelin](eco_integration/zeppelin.md).

[02.Table Design.ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/02.%E8%A1%A8%E8%AE%BE%E8%AE%A1.ipynb)
