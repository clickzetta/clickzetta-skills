# Import Data from VOLUME to Table

**Objective**: Use the Copy command and SQL statements to import files (CSV, Parquet, ORC) from Volume into a Lakehouse table.

## Syntax

```SQL
COPY INTO  TABLE_NAME 
FROM 
{ VOLUME external_volume_name | TABLE VOLUME table_name  | USER VOLUME }  
     ([column_list] )
[USING {CSV | ORC | PARQUET } 
    (formatTypeOptions)]
[FILES = ( '<file_name>'  , ...  )]
[COPYOPTIONS]
```

## Example

### Example 1: Import data files from VOLUME into a table

```
COPY INTO tbl_region 
FROM TABLE VOLUME region 
    (r_regionkey integer, r_name char(25), r_comment varchar(152)) 
USING csv OPTIONS('sep' = '|' ) 
FILES ('region.tbl')
--Delete files in the volume to save storage
PURGE=TRUE;
```

### Example 2: Write the SELECT query result for VOLUME into a table

```
COPY INTO region 
FROM (SELECT * FROM TABLE VOLUME region 
         (r_regionkey integer, r_name char(25), r_comment varchar(152)) 
using csv Options( 'sep' = '|' ) 
FILES ('region.tbl') 
WHERE r_regionkey < 3)t
--Delete files in the volume to save storage
PURGE=TRUE;
```

^
