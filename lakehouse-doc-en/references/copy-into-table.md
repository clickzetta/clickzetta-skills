#  Description

Load data from files in object storage into a table. These files must exist in object storage.

* Currently supported object storage locations are Tencent Cloud COS, Alibaba Cloud OSS, and AWS S3. Currently, only Volume objects are supported.
* Cross-cloud vendor import is not supported at the moment. For example, if your Lakehouse service is on Alibaba Cloud but the object storage is on Tencent Cloud.

# Syntax
```SQL
-- Directly import data from VOLUME
COPY INTO|OVERWRITE table_name FROM VOLUME volume_name
[( <column_name> <column_type>,...) ]
USING CSV | PARQUET | ORC | BSON
OPTIONS(
  FileFormatParams
) 
FILES('filename1','fiename2'...)|SUBDIRECTORY 'path'|REGEXP <pattern>;

-- Perform transformation during import
COPY INTO table_name FROM (
SELECT  <column_name>,... 
FROM VOLUME <volume_name>
[(<column_name> <column_type>,...) ]
USING CSV|PARQUET|ORC 
OPTIONS(
  FileFormatParams
) 
FILES|SUBDIRECTORY|REGEXP <pattern>
);
```
### Instructions

After the copy into statement, you can directly use the volume query syntax to transform data during the import process. Refer to volume query [structured and semi-structured data analysis](<structure_data_analysis.md>).

### **Parameter Description**:

* **OVERWRITE**｜**INTO**:
  * **INTO**: Append mode. When using the `INTO` clause for data import, new data will be appended to the target table, and this mode will not delete or modify existing data in the table.
  * **OVERWRITE**: Overwrite mode. When using the `OVERWRITE` clause for data import, existing data in the target table will be cleared, and then new data will be imported. This mode is suitable for scenarios where new data needs to completely replace old data.
```
--Append data to the table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
COPY INTO birds FROM 
VOLUME  my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
--Overwrite data in the table
COPY OVERWRITE birds FROM 
VOLUME  my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```
* **column\_name** and **column\_type**: Optional, Lakehouse supports automatic schema recognition for files. It is recommended not to fill them in. When specified, the column names and types in the file must match the predefined column types in the file.
  * Automatic schema recognition for CSV files will automatically generate fields, with field numbers starting from f0. Currently, the automatically recognized types are int, double, string, and bool.
  * For Parquet and ORC formats, the field names and types stored in the file will be automatically recognized. If the number of columns in the specified file is inconsistent, Lakehouse will attempt to merge them. If merging is not possible, an error will be reported.
```
--Specify the column types and names in the volume
COPY OVERWRITE birds FROM 
VOLUME  my_volume(id int,name string,wingspan_cm float,colors string)
USING csv
SUBDIRECTORY 'dau_unload/read/';
--Automatically detect the column types and names in the volume
COPY OVERWRITE birds FROM 
VOLUME  my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```
* **FileFormatParams**: Multiple parameters are separated by commas, in the string format 'key'='value'
* CSV format: Supports the following file parameter combinations
  * sep: Column separator, default is ",". Supports a maximum length of 2 character, for example: `'sep'=','` or `sep='||'`
  * compression: Configures the file compression format. Supported compression formats are: gzip/zstd/zlib. For example: `'compression'='gzip'`
   * `lineSep`: The line separator, which by default recognizes both `\r\n` and `\n` as newline characters. It supports a maximum length of 2 characters. For example:
        * `'lineSep' = '$'`: Uses `$` as the line separator.
        * `lineSep = '\r\n'`: Uses the Windows-style carriage return and line feed as the newline character.
  * quote: Sets a single character used to escape quote values. The default value is double quotes `"`, for example: `'quote'='"'`
  * header: Whether to parse the header, default is false. Boolean type, for example: `'header'='true'`
  * timeZone: Configures the time zone, no default value. Used to specify the time zone for the time format in the file. For example: `'timeZone' = 'Asia/Shanghai'`
  * escape: Used to escape quotes within quoted values, default value is `\`, for example: `'escape'='\'`
  * nullValue: Used to determine what content should be Null, default value is `""`, for example `'nullValue'='\\\N'` or `'nullValue'=r'\N'`
    ```
    --Specify delimiter and quote
    COPY OVERWRITE birds FROM 
    VOLUME  my_volume
    USING csv
    OPTIONS('sep'='|','quote'='"')
    files('dau_unload/part00001.csv');
    ```
  
        
