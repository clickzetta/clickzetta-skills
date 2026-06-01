# EXTERNAL SCHEMA

【**Preview Release】This feature is currently in public preview**.

## Introduction

External Schema (EXTERNAL SCHEMA) is a feature provided by Lakehouse to query external data sources. With EXTERNAL SCHEMA, you can access external metadata services (such as HMS) and perform batch mapping of external tables without importing data into Lakehouse. For example, by mapping to a Hive Database and using the Hive Metadata Service (HMS) interface, the external schema can directly obtain Hive metadata information without actually creating table structures in Lakehouse.
Using EXTERNAL SCHEMA can bring the following benefits:

1. **Direct Query**: With EXTERNAL SCHEMA, users can directly query data in external databases (such as Apache Hive) without going through a complex data import process.
2. **Data Transformation and Import**: By using the `INSERT INTO ..SELECT` statement, users can perform data extraction, transformation, and loading (ETL), writing query results directly into Lakehouse tables.
3. **Real-time Join**: EXTERNAL SCHEMA supports real-time joins between Lakehouse tables and data in external data sources, meaning users can query data as it changes without waiting for data to be reloaded.
4. **Delete Behavior Explanation**: Deleting an external schema will not delete the Hive Database, as the external schema only establishes a mapping relationship with the Hive Database. The delete operation will only remove the external schema metadata information in Lakehouse.

This design provides great flexibility and convenience as it reduces the need for data migration and allows users to query and analyze data stored in external data sources in real-time.

## Supported Scope

* Hive on OSS (Alibaba Cloud Object Storage Service)
* Hive on COS (Tencent Cloud Object Storage Service)
* Hive on GCS (Google Cloud Object Storage Service)
* Hive on HDFS (Preview, please contact Lakehouse support)

## Difference Between External Schema and External Table

* **External Schema**: Directly interacts with the Hive Metadata Service (HMS) and obtains Hive metadata information through the HMS interface.
* **External Table**: Users can custom create tables, specifying column contents and table names.
* **External Schema Limitations**: Since it directly maps HMS, tables cannot be directly created, deleted, or renamed under an external schema.
* **External Table Advantages**: Supports operations such as renaming and modifying comments because they are created under an internal schema.

## External Schema Billing

* **Storage Fees**: External tables do not incur storage fees as data is not stored in Lakehouse.
* **Computation Fees**: Using external tables for computation will consume computational resources, thus incurring computation fees.

## External Schema Permissions

* **Create External Schema Permission**: Requires create schema permission.
* **Delete External Schema Permission**: Requires drop permission.
* **Permissions for Tables under External Schema**: Currently, individual tables cannot be authorized separately, only (ALL TABLES permission) is supported.

## Management

Singdata Lakehouse provides commands to create and delete EXTERNAL SCHEMA, allowing users to manage access permissions and configurations for these external data sources as needed.

* **Create EXTERNAL SCHEMA**: Users can create a new EXTERNAL SCHEMA using the `CREATE EXTERNAL SCHEMA` command to start interacting with external databases. Specific syntax and parameter settings can be found in the [Create EXTERNAL SCHEMA](createexternallschema.md) document.
* **Delete EXTERNAL SCHEMA**: If an EXTERNAL SCHEMA is no longer needed, or if users want to remove access to an external database, they can use the `DROP SCHEMA` command to delete it. Detailed operation steps and precautions are provided in the [Delete EXTERNAL SCHEMA](dropschema.md) document.

## Permission Explanation

* **Create External Schema Permission**: Requires create schema permission.
* **Delete External Schema Permission**: Requires drop permission.
* **Permissions for Tables under External Schema**: Currently, individual tables cannot be authorized separately, only (ALL TABLES permission) is supported.

## Constraints and Limitations

**Supported Data Sources**: Currently, EXTERNAL SCHEMA mainly supports accessing Hive Metastore metadata services, and data needs to be stored in HDFS or Alibaba Cloud, Tencent Cloud, Google Cloud object storage services.
**Operation Restrictions**: In the external Schema, operations such as creating or deleting tables are not supported because they are directly mapped. Additionally, tables under the external Schema only support read-only operations and do not allow data manipulation language (DML) operations such as insert, update, truncate, or delete. Users can perform query and join operations and create views based on these tables.
**Deletion Behavior Description**: Deleting an external Schema will not delete the mapped objects in the source system (such as Hive Database and its contained tables).

## Example

Connect to Alibaba Cloud OSS\*\*

To connect to Alibaba Cloud OSS, you need the following parameters, specifically refer to [Alibaba Cloud OSS Documentation](https://help.aliyun.com/zh/oss/developer-reference/configure-ossutil):

First, you need to create a storage connection to connect to the external object storage service.

```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss
    type OSS
    ACCESS_ID='LTAIxxxxxxxxxxxx'
    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'
    ENDPOINT='xxx';
```

Next, create a directory link pointing to the Hive Metastore service.

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

* `connection`: Required parameter, specifies the name of the directory connection.
* `SCHEMA`: Optional parameter, used to map the database name in Hive. If not specified, Lakehouse will default to using the created `schema_name` to automatically map to the database in Hive.

^
