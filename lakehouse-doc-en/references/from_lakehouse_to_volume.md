# Export Data to VOLUME - COPY INTO VOLUME

**Objective**: Export a table or a query result to a specified path in the Volume

## Syntax

```SQL
COPY INTO { VOLUME external_volume_name | TABLE VOLUME table_name  | USER VOLUME }  
SUBDIRECTORY '<path>'
FROM { [<namespace>.]<table_name> |(<query>)}
FILE_FORMAT = ( TYPE = { CSV|TEXT|PARQUET }  [ formatTypeOptions ]  ) 
[ copyOptions ]
```

### **Parameter Description**

* **formatTypeOptions**

  * COMPRESSION: Optional parameter. Specifies the compression format, default is no compression. Supports GZIP, ZSTD, DEFLATE compression, for example: `COMPRESSION = 'GZIP'`

* **copyOptions**

  * filename\_prefix = '\<prefix\_name>'. Optional parameter. Sets the file prefix, for example: `filename_prefix = 'my_prefix_'`
  * filename\_suffix = '\<suffix>'. Optional parameter. Sets the file suffix, for example: `filename_suffix = '.data'`
  * include\_job\_id = 'TRUE' | 'FALSE'. Optional parameter. Sets whether the job ID is included in the file name, default is not to include the job ID if not set. For example: `include_job_id = 'TRUE'`

## Usage Example

* Export table data to Volume

```SQL
-- Unload to external volume
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT = (type = CSV);

-- Unload to table volume
COPY INTO TABLE VOLUME dau SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT = (type = CSV);

-- Unload to user volume
COPY INTO USER VOLUME SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT = (TYPE = CSV )


SHOW VOLUME DIRECTORY my_external_vol;

relative_path                                   url                                                                size last_modified_time  
----------------------------------------------- ------------------------------------------------------------------ ---- ------------------- 
dau_unload/part00001.csv                           oss://your-bucket/dau_unload/part00001.csv                           75   2024-05-29 17:03:25 
```

* Export Query Results to Volume

```SQL
-- copy from query
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM (SELECT * FROM DAU limit 5)
FILE_FORMAT = (type = CSV);
```

* Set the export file format during export

```SQL
-- copy from table to external volume
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT = (type = CSV);

-- COPY_OPTION: Unload and compress with gzip
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM (SELECT * FROM DAU limit 5)
FILE_FORMAT = (TYPE = CSV COMPRESSION = 'GZIP') ;

COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau/' 
FROM TABLE dau
FILE_FORMAT = (type = PARQUET COMPRESSION = 'GZIP');
```

* Set export task parameters during export

```SQL
-- COPY_OPTION: Unload and add prefix to file names
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT = (TYPE = CSV) 
FILENAME_PREFIX = 'my_prefix_';

-- COPY_OPTION: Unload and add suffix to file names
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT = (TYPE = CSV) 
FILENAME_PREFIX = '.data';

-- COPY_OPTION: Unload and add job id to file names
COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/' 
FROM TABLE dau
FILE_FORMAT =  (TYPE = CSV )
INCLUDE_JOB_ID = 'TRUE';
```

## Constraints and Limitations

* Requires JDBC driver version 1.3.5 or above.
* Direct export to object storage location is not currently supported (can be exported to the corresponding object storage location with the help of Volume object).

^
