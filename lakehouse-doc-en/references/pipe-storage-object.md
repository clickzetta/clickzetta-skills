# Continuous Data Import from Object Storage Using Pipe

Pipe is a powerful data import feature in the Lakehouse platform. It allows users to read data directly from object storage at a fixed frequency and import it into the Lakehouse. By implementing a file detection mechanism, Pipe supports micro-batch processing to load files, enabling users to quickly access the latest data. It is particularly suitable for scenarios requiring real-time or near-real-time data processing.

## How Pipe Works

1. **File Detection**:

   1. **EVENT\_NOTIFICATION\_MODE**: Requires enabling message service, using Alibaba Cloud Message Service to notify Lakehouse of new file uploads. Currently, only Alibaba Cloud OSS and AWS S3 are supported.
   2. **LIST\_PURGE mode**: Periodically scans directories, synchronizes unrecorded files, and deletes the original files after synchronization.

2. **COPY Statement**: Defines the source location of the data files and the target table, supporting multiple file formats.

3. **Automated Loading**: Automatically detects new files and executes the COPY statement.

4. **Duplicate Import Prevention Mechanism**: To avoid duplicate imports, the load\_history function records the copy import history files of the current table. When Pipe executes, it deduplicates based on the load\_history table name and the import file name, ensuring that existing files are not imported again. If you need to import already recorded files, you can manually execute the copy command. The load\_history records are currently retained for 7 days.

5. **Pipe Import Job History**: Since each execution is a Pipe-issued copy, you can view all operations in the job history. By filtering with the query\_tag in the job history, all pipe-executed copy jobs will be tagged with the format `pipe.``workspace_name``.schema_name.pipe_name`, making it easy to track and manage.

## Use Cases

* **Real-time Data Synchronization**: When your data is stored in object storage and needs to be frequently synchronized to obtain the latest data in a timely manner.
* **Cost Optimization**: Importing and exporting data on object storage can avoid incurring network public traffic costs. Especially within the same region, you can specify object storage for intranet transmission, further reducing costs.

## Notes

* When using EVENT\_NOTIFICATION\_MODE, you need to use the role arn authorization method to create the storage connection.
* LIST\_PURGE mode supports both key and role arn authorization methods.
* **Recommended File Size**: gzip compressed files are recommended to be 50MB. Uncompressed CSV and PARQUET files are recommended to be between 128MB and 256MB.
* **Data Loading Order**: **Data loading cannot guarantee strict order**.
* **Pipe Latency**: Pipe loading time is affected by various factors, including file format, size, and the complexity of the COPY statement.

## Cost

Charged based on the computing resources used when loading files.

## PIPE Syntax

```SQL
-- Syntax for creating a Pipe from object storage
CREATE PIPE [ IF NOT EXISTS ] <pipe_name>
    VIRTUAL_CLUSTER = 'virtual_cluster_name'
    INGEST_MODE='LIST_PURGE'|'EVENT_NOTIFICATION'
    [COPY_JOB_HINT='']
AS <copy_statement>;
```

* `<pipe_name>`: The name of the Pipe object you want to create.
* `VIRTUAL_CLUSTER`: Specify the name of the virtual cluster.
* `INGEST_MODE`: Set to `LIST_PURGE` or `EVENT_NOTIFICATION` to determine the data import mode.
* `COPY_JOB_HINT`: Optional, Lakehouse reserved parameter
* `IGNORE_TMP_FILE`: Values can be `true` or `false`, with the default value being `true`. This parameter supports filtering files or directories that start with a dot (`.`) or `_temporary`. For example, `s3://my_bucket/a/b/.SUCCESS`, `oss://my_bucket/a/b/_temporary/`, or `oss://my_bucket/a/b/_temporary_123/`.

## Supported File Formats

Refer to [COPY INTO import](copy-into-table.md).

## Using PIPE Load Cases

### Using Scan File Mode

**Specific Steps**

Step 1: Create connection and volume

```SQL
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

Step 2: Execute the copy command separately to see if it can be imported successfully

Step 2: Execute the copy command separately to see if it can be imported successfully

```SQL
copy into pipe_purge_mode from volume pipe_volume(id int,col string) 
using csv OPTIONS(
  'header'='false'
) ;
```

 Step 3: Use the above statement to build the pipe object

```SQL
create pipe volume_pipe_list_purge
  VIRTUAL_CLUSTER = 'default'
  -- Execute to get the latest file using scan file mode
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

### Step 4: View Pipe Execution History and Imported Files

* View the execution status of pipe copy jobs

Filter through the job history using the query\_tag. All copy jobs executed by the pipe will be tagged in the query\_tag with the format: pipe.workspace\_name.schema\_name.pipe\_name

* View the history of files imported by copy jobs

```SQL
select * from load_history('schema_name.table_name');
```

### Using Message Service Notification Mode (Only Supports Alibaba Cloud OSS and AWS S3)

Step 1: Enable Alibaba Cloud Message Service (MNS)

1. Enable the Message Service MNS in the Alibaba Cloud console.
2. Configure MNS to listen to the OSS (Object Storage Service) folder to be synchronized. [Refer to the specific documentation](https://help.aliyun.com/zh/mns/user-guide/create-a-rule-to-generate-oss-event-notifications?spm=a2c4g.11186623.0.i14)

Step 2: Authorize Lakehouse to Read OSS
Refer to the method of using role arn [Alibaba Cloud Storage Connection Creation](aliyun_storage_connection.md) to authorize Lakehouse to read the corresponding OSS Bucket.

Step 3: Authorize MNS to Lakehouse

```
In the Alibaba Cloud RAM console, grant the `AliyunMNSFullAccess` permission to the Role from step two, which in the case of step two is CzUDFRole.
```

Step 4: Create Storage Connection

```SQL
CREATE STORAGE CONNECTION my_connection_exnet_role
    TYPE oss
    REGION = 'cn-hangzhou'  -- Select according to the region where OSS is located
    ROLE_ARN = 'acs:ram::...:role/czudfrole'  -- Replace with your Role ARN
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com';  -- Select Endpoint according to the region where OSS is located
```

Step 5: Create Volume

```SQL
CREATE EXTERNAL VOLUME my_volume_exnet_role
    LOCATION 'oss://function-compute-my1/autoloader'  -- Replace with the path of the OSS Bucket
    USING connection my_connection_exnet_role
    DIRECTORY = (
        enable = TRUE,
        auto_refresh = TRUE
    )
    RECURSIVE = TRUE;
```

Step 6: Create Pipe

```SQL
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

^