* JSON format:
  * compression: Whether the source file/target file is compressed, default is no compression, configuration like `'compression'='gzip'`
   * explodeArray: Default value is true, optional value is false. Used when JSON content starts with an array. When set to true, the schema is considered to be the schema of a single unit within the array. When set to false, the schema is considered to be the schema of the array itself.

```
--Import json data
COPY OVERWRITE birds FROM 
VOLUME  my_volume
USING json
files('dau_unload/part00001.json');
```
* Parquet, ORC, BSON formats
* ```
  --Import parquet data
  COPY OVERWRITE birds FROM 
  VOLUME  my_volume
  USING parquet
  files('dau_unload/part00001.parquet');
  ```
* **FILES**: Used to specify the specific files to be read. Supports specifying multiple files of the same format. The file path is the sub-file path specified when creating the Volume. For example: `files('part-00002.snappy.parquet','part-00003.snappy.parquet')`.
* **SUBDIRECTORY**: Specifies the sub-path. Used to specify the sub-path to be read. When reading, all files in this directory will be recursively loaded. For example: `subdirectory 'month=02'`.
* ```
  COPY OVERWRITE birds FROM 
  VOLUME  my_volume(id int,name string,wingspan_cm float,colors string)
  USING csv
  SUBDIRECTORY 'dau_unload/read/';
  ```
* **REGEXP** \<pattern>: Regular expression matching. For example: `regexp 'part-.*.parquet'` matches files with a parquet suffix that start with part-. Another example: `regexp 'NYC/YellowTaxiTripRecords/parquet/yellow_tripdata_2022.*.parquet'` matches all files with a parquet suffix that start with *yellow_tripdata_2022* under the subpath *NYC/YellowTaxiTripRecords/parquet*.
* **PURGE=TRUE**: When this parameter is set, it indicates that the source files in object storage will be deleted after the data import is successful. This helps save storage space, especially when dealing with large amounts of data. If the import operation fails, the source files will not be deleted.
*  **ON_ERROR=CONTINUE|ABORT**: Controls the error - handling strategy during data loading. Adding this parameter also returns the list of imported files.
  * `CONTINUE`: Skips erroneous rows and continues loading subsequent data. Use when tolerating partial errors to maximize data loading. Currently, only file format mismatches (e.g., specifying zip compression in the command but encountering zstd - compressed files) are ignored.
  * `ABORT`: Immediately terminates the entire COPY operation. Use in scenarios with strict data quality requirements where any error necessitates manual inspection.

```
-- Specifying the abort parameter
copy into test_data from volume on_error_pipe using csv OPTIONS(sep='|','quote'='\0')
on_error = 'abort';
+-------------------------------------------------+---------+-------------+-------------+
|                      file                       | status  | rows_loaded | first_error |
+-------------------------------------------------+---------+-------------+-------------+
| oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv | SUCCESS | 2           |             |
+-------------------------------------------------+---------+-------------+-------------+
-- Specifying the continue parameter
copy into test_data from volume on_error_pipe using csv OPTIONS(sep='|','quote'='\0')
on_error = 'continue';
+-----------------------------------------------------+---------------+-------------+----------------------------------------------------------------------------------------------------------------------+
|                        file                         |    status     | rows_loaded |                                                                first_error                                           |
+-----------------------------------------------------+---------------+-------------+----------------------------------------------------------------------------------------------------------------------+
| oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv     | SUCCESS       | 2           |                                                                                                                      |
| oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv.zip | LOADED_FAILED | 0           | csv file: oss://lakehouse-perf-test/tmp/tmp_pipe/copy.csv.zip, line: 0: eatString throws quote(0) in unquote string, |
| oss://lakehouse-perf-test/tmp/tmp_pipe/new_copy.csv | SUCCESS       | 2           |                                                                                                                      |
+-----------------------------------------------------+---------------+-------------+----------------------------------------------------------------------------------------------------------------------+

```

# Notes

* It is recommended to choose a General Purpose Virtual Cluster (GENERAL PURPOSE VIRTUAL CLUSTER) when importing data, as general-purpose computing resources are more suitable for running batch jobs and loading data jobs.
* It is recommended to choose the same region when importing data to avoid public network transmission costs. Data transmission within the same region and the same cloud provider supports intranet transmission.

# Example

