## Description

`MAX_PT` is used to get the value of the largest partition in a partitioned table. This function is particularly suitable for handling partitioned tables and can help users quickly locate the latest data partition.

## Syntax
```SQL
max_pt('schema_name.table_name'｜ 'table_name')
```
## Parameter Description

* **schema\_name.table\_name**: This is a required parameter of type STRING. It supports the format schema\_name.table\_name or table\_name. If the schema is not specified, the current context environment will be used by default.

## Return Value Description

* This function returns the value of the largest first-level partition.

## Example

Example 1: Basic Usage

Assume `tbl` is a partitioned table with partitions `20120901` and `20120902`, and both partitions contain data. In the following statement, the value returned by `max_pt` is `'20120902'`.
```SQL
SELECT * FROM tbl WHERE pt = max_pt('tbl');
```
Equivalent to the following statement:
```SQL
SELECT * FROM tbl WHERE pt = (SELECT MAX(pt) FROM tbl);
```

 Example 2: Multi-level Partition Scenario

In a multi-level partition scenario, you can use standard SQL to retrieve data from the largest partition.

```SQL
SELECT * FROM table WHERE pt1 = (SELECT MAX(pt1) FROM table) AND pt2 = (SELECT MAX(pt2) FROM table WHERE pt1 = (SELECT MAX(pt1) FROM table));
```