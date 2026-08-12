# Export Data to VOLUME - COPY INTO VOLUME

**Objective**: Export a table or query result as files to a specified path in a Volume.

## Syntax

```Plain
COPY INTO { VOLUME <external_volume_name> | TABLE VOLUME <table_name> | USER VOLUME }
SUBDIRECTORY '<path>'
FROM { [<namespace>.]<table_name> | (<query>) }
FILE_FORMAT = ( TYPE = { CSV | TEXT | PARQUET } [ formatTypeOptions ] )
[ copyOptions ]
```

### Parameter Description

* **formatTypeOptions**
  * COMPRESSION: Optional. Specifies the compression format; the default is no compression. Supported formats: GZIP, ZSTD, DEFLATE. Example: `COMPRESSION = 'GZIP'`

* **copyOptions**
  * `filename_prefix = '<prefix_name>'`: Optional. Sets a prefix for output file names. Example: `filename_prefix = 'my_prefix_'`
  * `filename_suffix = '<suffix>'`: Optional. Sets a suffix for output file names. Example: `filename_suffix = '.data'`
  * `include_job_id = 'TRUE' | 'FALSE'`: Optional. Sets whether to include the job ID in file names. Defaults to not included when omitted. Example: `include_job_id = 'TRUE'`

## Usage Examples

* Export table data to a Volume

  ```sql
  -- Unload to external volume
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV);

  -- Unload to table volume
  COPY INTO TABLE VOLUME dau SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV);

  -- Unload to user volume
  COPY INTO USER VOLUME SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV);


  SHOW VOLUME DIRECTORY my_external_vol;

  relative_path                                   url                                                                size last_modified_time
  ----------------------------------------------- ------------------------------------------------------------------ ---- -------------------
  dau_unload/part00001.csv                        oss://your-bucket/dau_unload/part00001.csv                        75   2024-05-29 17:03:25
  ```

* Export query results to a Volume

  ```sql
  -- copy from query
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM (SELECT * FROM DAU LIMIT 5)
  FILE_FORMAT = (TYPE = CSV);
  ```

* Set the file format during export

  ```sql
  -- copy from table to external volume
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV);

  -- COPY_OPTION: unload and compress with gzip
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM (SELECT * FROM DAU LIMIT 5)
  FILE_FORMAT = (TYPE = CSV COMPRESSION = 'GZIP');

  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = PARQUET COMPRESSION = 'GZIP');
  ```

* Set task parameters during export

  ```sql
  -- COPY_OPTION: unload and add prefix to file names
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV)
  FILENAME_PREFIX = 'my_prefix_';

  -- COPY_OPTION: unload and add suffix to file names
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV)
  FILENAME_SUFFIX = '.data';

  -- COPY_OPTION: unload and add job id to file names
  COPY INTO VOLUME my_external_vol SUBDIRECTORY 'dau_unload/'
  FROM TABLE dau
  FILE_FORMAT = (TYPE = CSV)
  INCLUDE_JOB_ID = 'TRUE';
  ```

## Constraints and Limitations

* Requires JDBC driver version 1.3.5 or above.

## Related Documentation

- [Copy Files Between Volumes - COPY FILES INTO VOLUME](copy-files-into-volume.md): copy existing files verbatim from one Volume to another
