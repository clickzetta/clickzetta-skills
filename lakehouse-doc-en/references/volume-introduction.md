# Volume Object

Volume is Singdata Lakehouse's object storage mount point, used to access files in external object storage (OSS/COS/S3) or as Lakehouse's built-in file storage space.

## What is Volume

A Volume is similar to the concept of "external table" or "mount point" in traditional databases, but it is oriented toward **files** rather than **tables**. With Volume, you can:

- Directly query CSV/JSON/Parquet files in object storage
- Import files from object storage into Lakehouse tables
- Export Lakehouse table data to object storage
- Manage Lakehouse's built-in file storage space

## Volume Types

Lakehouse provides four Volume types, categorized by **creation method**:

### Automatically Created Volumes

#### User Volume

User-level file storage space, automatically available for each user.

```sql
-- Upload files to User Volume
PUT file:///local/data.csv TO USER VOLUME;

-- Download files from User Volume
GET USER VOLUME FILE 'data.csv' TO file:///local/;

-- List files in User Volume
SHOW USER VOLUME DIRECTORY;
```

#### Table Volume

Table-level file storage space, automatically associated with each table.

```sql
-- Upload files to Table Volume
PUT file:///local/data.csv TO TABLE VOLUME my_table FILE 'data.csv';

-- Query Table Volume files
SELECT * FROM TABLE VOLUME my_table USING CSV;
```

### Explicitly Created Volumes

#### External Volume (Mount External Storage)

Created via `CREATE EXTERNAL VOLUME`, mounts external object storage (OSS/COS/S3).

```sql
-- Create storage connection
CREATE STORAGE CONNECTION my_oss_conn
    TYPE oss
    ENDPOINT = 'oss-cn-shanghai.aliyuncs.com'
    ACCESS_ID = 'xxx'
    ACCESS_KEY = 'xxx';

-- Create External Volume
CREATE EXTERNAL VOLUME my_vol
    LOCATION 'oss://my-bucket/data/'
    USING CONNECTION my_oss_conn;
```

#### Named Volume (Using Internal or External Storage)

Created via `CREATE VOLUME`, a type of External Volume emphasizing explicit user creation with a custom name.

```sql
-- Create a Named Volume using internal storage
CREATE VOLUME my_named_volume
    DIRECTORY = (enable = true, auto_refresh = true)
    RECURSIVE = true;
```

> ⚠️ **Note**: Named Volume is a type of External Volume. External Volume can mount external storage (OSS/COS/S3) or use internal storage. Named Volume emphasizes explicit user creation with a custom name, distinct from automatically generated User/Table Volumes.

### Type Comparison

| Type | Creation Method | Storage Location | Applicable Scenarios |
|---|---|---|---|
| User Volume | Auto-created | Internal | Upload/download local files, RAG knowledge base |
| Table Volume | Auto-created (one per table) | Internal | Table-associated ETL files, batch import/export |
| External Volume | `CREATE EXTERNAL VOLUME` | External (OSS/COS/S3) | Mount existing object storage |
| Named Volume | `CREATE VOLUME` | Internal or external | Cross-team shared resources |

## Volume Usage Scenarios

| Scenario | Usage |
|---|---|
| Import data from OSS | `COPY INTO table FROM VOLUME my_vol USING CSV` |
| Export data to OSS | `COPY INTO VOLUME my_vol FROM table USING PARQUET` |
| Query files directly | `SELECT * FROM VOLUME my_vol USING PARQUET FILES ('data.parquet')` |
| Upload local files | `PUT file:///local/data.csv TO USER VOLUME` |
| RAG knowledge base | Upload documents to Volume, vectorize via unstructured ETL pipeline |

## Volume and Pipe Relationship

Pipe is Lakehouse's continuous data ingestion pipeline. When a Pipe ingests data from object storage (OSS/S3/COS), it depends on Volume at the lower level to access files:

```
Object Storage (OSS/S3/COS)
         |
     [Volume] ---- Mount point, access files
         |
      [Pipe] ---- Continuous ingestion pipeline
         |
     [Table] ---- Structured data in Lakehouse
```

- **Volume** provides file access capability, mounting external object storage
- **Pipe** provides continuous streaming capability, monitoring new files in Volume and auto-importing them into tables
- Together, they automate the "Object Storage -> Lakehouse Table" data flow

**Typical Usage**:
```sql
-- Create External Volume to mount OSS
CREATE EXTERNAL VOLUME my_vol LOCATION 'oss://bucket/data/' USING CONNECTION oss_conn;

-- Create Pipe for continuous ingestion of new files in Volume
CREATE PIPE my_pipe AS
    COPY INTO orders FROM VOLUME my_vol USING CSV;
```

## Volume and Table Relationship

There is a **bidirectional data flow** relationship between Volume and Table:

```
Object Storage (OSS/S3/COS)
         |
     [Volume] ---- Mount point, access files
         |
    COPY INTO ---- Bidirectional data transfer
         |
     [Table] ---- Structured data in Lakehouse
```

**Data from Volume to Table (Import)**:
```sql
-- Import file data from Volume into table
COPY INTO orders FROM VOLUME my_vol USING CSV;
```

**Data from Table to Volume (Export)**:
```sql
-- Export table data to Volume
COPY INTO VOLUME my_vol SUBDIRECTORY 'export/' FROM orders FILE_FORMAT = (TYPE = PARQUET);
```

- Volume manages **files**; Table manages **structured data**
- Volume is the channel for data entering the lake and the exit for data leaving the lake
- Table is the subject of data processing; processing results can be exported to external storage via Volume

## Related Documentation

- [Volume Overview](datalake_volume.md)
- [External Volume](external_volume.md)
- [Internal Volume](internal_volume.md)
- [Import Data from Volume](from_volume_to_table.md)
- [Export Data to Volume](from_lakehouse_to_volume.md)
