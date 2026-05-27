## Function
Insert one or more rows of data into the table. The data will overwrite the target table being written to. If the table is a partitioned table, it will overwrite the partition, if the table is a non-partitioned table, it will overwrite the table data.

## Syntax

```SQL
INSERT OVERWRITE [TABLE] table_name 
[ PARTITION partition_spec] 
 [ column_list ]
{VALUES(value [,...]) ,(value  [,...])| query}

partition_spec ::=
    partition_col_name = partition_col_val [ , ... ] | partition_col_name

```

**Parameter Description**

**1.TABLE**: Optional, keyword

**2.partition_spec**: Optional, when the table is a partitioned table and the partition field is not a function, this option can be specified, compatible with hive syntax,
- Supports specifying partition value (static partition)
- Supports specifying partition field (dynamic partition), partition is automatically mapped according to values or select values, the system automatically overwrites partition data according to the value of the partition column
- If this option is not specified, the system will automatically overwrite the data of the corresponding partition according to the value of the partition column

When the table is a regular table or the partition field is a function
- No need to specify this option, if the partition value is a function, the system will automatically overwrite the data of the corresponding partition according to the value of the partition column

**3.column_list**
Will reorder the columns of the input query according to the specified columns, this option can be specified when the result of the input query is inconsistent with the table

## Examples
Create a partitioned table
Case one
```SQL
CREATE TABLE t1 (id BIGINT,name VARCHAR(64))
  PARTITIONED BY (dt string);

INSERT OVERWRITE t1 VALUES(1001, 's121', 'beijing');
INSERT OVERWRITE t1 VALUES(1002, 's123', 'beijing'),(1003, 's124', 'beijing');
INSERT OVERWRITE t1 PARTITION(dt='shanghai')(name,id) VALUES('s125',1005);

--With select statement
INSERT OVERWRITE t1 select * from t2;
INSERT OVERWRITE t1 partition(dt="shanxi") select id,name from t2;
```
Case two

```SQL
CREATE TABLE t1 (id BIGINT,name VARCHAR(64),dt STRING)
  PARTITIONED BY (dt );

INSERT OVERWRITE t1 VALUES(1001, 's121', 'beijing');
INSERT OVERWRITE t1 VALUES(1002, 's123', 'beijing'),(1003, 's124', 'beijing');
INSERT OVERWRITE t1 PARTITION(dt='shanghai')(name,id) VALUES('s125',1005);

--With select statement
INSERT OVERWRITE t1 select * from t2;
INSERT OVERWRITE t1 partition(dt="shanxi") select id,name from t2;
```

