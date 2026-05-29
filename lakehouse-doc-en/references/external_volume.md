# External Volume

An External Volume is used to mount external object storage (Alibaba Cloud OSS, Tencent Cloud COS, Amazon S3). Through an External Volume, Singdata Lakehouse can directly access and manage files stored in external cloud storage without migrating data into Singdata Lakehouse.

## What Is an External Volume

An External Volume is an object in Singdata Lakehouse that points to a specific path in external object storage. It is created with `CREATE EXTERNAL VOLUME` to mount external object storage (OSS/COS/S3).

> ⚠️ **Note**: A Named Volume (created with `CREATE VOLUME`) is an **internal Volume** — data is stored inside Singdata Lakehouse. It is a different type from an External Volume. See [Named Volume](om-named-volume.md).

With an External Volume, you can:

- Query CSV/JSON/Parquet files directly in object storage
- Import data from object storage into Singdata Lakehouse tables
- Export Singdata Lakehouse table data to object storage
- Manage files in external storage in a unified way

**Key characteristics**:
- Data is stored in external cloud storage; Singdata Lakehouse only stores path metadata
- Supports Alibaba Cloud OSS, Tencent Cloud COS, and Amazon S3

## Creating an External Volume

### Prerequisites

Before creating an External Volume (mounting external storage), you must first create a Storage Connection:

```sql
-- Create an Alibaba Cloud OSS storage connection
CREATE STORAGE CONNECTION IF NOT EXISTS oss_conn
    TYPE oss
    ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'
    ACCESS_ID = 'your_access_key_id'
    ACCESS_KEY = 'your_access_key_secret';
```

### Create an External Volume (Mount External Storage)

```sql
CREATE EXTERNAL VOLUME [IF NOT EXISTS] [schema_name.]<volume_name>
    LOCATION '<storage_url>'
    USING CONNECTION <connection_name>
    DIRECTORY = (
        enable = true,
        auto_refresh = true
    )
    RECURSIVE = true;
```

**Parameter reference**:

| Parameter | Description |
|-----------|-------------|
| `volume_name` | Volume name; must be unique within the same schema |
| `LOCATION` | Object storage path, e.g. `oss://bucket_name/path/` |
| `USING CONNECTION` | Name of the referenced Storage Connection |
| `DIRECTORY.enable` | Whether to enable directory functionality |
| `DIRECTORY.auto_refresh` | Whether to automatically refresh file metadata |
| `RECURSIVE` | Whether to recursively scan subdirectories |

**Example**:

```sql
-- Create an External Volume mounting an OSS bucket
CREATE EXTERNAL VOLUME my_oss_vol
    LOCATION 'oss://mcp-data-hangzhou/test/'
    USING CONNECTION oss_conn
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

### Create a Named Volume

> A Named Volume is an internal Volume. For the creation syntax, see [CREATE VOLUME](create-volume.md). For the usage guide, see [Named Volume](om-named-volume.md).

## Viewing an External Volume

### View Volume Details

```sql
DESC VOLUME my_oss_vol;
+------------------------+--------------------------------+
| info_name              | info_value                     |
+------------------------+--------------------------------+
| name                   | my_oss_vol                     |
| creator                | qiliang                        |
| created_time           | 2026-05-20 00:23:49.074        |
| last_modified_time     | 2026-05-20 00:23:49.074        |
| external               | true                           |
| url                    | oss://mcp-data-hangzhou/test/  |
| connection_name        | quick_start.oss_conn           |
| recursive              | true                           |
| directory_enabled      | true                           |
| directory_auto_refresh | true                           |
+------------------------+--------------------------------+
```

### List Files in a Volume

```sql
SHOW VOLUME DIRECTORY my_oss_vol;
+---------------------------------+--------------------------------------------------------------+----------+---------------------+
| relative_path                   | url                                                          | size     | last_modified_time  |
+---------------------------------+--------------------------------------------------------------+----------+---------------------+
| green_tripdata_2025-03.parquet  | oss://mcp-data-hangzhou/test/green_tripdata_2025-03.parquet  | 1253510  | 2025-09-03 17:33:05 |
| taxi_data.parquet               | oss://mcp-data-hangzhou/test/taxi_data.parquet               | 69964745 | 2025-06-07 03:42:52 |
+---------------------------------+--------------------------------------------------------------+----------+---------------------+
```

## Querying Files in an External Volume

```sql
-- Query a Parquet file
SELECT * FROM VOLUME my_oss_vol
    USING PARQUET
    FILES ('green_tripdata_2025-03.parquet')
    LIMIT 5;

-- Query a CSV file
SELECT * FROM VOLUME my_oss_vol
    USING CSV
    OPTIONS ('header' = 'true')
    FILES ('data.csv')
    LIMIT 5;
```

## Importing External Volume Data into a Table

```sql
-- Create the target table
CREATE TABLE green_trip (
    VendorID INT,
    lpep_pickup_datetime TIMESTAMP,
    trip_distance DOUBLE,
    fare_amount DOUBLE,
    total_amount DOUBLE
);

-- Import data from the Volume
COPY INTO green_trip FROM VOLUME my_oss_vol
    (VendorID INT, lpep_pickup_datetime TIMESTAMP, trip_distance DOUBLE, fare_amount DOUBLE, total_amount DOUBLE)
    USING PARQUET
    FILES ('green_tripdata_2025-03.parquet');
```

## Exporting Data to an External Volume

```sql
-- Export table data to an External Volume
COPY INTO VOLUME my_oss_vol
    SUBDIRECTORY 'export/'
    FROM green_trip
    FILE_FORMAT = (TYPE = CSV HEADER = true);
```

> Named Volumes also support `COPY INTO VOLUME` for export using the same syntax — simply replace `my_oss_vol` with the Named Volume name.

## Refreshing Volume File Metadata

When files in external storage change, you can manually refresh the Volume's file metadata:

```sql
ALTER VOLUME my_oss_vol REFRESH;
```

> ⚠️ **Note**: Only External Volumes (mounted external storage) support the REFRESH operation. Named Volumes (internal storage) do not require refreshing.

## Dropping an External Volume

```sql
DROP VOLUME [IF EXISTS] my_oss_vol;
```

> ⚠️ **Note**: Dropping an External Volume only removes the metadata reference in Singdata Lakehouse — it does not delete the actual files in external object storage or internal storage. To delete files, use the `REMOVE` command first.

## Required Permissions

| Permission | Description |
|------------|-------------|
| READ METADATA | View Volume object metadata |
| READ VOLUME | Read files and directories under the Volume |
| WRITE VOLUME | Write data to the Volume |
| ALTER VOLUME | Modify Volume properties (e.g., REFRESH) |

## Notes

- An External Volume (external storage) only stores path metadata; actual data resides in external cloud storage
- Storage costs for an External Volume (external storage) are charged at the cloud provider's standard rates; there are no additional storage charges on the Singdata Lakehouse side
- Storage costs for a Named Volume (internal storage) are charged at Singdata Lakehouse storage rates
- Cross-cloud creation is not supported: an Alibaba Cloud instance can only create an OSS Connection; a Tencent Cloud instance can only create a COS Connection
- Dropping an External Volume does not delete the actual files in external or internal storage

## Related Documentation

- [Data Lake Storage Management: Volume](datalake_volume.md)
- [Create a Storage Connection](create-storage-connection.md)
- [Using Internal Volumes](internal_volume.md)
- [Import Data from a Volume](from_volume_to_table.md)
- [Export Data to a Volume](from_lakehouse_to_volume.md)
