# Continuous Data Import from Object Storage Using Pipe

Pipe is a powerful data import feature in the Singdata Lakehouse platform. It allows users to read data directly from object storage at a fixed frequency and import it into the Lakehouse. By implementing a file detection mechanism, Pipe supports micro-batch file loading, enabling quick access to the latest data. It is particularly suitable for scenarios requiring real-time or near-real-time data processing.

Think of an object storage Pipe as a program that continuously scans an inbox — you simply upload files to OSS/S3/COS, and it automatically detects and imports them without any manual trigger.

## How Pipe Works

1. **File Detection**:

   1. **EVENT\_NOTIFICATION\_MODE**: Requires enabling a message service. Uses Alibaba Cloud Message Service to notify the Lakehouse of new file uploads. Currently only Alibaba Cloud OSS and AWS S3 are supported.
   2. **LIST\_PURGE mode**: Periodically scans directories, synchronizes unrecorded files, and deletes source files after synchronization.

2. **COPY Statement**: Defines the source location of data files and the target table, supporting multiple file formats.

3. **Automated Loading**: Automatically detects new files and executes the COPY statement.

4. **Duplicate Import Prevention**: To avoid duplicate imports, the `load_history` function records the COPY import history for the current table. When Pipe executes, it deduplicates based on the `load_history` table name and import file name, ensuring already-imported files are not re-imported. If you need to re-import a recorded file, manually execute a COPY command. Records in `load_history` are retained for 7 days.

5. **Pipe Import Job History**: Since each execution is a Pipe-issued COPY, you can view all operations in the job history. Filter by `query_tag` in the job history — all COPY jobs executed by a Pipe are tagged with the format `pipe.``workspace_name``.schema_name.pipe_name`, making it easy to track and manage.

## Use Cases

* **Real-time Data Synchronization**: When data is stored in object storage and needs frequent synchronization to access the latest data.
* **Cost Optimization**: Importing and exporting data via object storage avoids public network traffic costs. Within the same region, you can specify intranet transfer for object storage to further reduce costs.

## Notes

* When using EVENT\_NOTIFICATION\_MODE, you must use the role ARN authorization method to create the storage connection.
* LIST\_PURGE mode supports both access key and role ARN authorization.
* **Recommended File Size**: gzip compressed files should be around 50 MB. Uncompressed CSV and Parquet files should be between 128 MB and 256 MB.
* **Data Loading Order**: **Data loading cannot guarantee strict ordering**.
* **Pipe Latency**: Pipe loading time is affected by various factors, including file format, size, and the complexity of the COPY statement.
* **Pipe and Volume Mapping**: Each Pipe requires a dedicated Volume and cannot be shared.
* Modifying the COPY statement logic is not supported. If you need to change it, delete the Pipe and recreate it.
* When modifying a Pipe's `COPY_JOB_HINT`, the new settings overwrite existing hints. If your Pipe already has hints such as `{"cz.sql.split.kafka.strategy":"size"}`, you must include all required hints together when setting new ones; otherwise existing hints will be overwritten. Separate multiple parameters with commas.
* The COPY statement inside a PIPE does not support the `files`, `regexp`, or `subdirectory` parameters.


## Cost

Charged based on the computing resources used when loading files.

## PIPE Syntax

```sql
-- Syntax for creating a Pipe from object storage
CREATE PIPE [ IF NOT EXISTS ] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    INGEST_MODE='LIST_PURGE'|'EVENT_NOTIFICATION'
    [COPY_JOB_HINT='']
AS <copy_statement>;
```

- `<pipe_name>`: The name of the Pipe object to create.
- `VIRTUAL_CLUSTER`: Specifies the Virtual Cluster name.
- `INGEST_MODE`: Determines the data ingestion mode — choose one:
  - `LIST_PURGE`: Periodically polls and scans the directory — simple to configure, suitable for most scenarios; **deletes source files after a successful import (irreversible)**
  - `EVENT_NOTIFICATION`: Triggers immediately upon receiving an object storage event notification — suitable for near-real-time ingestion where source files must be retained; requires additional MNS queue configuration

  > ⚠️ **Warning**: `LIST_PURGE` mode **permanently deletes** source files from object storage after a successful import. If you need to retain the original files, use `EVENT_NOTIFICATION` mode.
