# EXTERNAL SCHEMA
**【Preview Release】This feature is currently in the public preview release stage.**
## Introduction

External Schema (EXTERNAL SCHEMA) is a feature provided by Lakehouse that allows querying of external data sources. With EXTERNAL SCHEMA, users can access external metadata services (such as HMS) and perform batch mapping of external tables without having to import data into Lakehouse. For example, by establishing a mapping with a Hive Database and utilizing the Hive Metadata Service (HMS) interface, External Schema can directly obtain Hive metadata information without actually creating table structures in Lakehouse.
Using EXTERNAL SCHEMA offers the following benefits:
1. **Direct Query**: Users can directly query data in external databases (such as Apache Hive) without going through complex data import processes.
2. **Data Transformation and Import**: Combined with the `INSERT INTO ..SELECT` statement, users can achieve data extraction, transformation, and loading (ETL), writing query results directly into Lakehouse tables.
3. **Real-time Join**: EXTERNAL SCHEMA supports real-time joining of Lakehouse tables with data from external data sources, allowing users to query directly when data changes without waiting for data to be reloaded.
4. **Deletion Behavior Explanation**: Deleting an external Schema does not delete the Hive Database, as the external Schema only establishes a mapping relationship with the Hive Database. The deletion operation only removes the external Schema metadata information in Lakehouse.

This design provides great flexibility and convenience as it reduces the need for data migration and enables users to query and analyze data stored in external data sources in real-time.

## Supported Scope

  * Hive on OSS (Alibaba Cloud Object Storage Service)
  * Hive on COS (Tencent Cloud Object Storage Service)
  * Hive on GCS (Google Cloud Object Storage Service)
  * Hive on HDFS (Preview contact Lakehouse support)

## Differences Between External Schema and External Tables

  * **External Schema**: Directly interacts with the Hive Metadata Service (HMS) and obtains Hive metadata information through HMS interfaces.
  * **External Tables**: Users can create tables with custom-defined columns and table names.
  * **External Schema Limitations**: Since it directly maps to HMS, users cannot directly create, delete, or rename tables under an External Schema.
  * **Advantages of External Tables**: Supports operations such as renaming and modifying comments, as they are created under internal Schemas.

## External Schema Cost

  * **Storage Costs**: External tables do not incur storage costs as the data is not stored in Lakehouse.
  * **Compute Costs**: Using external tables for computations consumes compute resources, thus generating compute costs.

## External Schema Permissions

  * **Create External Schema Permission**: Requires the permission to create a Schema (create schema).
  * **Delete External Schema Permission**: Requires the drop permission.
  * **Table Permissions within External Schema**: Currently, individual tables cannot be authorized separately, only ALL TABLES permission is supported.

## Management

Cloud Lakehouse provides commands to create and delete EXTERNAL SCHEMA, enabling users to manage access permissions and configurations for these external data sources as needed.

  * **Creating EXTERNAL SCHEMA**: Users can use the `CREATE EXTERNAL SCHEMA` command to create a new EXTERNAL SCHEMA and begin interacting with external databases. Specific syntax and parameter settings can be found in the [Create EXTERNAL SCHEMA](CREATEEXTERNAlLSCHEMA.md) documentation.
  * **Deleting EXTERNAL SCHEMA**: If an EXTERNAL SCHEMA is no longer needed or if access to the external database needs to be removed, the `DROP SCHEMA` command can be used to delete it. Related steps and precautions are detailed in the [Delete EXTERNAL SCHEMA](DROPSCHEMA.md) documentation.

## Permission Description

  * **Create External Schema Permission**: Requires the permission to create a Schema (create schema).
  * **Delete External Schema Permission**: Requires the drop permission.
  * **Table Permissions within External Schema**: Currently, individual tables cannot be authorized separately, only ALL TABLES permission is supported.

## Constraints and Limitations

  * **Supported Data Sources**: Currently, EXTERNAL SCHEMA primarily supports access to Hive Metastore metadata services, with data stored in HDFS or object storage services from Alibaba Cloud, Tencent Cloud, and Google Cloud.
  * **Operation Limitations**: Under an external Schema, operations such as table creation and deletion are not supported as they are directly mapped. Additionally, tables under an external Schema only support read-only operations and do not allow data manipulation language (DML) operations such as insert, update, truncate, or delete. Users can perform query and join operations and can create views based on these tables.
  * **Deletion Behavior Explanation**: Deleting an external Schema does not delete the mapped objects (such as Hive Databases and their included tables) in the source system.

## Usage Example

#### **1. Connecting to Alibaba Cloud OSS**

To connect to Alibaba Cloud OSS, you need the following parameters. Refer to the [Alibaba Cloud OSS documentation](https://help.aliyun.com/zh/oss/developer-reference/configure-ossutil) for details:

First, create a storage connection to link to the external object storage service.

```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss
    type OSS
    ACCESS_ID='LTAIxxxxxxxxxxxx'
    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'
    ENDPOINT='xxx';
```

Next, create a catalog connection pointing to the Hive metadata storage service (Hive Metastore).

```SQL
CREATE CATALOG CONNECTION if not exists connection_name
    type hms
    hive_metastore_uris='metastore_uris'
    storage_connection='storage_connection';
```

```SQL
CREATE EXTERNAL SCHEMA if not exists schema_name
    CONNECTION connection_name
    options(SCHEMA='hive_database_name');
```

  * `connection`: A required parameter specifying the name of the catalog connection.
  * `SCHEMA`: An optional parameter used to map the Hive database name. If not specified, Lakehouse will automatically map the created `schema_name` to the Hive database using the same name by default.