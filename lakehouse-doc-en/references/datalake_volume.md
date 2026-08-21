# Data Lake Storage Management: Volume

## Overview

Lakehouse Volume is an object in Singdata Lakehouse that represents an object storage location. It provides access to object storage, storage, management, and organization of files, and can be used to store and access files in various formats, including structured, semi-structured, and unstructured data. Volumes can be organized and managed under a Lakehouse Schema just like tables, views, and other objects.

Using the Volume feature brings the following benefits:

- **Unified Data Analysis**: Supports calling AI workloads in Singdata Lakehouse to process images, PDFs, and specially formatted unstructured data in object storage, enabling unified processing and analysis together with structured data on the platform.
- **Unified Permission Management**: Supports using the Singdata Lakehouse platform's permission system for unified permission management of databases, tables, and files in object storage.
- **Unified Data Governance**: Data in object storage is uniformly managed and governed by the Singdata Lakehouse platform.

## Volume Types

Lakehouse Volumes are classified into the following four types by **creation method**:

| Type | Creation Method | Storage Location | Description |
|---|---|---|---|
| **User Volume** | Auto-created | Internal storage | A user-specific personal storage space, each user has one by default |
| **Table Volume** | Auto-created | Internal storage | The file storage area associated with each table by default, permissions consistent with the table |
| **External Volume** | `CREATE EXTERNAL VOLUME` | External storage (OSS/COS/S3) | Mounts external object storage, treating object storage as a data lake |
| **Named Volume** | `CREATE VOLUME` | Internal or external storage | A Volume explicitly created by the user for cross-team resource sharing |

> ⚠️ **Note**: Named Volume is a type of External Volume, emphasizing explicit user creation with a custom name. External Volume can mount external storage (OSS/COS/S3) or use internal storage.

### Type Comparison

| Feature | User Volume | Table Volume | External Volume | Named Volume |
|---|---|---|---|---|
| **Creation Method** | Auto-created | Auto-created (one per table) | `CREATE EXTERNAL VOLUME` | `CREATE VOLUME` |
| **Storage Location** | Internal storage | Internal storage | External storage (OSS/COS/S3) | Internal or external storage |
| **Permission Management** | User owns by default | Consistent with table permissions | Requires separate authorization | Requires separate authorization |
| **Storage Cost** | Lakehouse storage billing | Lakehouse storage billing | Cloud provider storage billing | Lakehouse or cloud provider billing |
| **Typical Scenario** | Upload local files, RAG knowledge base | Table-associated ETL files, batch import/export | Mount existing object storage | Cross-team resource sharing |

## Data Operation Protocols

Volumes support three address formats for referencing files in different scenarios:

| Protocol Type | Address Format | Typical Scenario |
|---|---|---|
| External/Named Volume | `volume://volume_name/path_to_file` | Cross-team resource sharing |
| User Volume | `volume:user://~/path_to_file` | User's personal space |
| Table Volume | `volume:table://table_name/path_to_file` | Table-associated ETL files |

### Address Format Details

**External/Named Volume Format**: `volume://volume_name/upper.jar`

- `volume_name`: The name of the created Volume
- `upper.jar`: The target file name

**User Volume Format**: `volume:user://~/upper.jar`

- `user`: Indicates use of the User Volume protocol
- `~`: Represents the current user, a fixed value
- `upper.jar`: The target file name

**Table Volume Format**: `volume:table://table_name/upper.jar`

- `table`: Indicates use of the Table Volume protocol
- `table_name`: The table name, filled in according to the actual situation
- `upper.jar`: The target file name

## DDL Operations

Supported commands for different Volume types:

| Command | Description | User Volume | Table Volume | External/Named Volume |
|---|---|---|---|---|
| `CREATE VOLUME` | Create a Named Volume | No | No | Yes |
| `CREATE EXTERNAL VOLUME` | Create an External Volume | No | No | Yes |
| `DROP VOLUME` | Drop a Volume | No | No | Yes |
| `DESC VOLUME` | Describe Volume properties | No | No | Yes |
| `SHOW VOLUMES` | List created Volumes | No | No | Yes |
| `SHOW USER VOLUME DIRECTORY` | List User Volume files | Yes | No | No |
| `SHOW TABLE VOLUME DIRECTORY` | List Table Volume files | No | Yes | No |
| `SHOW VOLUME DIRECTORY` | List External/Named Volume files | No | No | Yes |
| `REMOVE` | Delete files from a Volume | Yes | Yes | Yes |
| `PUT` | Upload files to a Volume | Yes | Yes | Yes |
| `GET` | Download files from a Volume | Yes | Yes | Yes |

## Permissions

Creating a Named Volume or External Volume in a schema requires `CREATE VOLUME` on that schema. Dropping an existing Volume requires `DROP VOLUME` on that object.

| Permission | Description |
|---|---|
| READ METADATA | Permission to view Volume object metadata |
| READ VOLUME | Permission to read files and directories under the Volume object. Required when viewing the file list under a Volume, reading Volume files via SQL, and downloading files via the GET command |
| WRITE VOLUME | Permission to write data to a Volume. Required when uploading files via the PUT command and deleting files via the REMOVE command |
| ALTER VOLUME | Permission required for the ALTER VOLUME command. For example: `ALTER VOLUME <volume_name> REFRESH` to refresh the file metadata information under the Volume (External Volume only) |
| DROP VOLUME | Drop the specified Named Volume or External Volume |
| ALL PRIVILEGES | All privileges on the Volume object |

The `VOLUME` suffix in a privilege name is optional, so both `READ` and `READ VOLUME` are accepted. Use the full privilege names for clarity; `SHOW GRANTS` displays the full names.

## Cost

- **External Volume**: No additional storage cost on the Lakehouse side; storage costs are charged according to the cloud provider's standard rates.
- **Named Volume (internal storage)**: Lakehouse storage fees are charged based on the actual storage size.
- **User Volume / Table Volume**: Lakehouse storage fees are charged based on the actual storage size.

## Constraints and Limitations

- The size of a single uploaded file must not exceed 5 GB.
- JDBC driver version 1.4.4 or above is required to support local PUT/GET interfaces.
- External Volume does not support cross-cloud-provider creation: Alibaba Cloud instances can only create OSS Connections, and Tencent Cloud instances can only create COS Connections.

## Related Links

- [Internal Volume Usage](internal_volume.md)
- [External Volume Usage](external_volume.md)
- [Alibaba Cloud OSS VOLUME Creation](oss_volume_creation.md)
- [Tencent Cloud COS VOLUME Creation](cos_volume_creation.md)
- [Amazon S3 VOLUME Creation](s3_volume_creation.md)
- [Query Volume Files](structure_data_analysis.md)
- [Import Data from Volume to Table](from_volume_to_table.md)
- [Export Data to Volume](from_lakehouse_to_volume.md)