- `COPY_JOB_HINT`: Optional, reserved parameter for Lakehouse.
- `copy_statement`: `<copy_statement>` supports all file parameters. When the `ON_ERROR=CONTINUE|ABORT` parameter is set, it controls error handling during data loading, and the list of imported files is returned:
    * `CONTINUE`: Skips error rows and continues loading subsequent data. Suitable for tolerating partial errors while maximizing data loading completion. Currently, ignorable errors are limited to file format mismatches — for example, the command specifies zip compression but the file uses zstd.
    * `ABORT`: Immediately terminates the entire `COPY` operation. Suitable for strict data quality requirements where any error requires manual inspection.


## Supported File Formats

Refer to [COPY INTO import](copy-into-table.md).

## PIPE Load Examples

### Using Scan File Mode (LIST\_PURGE)

**Step-by-step instructions**

Step 1: Create a connection and volume

```sql
-- Create a connection to connect to object storage
CREATE STORAGE CONNECTION if not exists my_connection_exnet
    TYPE OSS
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_KEY = 'LTAI5tMmbq1Ty1xxxxxxxxx'
    SECRET_KEY = '0d7Ap1VBuFTzNg7gxxxxxxxxxxxx'
    COMMENT = 'OSS public endpoint';

-- Create a volume to map the object storage directory
CREATE EXTERNAL VOLUME pipe_volume
    location 'oss://ossmy/autoloader/pipe/'
    using connection my_connection_exnet
    directory = (
        enable=true,
        auto_refresh=true
    )
    recursive=true;
    
```

Step 2: Run the COPY command standalone to verify it imports successfully

```sql
copy into pipe_purge_mode from volume pipe_volume(id int,col string) 
using csv OPTIONS(
  'header'='false'
) ;
```

Step 3: Use the above statement to build the Pipe object

```sql
create pipe volume_pipe_list_purge
  VIRTUAL_CLUSTER = 'DEFAULT'
  -- Use scan file mode to get the latest files
  INGEST_MODE = 'LIST_PURGE'
  as
copy into pipe_purge_mode from volume pipe_volume(id int,col string) 
using csv OPTIONS(
  'header'='false'
)
-- Must add purge parameter to delete data after successful import 
purge=true
;
```

Step 4: View Pipe execution history and imported files

* View the execution status of Pipe COPY jobs

Filter by `query_tag` in the job history. All COPY jobs executed by the Pipe are tagged with the format: `pipe.workspace_name.schema_name.pipe_name`

* View the history of files imported by COPY jobs

```sql
select * from load_history('schema_name.table_name');
```

### Using Event Notification Mode (Alibaba Cloud OSS and AWS S3 only)

Step 1: Enable Alibaba Cloud Message Service (MNS)

