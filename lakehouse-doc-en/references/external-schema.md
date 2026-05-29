# EXTERNAL SCHEMA
> **This feature is currently in Public Preview.**
## Introduction

External Schema (EXTERNAL SCHEMA) is a Lakehouse feature for querying external data sources. With EXTERNAL SCHEMA, you can access external metadata services (such as HMS) and batch map external tables without importing data into Lakehouse. For example, by establishing a mapping with a Hive Database and using the Hive Metadata Service (HMS) interface, an External Schema can directly obtain Hive metadata without actually creating table structures in Lakehouse.

Using EXTERNAL SCHEMA provides the following benefits:

1. **Direct Querying**: Through EXTERNAL SCHEMA, users can directly query data in external databases (such as Apache Hive) without complex data import processes. Since Lakehouse offers better performance, it can also accelerate queries for third-party engines.
2. **Data Transformation and Import**: Combined with `INSERT INTO ..SELECT` statements, users can perform Extract, Transform, Load (ETL) operations, writing query results directly into Lakehouse tables.
3. **Real-Time Joins**: EXTERNAL SCHEMA supports joining Lakehouse tables with data from external data sources in real time, meaning users can query data as changes occur rather than waiting for data reloads.
4. **Deletion Behavior**: Deleting an External Schema does not delete the corresponding Database in Hive, because the External Schema only establishes a mapping relationship with the Hive Database; the deletion only removes the External Schema metadata in Lakehouse.

This design provides great flexibility and convenience, as it reduces the need for data migration and allows users to query and analyze data stored in external data sources in real time.

## Relationship Between External Catalog and External Schema

External Catalog and External Schema form a two-layer mapping structure. External Catalog is the top-level container, directly mapping to an external data system; External Schema is an intermediate-layer container that provides fine-grained data organization. By associating an External Schema with an internal Catalog, you can query external and internal tables in the same workspace using the simple `schema.table` format.

## Supported Scope

* Hive on OSS (Alibaba Cloud Object Storage Service)
* Hive on COS (Tencent Cloud Object Storage Service)
* Hive on GCS (Google Cloud Object Storage Service)
* Hive on HDFS (Preview, contact Lakehouse support)
* Databricks
* Both reads and writes are supported. Write formats supported: Parquet, ORC, Text file formats.

## External Schema vs. External Table

* **External Schema**: Interacts directly with Hive Metadata Service (HMS), obtaining Hive metadata via the HMS interface.
* **External Table**: Users can define their own table creation with custom column definitions and table names.
* **External Schema Limitations**: Because it directly maps HMS, you cannot directly create, drop, or rename tables under an External Schema.
* **External Table Advantages**: Supports operations such as renaming and modifying comments, since they are created under an internal Schema.

## External Schema Billing

* **Storage Costs**: External tables incur no storage costs, as data is not stored in Lakehouse.
* **Compute Costs**: Using external tables for computation consumes compute resources and therefore incurs compute costs.

## External Schema Privileges

* **Create External Schema Privilege**: Requires the privilege to create a schema (create schema).
* **Drop External Schema Privilege**: Requires the drop privilege.
* **Table Privileges Under External Schema**: Individual table-level grants are not currently supported; only ALL TABLES privilege is available.

## Management

Singdata Lakehouse provides commands to create and delete EXTERNAL SCHEMA, allowing users to manage access and configuration of these external data sources as needed.

- **Creating EXTERNAL SCHEMA**: Users can create a new EXTERNAL SCHEMA using the `CREATE EXTERNAL SCHEMA` command to begin interacting with external databases. Specific syntax and parameter settings can be found in the [Creating EXTERNAL SCHEMA](create-external-schema.md) documentation.
- **Deleting EXTERNAL SCHEMA**: If a particular EXTERNAL SCHEMA is no longer needed, or if users wish to remove access to an external database, they can use the `DROP SCHEMA` command to delete it. Related procedures and notes are detailed in the [Deleting EXTERNAL SCHEMA](drop-schema.md) documentation.

## Privilege Notes

* **Create External Schema Privilege**: Requires the privilege to create a schema (create schema).
* **Drop External Schema Privilege**: Requires the drop privilege.
* **Table Privileges Under External Schema**: Individual table-level grants are not currently supported; only ALL TABLES privilege is available.

## Constraints and Limitations

**Supported Data Sources**: Currently, EXTERNAL SCHEMA primarily supports access to Hive Metastore metadata services, with data needing to be stored in HDFS or Alibaba Cloud, Tencent Cloud, or Google Cloud object storage services.

**Operation Limitations**: Under an External Schema, operations such as creating or dropping tables are not supported since they are directly mapped. Additionally, tables under an External Schema only support read operations; Data Manipulation Language (DML) operations such as INSERT, UPDATE, TRUNCATE, or DELETE are not allowed. Users can perform queries and joins, and can create views based on these tables.

**Deletion Behavior**: Deleting an External Schema does not delete the mapped objects in the source system (such as the Hive Database and the tables it contains).

## Examples

#### **1. Connecting to Alibaba Cloud OSS**

To connect to Alibaba Cloud OSS, you need the following parameters. Refer to the *[Alibaba Cloud OSS Documentation](https://help.aliyun.com/zh/oss/developer-reference/configure-ossutil)* for details:

First, create a storage connection to connect to the external object storage service.

```SQL
CREATE STORAGE CONNECTION if not exists catalog_storage_oss
    type OSS
    ACCESS_ID='LTAIxxxxxxxxxxxx'
    ACCESS_KEY='T8Gexxxxxxmtxxxxxx'
    ENDPOINT='xxx';
```

Next, create a catalog connection pointing to the Hive Metadata Service (Hive Metastore).

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

* `connection`: Required parameter specifying the catalog connection name.
* `SCHEMA`: Optional parameter for mapping the Hive database name. If not specified, Lakehouse defaults to mapping the created `schema_name` to the database in Hive automatically.