1. Load data from user volume
```SQL
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
-- Upload data to user volume
PUT '/Users/Downloads/data.csv' TO USER VOLUME FILE 'data.csv';
-- Import file data into target table
COPY INTO t_copy_from_volume FROM USER VOLUME  
USING csv  
OPTIONS(
        'header'='true',
        'lineSep'='\n'
)
FILES ('data.csv')
-- Delete files in volume to save storage
PURGE=TRUE;
;
```
2. Load Data from Table Volume
```SQL
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
-- Upload data to table volume
PUT '/Users/Downloads/data.csv' TO TABLE VOLUME t_copy_from_volume FILE 'data.csv';
-- Import file data into the target table
COPY INTO t_copy_from_volume FROM TABLE VOLUME t_copy_from_volume
USING csv  
OPTIONS(
        'header'='true',
        'lineSep'='\n'
)
FILES ('data.csv')
-- Delete files in the volume to save storage
PURGE=TRUE;
;

```
Export to External Volume

Before using, it is necessary to create VOLUME and CONNECTION. The creation process can refer to [CONNECTION creation](Datalake_StorageConnection.md) and [VOLUME creation](datalake_volume_object.md)

3. Import data from OSS
```SQL
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
-- Create oss connection
CREATE STORAGE CONNECTION  catalog_storage_oss
    type OSS
    ACCESS_ID='xxxx'
    ACCESS_KEY='xxxxxxx'
    ENDPOINT='oss-cn-hangzhou-internal.aliyuncs.com';
-- Create volume
CREATE EXTERNAL VOLUME my_volume
    location 'oss://mybucket/test_insert/'
    using connection catalog_storage_oss
    directory = (
        enable=true,
        auto_refresh=true
    );
-- Load data into table
COPY INTO birds FROM 
VOLUME  my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```
4. Import data from COS
```
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
-- Create COS connection
CREATE STORAGE CONNECTION my_conn 
  TYPE COS
  ACCESS_KEY = '<access_key>'
  SECRET_KEY = '<secret_key>'
  REGION = 'ap-shanghai'
  APP_ID = '1310000503';
-- Create volume
CREATE EXTERNAL VOLUME my_volume
    location 'cos://mybucket/test_insert/'
    using connection my_conn
    directory = (
        enable=true,
        auto_refresh=true
    );
-- Import data into the table
COPY INTO birds FROM 
VOLUME  my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';

```
5. Import data from s3
```SQL
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);

-- Create s3 connection
CREATE STORAGE CONNECTION aws_bj_conn
    TYPE S3
    ACCESS_KEY = 'AKIAQNBSBP6EIJE33***'
    SECRET_KEY = '7kfheDrmq***************************'
    ENDPOINT = 's3.cn-north-1.amazonaws.com.cn'
    REGION = 'cn-north-1';
-- Create volume
CREATE EXTERNAL VOLUME my_volume
    location 's3://mybucket/test_insert/'
    using connection aws_bj_conn
    directory = (
        enable=true,
        auto_refresh=true
    );
-- Import data into the table
COPY INTO birds FROM 
VOLUME  my_volume
USING csv
SUBDIRECTORY 'dau_unload/read/';
```
6. Import CSV file and parse with json function, import into json table
```SQL
CREATE  TABLE pipe_json_load(col JOSN);
COPY INTO pipe_json_load FROM(
SELECT parse_json(col)
FROM  VOLUME 
hz_csv_volume(
col
)
USING csv 
OPTIONS ('header' = 'false')
);
```
```markdown
7. Use SQL and dimension tables to join during the import process. Filter the data that needs to be imported
```
```
--The data is as follows
create table departments (
  dept_id int ,
  dept_name varchar,
  location varchar
);
insert into departments values
(10, 'Sales', 'Beijing'),
(20, 'R&D', 'Shanghai'),
(30, 'Finance', 'Guangzhou'),
(40, 'HR', 'Shenzhen');
--The employee table is as follows
CREATE  TABLE employees (
          emp_id int,
          emp_name varchar,
          dept_id int,
          salary int
);
--The data stored in the volume is as follows
10,"Sales","Beijing",
20,"R&D","Shanghai",
30,"Finance","Guangzhou",
40,"HR","Shenzhen",
--Only import the data of the sales department
COPY OVERWRITE employees FROM 
(SELECT f0::int,f1,f2::int,f3::int FROM 
VOLUME  my_volume
USING csv
files('dau_unload/employees/part00001.csv') 
join
departments   
on f3=dept_id
where dept_name='Sales'
);
```
```markdown
8. Import Parquet files and use regular expressions to match corresponding files
```
```SQL
COPY INTO hz_parquet_table
FROM VOLUME hz_parquet_volume
USING parquet 
REGEXP 'month=0[1-5].*.parquet';
```
9. Import BSON File

```SQL
--LOAD FROM VOLUME USING BSON FORMAT
COPY INTO t_bson 
FROM VOLUME my_external_vol(
        name string, 
        age bigint, 
        city string, 
        interests array<string>
)
USING BSON
FILES( 'data.bson');
```

^
