# Verify the Operation Results of Schema Evolution

Singdata Lakehouse Schema Evolution supports changing columns in a table through the ALTER statement, including adding columns, modifying columns, and deleting columns. Modifying columns includes changing column names and column data types. It supports changes in complex types.
This article provides corresponding examples to facilitate the verification of the operation results of Schema Evolution, quickly understand the results of Schema Evolution, and verify whether the implementation meets expectations.

## Create schema and table

```
CREATE SCHEMA IF NOT EXISTS clickzetta_demo_schema_evolution_schema;
USE SCHEMA clickzetta_demo_schema_evolution_schema;
CREATE TABLE if not exists clickzetta_demo_schema_evolution_schema.schema_evolution (
    t_tinyint tinyint,
    t_snmallint smallint,
    t_int int,
    t_bigint bigint,
    t_float float,
    t_double double,
    t_decimal decimal(5,2)
)partitioned by(pt string);
```

## Insert Data

```
insert into clickzetta_demo_schema_evolution_schema.schema_evolution select 1y,234s,10000,100000000,0.2f,0.004d,123.1bd,'202231120';
```

A column must be added to the partition table at a specified position, otherwise the added column will be the last column

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution ADD COLUMN t_add int comment 'add';
```



```
desc clickzetta_demo_schema_evolution_schema.schema_evolution;
```

![](.topwrite/assets/image_1718704848571.png)

## Add Columns at Specified Position

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution ADD COLUMN t_add2 int comment 'add' after t_decimal;
desc clickzetta_demo_schema_evolution_schema.schema_evolution;
```

![](.topwrite/assets/image_1718704923098.png)

## Delete Column

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution DROP   COLUMN t_add;
desc clickzetta_demo_schema_evolution_schema.schema_evolution;
```

## Rename Columns

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution rename COLUMN t_add2 to t_add;
desc clickzetta_demo_schema_evolution_schema.schema_evolution;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution;
```

## Modify Field Position

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution change COLUMN t_add  after t_tinyint ;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution;
```

## Modify Data Types

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution change COLUMN t_decimal  type DECIMAl(7,4) ;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution;
```

Unsupported type conversions will result in an error

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution change COLUMN t_decimal  type date ;
```

## Modify Field Comment

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution change COLUMN t_tinyint  comment 'mysmallint';
desc clickzetta_demo_schema_evolution_schema.schema_evolution;
```

## Complex Type Modification

### Create Table

```
 CREATE TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 (
  point struct<x: int, y: double>,
  points array<struct<x: double, y: double>>,
  points_ky map<struct<x: int>, struct<a: int>>
    );
```

### Insert Data

```
insert into clickzetta_demo_schema_evolution_schema.schema_evolution_01 values(struct(1D,2D),array(struct(1D,2D)),null);
```

### Add Column

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 ADD COLUMN point.z double ;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution_01;
```

### Delete the z column in the point struct

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 DROP COLUMN point.z;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution_01;
```

### Rename the x column in the point struct

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 rename COLUMN point.x to xx;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution_01;
```

### Delete the column y in the nested struct of the array

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 DROP COLUMN points.element.y;
desc clickzetta_demo_schema_evolution_schema.schema_evolution_01;
```

## Modify struct type

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 CHANGE COLUMN point.xx type bigint;
desc clickzetta_demo_schema_evolution_schema.schema_evolution_01;
```

### Modify Complex Type Position

```
ALTER TABLE clickzetta_demo_schema_evolution_schema.schema_evolution_01 CHANGE COLUMN point.y first;
select * from clickzetta_demo_schema_evolution_schema.schema_evolution_01;
```

## Cleanup

```
DROP SCHEMA IF EXISTS clickzetta_demo_schema_evolution_schema;
```

## Congratulations, it's done.

Please enjoy and learn more!

## Appendix

### Download Zeppelin Notebook Source File

The code in this document is also available in a version that runs on [Zeppelin](eco_integration/Zeppelin.md). If you want to run the code directly, please follow the documentation to install [Zeppelin](eco_integration/Zeppelin.md).

[03.Schema Evolution.ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/03.Schema%20Evolution.ipynb)
