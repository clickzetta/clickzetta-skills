# Export File Using COPY INTO

Export tables or query results to a specified path. You can export a table or query results to a file and save it to a specified path in the Volume. Please note that if a file with the same name already exists at the specified path, it will be overwritten.

Notes

* **Default Filename**: When exporting from Lakehouse, the default filename is the same. Therefore, if you run the export operation multiple times and specify the same subdirectory (SUBDIRECTORY), the new file will overwrite the previously exported file.
* **Avoid Overwriting**: To prevent accidentally overwriting existing files, make sure to use a unique filename or subdirectory each time you export.

## Syntax

```SQL
---Syntax
COPY INTO { VOLUME external_volume_name | TABLE VOLUME table_name  | USER VOLUME }  
SUBDIRECTORY '<path>'
FROM { [schema.]<table_name> | ( <query> ) }
FILE_FORMAT = ( TYPE = { CSV  | PARQUET | JSON }  [ formatTypeOptions ]  ) 
[ copyOptions ]
```

### Parameter Description

* COPY INTO: Indicates appending data to the directory

* VOLUME supports external\_volume\_name: For detailed introduction, refer to [Volume Introduction](datalake_volume.md)
  * external\_volume\_name: The external storage location specified by the customer, Singdata only retains the path metadata. Supported storage products include: Alibaba Cloud OSS, Tencent Cloud COS, Amazon S3. The creation process can be referred to in [CONNECTION Creation](datalake_storageconnection.md) and [VOLUME Creation](datalake_volume_object.md)
  * Table Volume: Internal storage of Lakehouse, stored together with internal table objects under the specified Schema path
  * User Volume: The file storage area associated with the user account, the Workspace User has default management permissions for this area. Each Workspace by default has a User Volume with management permissions

```SQL
--1. Import data into external_volume. Prerequisite: external_volume must be created
COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);
--View files in the volume
--show volume directory
SHOW VOLUME DIRECTORY my_volume SUBDIRECTORY 'dau_unload/';
+--------------------------+----------------------------------------------------------------+------+---------------------+
|      relative_path       |                              url                               | size | last_modified_time  |
+--------------------------+----------------------------------------------------------------+------+---------------------+
| dau_unload/part00001.csv | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv | 105  | 2024-12-27 16:49:01 |
+--------------------------+----------------------------------------------------------------+------+---------------------+

--2. Import data into user volume
COPY INTO USER VOLUME SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);
SHOW  USER VOLUME DIRECTORY  SUBDIRECTORY 'dau_unload/';
+--------------------------+-------------------------------------------------------------------------------------------------------------------+------+---------------------+
|      relative_path       |                                                        url                                                        | size | last_modified_time  |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+------+---------------------+
| dau_unload/part00001.csv | oss://lakehouse-hz-uat/86/workspaces/qingyun_6552637055735457988/internal_volume/user_13/dau_unload/part00001.csv | 105  | 2024-12-27 16:52:06 |
+--------------------------+-------------------------------------------------------------------------------------------------------------------+------+---------------------+
--Delete files in user volume
REMOVE  VOLUME my_volume  FILE 'dau_unload/part00001.csv'

--3. Import data into table volume
COPY INTO TABLE VOLUME birds  SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);
SHOW  TABLE VOLUME  DIRECTORY  birds SUBDIRECTORY 'dau_unload/';
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------+---------------------+
|      relative_path       |                                                                 url                                                                 | size | last_modified_time  |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------+---------------------+
| dau_unload/part00001.csv | oss://lakehouse-hz-uat/86/workspaces/qingyun_6552637055735457988/internal_volume/table_6808843871866704121/dau_unload/part00001.csv | 105  | 2024-12-27 16:57:54 |
+--------------------------+-------------------------------------------------------------------------------------------------------------------------------------+------+---------------------+
--Delete files in table volume
REMOVE TABLE VOLUME birds  FILE 'dau_unload/part00001.csv';
```

***

* **SUBDIRECTORY**: Specify the subpath, the parameter must be filled in. For example: \`subdirectory 'month=02'

* **FROM**: Supports direct export of data from the table, directly write the query

```SQL
 --Directly specify the table
 COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
 FROM TABLE birds
 file_format = (type = CSV);
 --Export the SQL result set
 COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
 FROM  (select * from birds limit 1)
 file_format = (type = CSV);
