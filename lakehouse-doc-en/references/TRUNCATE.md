## TRUNCATE TABLE

## Description

The `TRUNCATE TABLE` command is used to quickly delete all records in a table, but the table structure and its attributes will remain unchanged. Unlike the `DROP TABLE` command, `TRUNCATE TABLE` does not completely delete the table, but only deletes the data in the table.

## Syntax
```SQL
TRUNCATE TABLE  [ IF EXISTS ] table_name;
```
**Required Parameters**

* `table_name`: Specify the name of the table to clear data from.

**Optional Parameters**

* `IF EXISTS`: If the specified table does not exist, no error is reported and other operations continue.

##  Example

1. Clear all records from the table named `employees`:
   ```SQL
   TRUNCATE TABLE employees;
   ```
2. Clear the table `employees`, do not report an error if the table does not exist:
   ```SQL
   TRUNCATE TABLE IF EXISTS employees;
   ```
# TRUNCATE TABLE PARTITION

## Function

The `TRUNCATE TABLE PARTITION` command is used to clear the data of specified partitions in a partitioned table. It supports clearing partition data through conditional filtering. If you want to delete one or more partitions that meet a certain rule condition at once, you can use an expression to specify the filtering condition, match the partitions through the filtering condition, and batch clear the partition data.

## Syntax

* Specify partition deletion:
```SQL
TRUNCATE TABLE <table_name> PARTITION (<pt_spec>)[, PARTITION (<pt_spec>)....];
```
* Specify partition filter conditions:
```SQL
TRUNCATE TABLE <table_name>  <partition_expression>;
partition_expression::=
   PARTITION (<partition_col> <relational_operators> <partition_col_value>)
   | PARTITION (scalar(<partition_col>) <relational_operators> <partition_col_value>)
   | PARTITION (<partition_filter> AND|OR <partition_filter>)
   | PARTITION (NOT <partition_filter>)
   | PARTITION (<partition_filter>)[,PARTITION (<partition_filter>), ...]
```
**Parameter Description**

* `table_name`: Specifies the name of the table.
* `IF EXISTS`: If the table does not exist, executing this command with this parameter will not result in an error.
* `pt_spec`: Required. The partition whose data is to be cleared. When there are multiple partition fields, the format is `(partition_col1 = partition_col_value1, partition_col2 = partition_col_value2, ...)`. `partition_col` is the partition field, and `partition_col_value` is the partition value. Partition fields are case-insensitive, while partition values are case-sensitive. Supports specifying multiple partition values separated by commas.
* `partition_expression`: Can include the following forms:

  1. **Comparison operations based on partition columns**:
  ```SQL
  PARTITION (<partition_col> <relational_operators> <partition_col_value>)
  ```
* `<partition_col>`: The name of the partition column in the partition table.
  * `<relational_operators>`: Relational operators, such as `=` , `<` , `>` , `<=` , `>=` , `<>`.
  * `<partition_col_value>`: The value to be compared with the partition column.
  * The following example
  ```
  TRUNCATE TABLE sales PARTITION (sale_date < '2022-01-01');
  ```
2. **Partition Column Comparison Based on Scalar Functions**:
  ```SQL
  PARTITION (scalar(<partition_col>) <relational_operators> <partition_col_value>)
  ```
* The `scalar` function is a function that returns a single value and is used to convert the values of partition columns into scalar values. Currently, the partition scalar functions supported by the lakehouse include time functions, JSON functions, data functions, encryption functions, regular expression functions, and string functions.

  * The following example
    ```
    TRUNCATE TABLE sales PARTITION (lower(pt)=product1);
    ```
3. **Composite Conditions Based on Partition Filters**:
  ```SQL
  PARTITION (<partition_filter> AND|OR <partition_filter>)
  ```
* `<partition_filter>`: Can be any valid partition filter condition.
  * `AND|OR`: Logical operators used to combine multiple filter conditions.
  * Example as follows
    ```
    TRUNCATE TABLE sales  PARTITION(pt1='2023' and pt2='03');
    ```
4. **Negative Conditions Based on Partition Filters**:
  ```SQL
  PARTITION (NOT <partition_filter>)
  ```
* `NOT`: Logical NOT operator, used to negate a filter condition.
  * Example as follows
    ```
    TRUNCATE TABLE sales  PARTITION(pt2 not in('01','04'));
    ```
5. **List of Multiple Partition Filters**:
  ```SQL
  PARTITION (<partition_filter>)[,PARTITION (<partition_filter>), ...]
  ```
* Allows you to list multiple partition filter conditions, separated by commas.

## Usage Example

1. Specify partition deletion
```sql
-- Clear a partition from the table sale_detail
TRUNCATE  TABLE sale_detail PARTITION (pt = '202402', region = 'beijing');
-- Clear two partitions from the table sale_detail simultaneously, clearing sales records for Hangzhou and Shanghai regions in January 2024.
TRUNCATE  TABLE sale_detail PARTITION (pt = '201401', region = 'hangzhou'),
PARTITION (pt = '201401', region = 'shanghai');
```
2. Use filter conditions to delete and clear all partitions in the `sales` table that meet the partition conditions `year < 2024 AND quarter = 1`:
   ```SQL
   TRUNCATE  TABLE sales PARTITION 
   (
   YEAR < 2024 AND      
   QUARTER = 1
   );
   ```

^