1. Enable Message Service MNS in the Alibaba Cloud console.
2. Configure MNS to listen to the OSS folder you want to synchronize. [See the documentation](https://help.aliyun.com/zh/mns/user-guide/create-a-rule-to-generate-oss-event-notifications?spm=a2c4g.11186623.0.i14)

Step 2: Authorize Lakehouse to read OSS

Refer to the role ARN method in [Alibaba Cloud Storage Connection Creation](aliyun_storage_connection.md) to authorize Lakehouse to read the corresponding OSS bucket.

Step 3: Grant MNS access to Lakehouse

```
In the Alibaba Cloud RAM console, grant the `AliyunMNSFullAccess` permission to the Role from Step 2 (in the example, this is CzUDFRole).
```


Step 4: Create a Storage Connection

```sql
CREATE STORAGE CONNECTION my_connection_exnet_role
    TYPE oss
    REGION = 'cn-hangzhou'  -- Select according to the region where OSS is located
    ROLE_ARN = 'acs:ram::...:role/czudfrole'  -- Replace with your Role ARN
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com';  -- Select Endpoint based on the OSS region
```

Step 5: Create a Volume

```sql
CREATE EXTERNAL VOLUME my_volume_exnet_role
    LOCATION 'oss://function-compute-my1/autoloader'  -- Replace with your OSS Bucket path
    USING connection my_connection_exnet_role
    DIRECTORY = (
        enable = TRUE,
        auto_refresh = TRUE
    )
    RECURSIVE = TRUE;
```

Step 6: Create a Pipe

```sql
CREATE PIPE my_pipe
VIRTUAL_CLUSTER='TEST_VC'
ALICLOUD_MNS_QUEUE = 'lakehouse-oss-event-queue'  -- Use the created MNS queue
AS
COPY INTO pipe_log_json FROM (
    SELECT parse_json(col) json_col
    FROM volume my_volume_exnet_role(col string)
    USING csv
    OPTIONS ('header' = 'false', 'sep' = '\001', 'quote' = '\0')
);
```

## Status Monitoring and Management

### View Pipe Status


````
DESC PIPE EXTENDED kafka_pipe_stream
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|     info_name      |                                                                                                               info_value                                                            |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| name               | kafka_pipe_stream                                                                                                                                                                   |
| creator            | UAT_TEST                                                                                                                                                                            |
| created_time       | 2025-03-05 10:40:55.405                                                                                                                                                             |
| last_modified_time | 2025-03-05 10:40:55.405                                                                                                                                                             |
| comment            |                                                                                                                                                                                     |
| properties         | ((virtual_cluster,test_alter))                                                                                                                                                      |
| copy_statement     | COPY INTO TABLE qingyun.pipe_schema.kafka_sink_table_1 FROM (SELECT `current_timestamp`() AS ```current_timestamp``()`, CAST(kafka_table_stream_pipe1.`value` AS string) AS `value` |
| pipe_status        | RUNNING                                                                                                                                                                             |
| output_name        | xxxxxxx.pipe_schema.kafka_sink_table_1                                                                                                                                              |
| input_name         | kafka_table_stream:xxxxxxx.pipe_schema.kafka_table_stream_pipe1                                                                                                                     |
| invalid_reason     |                                                                                                                                                                                     |
| pipe_latency       | {"kafka":{"lags":{"0":0,"1":0,"2":0,"3":0},"lastConsumeTimestamp":-1,"offsetLag":0,"timeLag":-1}}                                                                                   |
+--------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

````

### View Pipe Execution History

Since each execution is a Pipe-issued COPY, you can view all operations in the job history. Filter by `query_tag` in the [job history](<web-job-history.md>). All COPY jobs executed by a Pipe are tagged with the format `pipe.``workspace_name``.schema_name.pipe_name` for easy tracking.

### Stop and Start a Pipe

- Pause a Pipe:
```
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = true;
```
- Resume a Pipe:
```
ALTER PIPE pipe_name SET PIPE_EXECUTION_PAUSED = false
```

### Modify Pipe Properties

You can modify Pipe properties one at a time. If multiple properties need to be changed, run the `ALTER` command multiple times. Below are the modifiable properties and their syntax:

```sql
ALTER PIPE pipe_name SET 
   [VIRTUAL_CLUSTER = 'virtual_cluster_name']
   [BATCH_INTERVAL_IN_SECONDS='']
   [BATCH_SIZE_PER_KAFKA_PARTITION='']
   [MAX_SKIP_BATCH_COUNT_ON_ERROR='']
   [RESET_KAFKA_GROUP_OFFSETS='']
   [COPY_JOB_HINT='']
```

Examples:

```
-- Change the compute cluster
ALTER PIPE pipe_name SET VIRTUAL_CLUSTER = 'DEFAULT'
-- Set COPY_JOB_HINT
ALTER PIPE pipe_name SET COPY_JOB_HINT='{"cz.mapper.kafka.message.size": "2000000"}'
```