```

* **formatTypeOptions**: File format, supports CSV, TEXT, PARQUET, JSON. The JSON export format is [JSON LINE](https://jsonlines.org/)

* Parameters supported by CSV format:
  * sep: Column separator, default is ",". Supports a maximum length of 1 character, for example: `sep=','`
  * compression: Configure file compression format. Supported compression formats are: gzip/zstd/zlib. For example: `compression='gzip'`
  * lineSep: Line separator, default value is "\n". Supports a maximum length of 2 characters, for example: `lineSep='$'`
  * quote: Set a single character used to escape quote values. The default value is double quotes `"`, for example: `quote='"'`
  * header: Whether to parse the header, default is false. Boolean type, for example: `header='true'`
  * timeZone: Configure time zone, no default value. Used to specify the time zone of the time format in the file. For example: `timeZone = 'Asia/Shanghai'`
  * escape: Used to escape quotes in quoted values, default value is "", for example: `escape='\'`
  * nullValue: Used to determine what content should be Null, default value is `""`, for example nullValue='\\\N' or nullValue=r'\N'. Using r can avoid needing escape characters, refer to [regular expression escape](regexp-statement.md)
  * multiLine: Whether there are multi-line csv records, default value is `false`, if there are such records, configure `multiLine='true'`

```SQL
--Specify delimiter as | and compression
COPY INTO VOLUME my_volume  SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (
    type= CSV
    sep='|'
    compression='gzip'
);
```

* Parameters supported in JSON format:
  * compression: Whether the source file/target file is compressed, default is no compression, configuration like `'compression'='gzip'`
  * ```SQL
    COPY INTO VOLUME my_volume  SUBDIRECTORY 'dau_unload/'
    FROM TABLE birds
    file_format = (
        type= json
    );
    ```
* Parquet, ORC, BSON format: None
* ```SQL
  COPY INTO VOLUME my_volume  SUBDIRECTORY 'dau_unload/'
  FROM TABLE birds
  file_format = (
      type= parquet
  );
  ```
* **copyOptions**

  * filename\_prefix = '\<prefex\_name>'. Optional parameter. Sets the file prefix, for example: filename\_prefix = 'my\_prefix\_'

```SQL
--Add prefix to the file
COPY INTO VOLUME my_volume  SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (
    type= json
  
)
filename_prefix='birds'
;
--View directory, the first line has the prefix birds added
SHOW VOLUME DIRECTORY my_volume SUBDIRECTORY 'dau_unload/';

+-------------------------------+---------------------------------------------------------------------+------+---------------------+
|         relative_path         |                                 url                                 | size | last_modified_time  |
+-------------------------------+---------------------------------------------------------------------+------+---------------------+
| dau_unload/birds00001.json    | oss://lakehouse-perf-test/test_insert/dau_unload/birds00001.json    | 295  | 2024-12-27 17:29:20 |
| dau_unload/part00001.csv      | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv      | 105  | 2024-12-27 17:15:40 |
| dau_unload/part00001.csv.gzip | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv.gzip | 104  | 2024-12-27 17:19:33 |
| dau_unload/part00001.json     | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.json     | 295  | 2024-12-27 17:24:26 |
| dau_unload/part00001.parquet  | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.parquet  | 1886 | 2024-12-27 17:27:15 |
| dau_unload/part00001.text     | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.text     | 87   | 2024-12-27 17:25:34 |
+-------------------------------+---------------------------------------------------------------------+------+---------------------+
```

* filename\_suffix = '\<suffix>'. Parameter. Set the file suffix, for example: filename\_suffix = '.data'

```SQL
        -- Add suffix
        COPY INTO VOLUME my_volume  SUBDIRECTORY 'dau_unload/'
        FROM TABLE birds
        file_format = (
            type= json
          
        )
        filename_suffix='.data';
        -- View directory, as the fourth line added the prefix birds
        SHOW VOLUME DIRECTORY my_volume SUBDIRECTORY 'dau_unload/';
        +-------------------------------+---------------------------------------------------------------------+------+---------------------+
        |         relative_path         |                                 url                                 | size | last_modified_time  |
        +-------------------------------+---------------------------------------------------------------------+------+---------------------+
        | dau_unload/birds00001.json    | oss://lakehouse-perf-test/test_insert/dau_unload/birds00001.json    | 295  | 2024-12-27 17:29:20 |
        | dau_unload/part00001.csv      | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv      | 105  | 2024-12-27 17:15:40 |
        | dau_unload/part00001.csv.gzip | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv.gzip | 104  | 2024-12-27 17:19:33 |
        | dau_unload/part00001.data     | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.data     | 295  | 2024-12-27 17:33:49 |
        | dau_unload/part00001.json     | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.json     | 295  | 2024-12-27 17:24:26 |
        | dau_unload/part00001.parquet  | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.parquet  | 1886 | 2024-12-27 17:27:15 |
        | dau_unload/part00001.text     | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.text     | 87   | 2024-12-27 17:25:34 |
        +-------------------------------+---------------------------------------------------------------------+------+---------------------+
```

* include\_job\_id = 'TRUE' | 'FALSE'. Optional parameter. Sets whether the job ID is written into the file name. If not set, the default is not to write the job ID. For example: include\_job\_id = 'TRUE'

```
-- The exported file includes jobid
COPY INTO VOLUME my_volume  SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (
    type= json
)
include_job_id = 'TRUE' ;
-- View the directory, as in line 8, the exported file includes jobid
+--------------------------------------------------------+----------------------------------------------------------------------------------------------+------+---------------------+
|                     relative_path                      |                                             url                                              | size | last_modified_time  |
+--------------------------------------------------------+----------------------------------------------------------------------------------------------+------+---------------------+
| dau_unload/birds00001.json                             | oss://lakehouse-perf-test/test_insert/dau_unload/birds00001.json                             | 295  | 2024-12-27 17:29:20 |
| dau_unload/part00001.csv                               | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv                               | 105  | 2024-12-27 17:15:40 |
| dau_unload/part00001.csv.gzip                          | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.csv.gzip                          | 104  | 2024-12-27 17:19:33 |
| dau_unload/part00001.data                              | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.data                              | 295  | 2024-12-27 17:33:49 |
| dau_unload/part00001.json                              | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.json                              | 295  | 2024-12-27 17:24:26 |
| dau_unload/part00001.parquet                           | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.parquet                           | 1886 | 2024-12-27 17:27:15 |
| dau_unload/part00001.text                              | oss://lakehouse-perf-test/test_insert/dau_unload/part00001.text                              | 87   | 2024-12-27 17:25:34 |
| dau_unload/part202412271736045501gmspelya5o900001.json | oss://lakehouse-perf-test/test_insert/dau_unload/part202412271736045501gmspelya5o900001.json | 295  | 2024-12-27 17:36:04 |
+--------------------------------------------------------+----------------------------------------------------------------------------------------------+------+---------------------+
```

## Usage Example

### Export data to user volume

```SQL
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');

COPY INTO USER VOLUME SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);
--Check if the export was successful
SHOW  USER VOLUME DIRECTORY  SUBDIRECTORY 'dau_unload/';
--Delete the file to avoid occupying storage
REMOVE  VOLUME my_volume  FILE 'dau_unload/part00001.csv';
```

### Export Data to Table Volume

```SQL
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');
COPY INTO TABLE VOLUME birds  SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);
--Check if the export was successful
SHOW  TABLE VOLUME  DIRECTORY  birds SUBDIRECTORY 'dau_unload/';
--Delete the file to avoid occupying storage
REMOVE  TABLE  VOLUME birds  FILE 'dau_unload/part00001.csv';
```

Exporting to an external volume requires creating a VOLUME and CONNECTION. The creation process can be referenced in [CONNECTION creation](datalake_storageconnection.md) and [VOLUME creation](datalake_volume_object.md)

### Export data to oss

```SQL
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');
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
-- Export data to test_insert subdirectory
COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);

```

### Export data to COS

```
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');
-- Create cos connection
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
-- Export data to the test_insert subdirectory
COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);

```

### Export Data to S3

```SQL
-- Create table
CREATE TABLE birds (
    id INT,
    name VARCHAR(50),
    wingspan_cm FLOAT,
    colors STRING
);
INSERT INTO birds (id, name, wingspan_cm, colors) VALUES
    (1, 'Sparrow', 15.5, 'Brown'),
    (2, 'Blue Jay', 20.2, 'Blue'),
    (3, 'Cardinal', 22.1, 'Red'),
    (4, 'Robin', 18.7, 'Red","Brown');
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
-- Export data to test_insert subdirectory
COPY INTO VOLUME my_volume SUBDIRECTORY 'dau_unload/'
FROM TABLE birds
file_format = (type = CSV);
```

^
