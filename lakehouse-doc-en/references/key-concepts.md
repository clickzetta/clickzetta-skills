# Singdata Lakehouse Key Concepts

This chapter details the key concepts of Singdata Lakehouse, helping you understand the product's design philosophy and the relationships between components.

## Account

An account is the contractual entity between your company and Singdata, equivalent to an enterprise master account.

An account is the business relationship entity of Singdata Lakehouse, representing the organization or individual that has established a partnership with Singdata.

**Core Responsibilities**:
- The account is responsible for recharging, issuing bills, paying fees, and ordering/modifying Singdata products
- All service instances and their resource objects belong to a specific account
- The account is the highest level of permissions and billing management

**Account URL**: Each account has a unique access URL in the format `<account_name>.accounts.clickzetta.com`.

## User

A user is a specific operator under an account, similar to an employee account in an enterprise IT system, with each person having their own permission scope.

A user is a specific operator under an account. An account can create multiple users, and different users are assigned access to data and resources through permission controls.

**Relationship with Account**:
- Users belong to an account and cannot cross accounts
- Users need to join a workspace to use its objects
- Permissions can be granted to users or roles

## Lakehouse Instance

A lakehouse instance is a complete Lakehouse environment you deploy in a cloud region, similar to provisioning an independent data warehouse instance on Alibaba Cloud.

A lakehouse instance is the carrier of Singdata Lakehouse product services, containing all resources including compute, storage, and metadata.

**Key Features**:
- One account can create one or more lakehouse instances
- Instances have a regional attribute; compute, data, and other service resources reside within the region of the cloud service provider
- Different instances are isolated from each other by default
- Within an instance, unified metadata management governs data objects, compute resources, and job tasks

## Workspace

A workspace is a team's independent development environment, similar to different projects in a Git repository — different teams operate within their own workspaces without interfering with each other.

A workspace is a logical container for organizing Lakehouse resource objects (data objects, compute resources, users, etc.) and provides supporting data development capabilities.

**Core Capabilities**:
- Organize and manage data objects such as Schemas, tables, and views
- Provide tools for data integration, development scheduling, and operations monitoring
- Workspaces are isolated from each other by default; users must join a workspace to use its objects
- Cross-workspace authorization enables sharing of objects between different workspaces within the same instance

**Relationship with Workflow**: One instance can have multiple workspaces, each with an independent development environment and scheduling system.

## Workspace and Catalog Relationship

This is one of the most commonly confused concepts in Lakehouse.

**Workspace** is a native Lakehouse concept with two layers of meaning:
- **Platform layer**: The top-level namespace for data objects, equivalent to a Database in traditional databases (three-level structure: `workspace.schema.table`)
- **Studio layer**: An isolated unit for the data development environment, containing independent users, roles, VClusters, Studio task scheduling, and more

**Catalog** is a more general term introduced with federation queries to uniformly describe "top-level namespaces":

| Category | Description | How to create |
|---|---|---|
| `MANAGED` | Native Workspace with both platform-layer and Studio-layer capabilities | Create a Workspace in the console |
| `EXTERNAL` | External Catalog mapping external data sources (Hive/Databricks/Iceberg, etc.) | `CREATE EXTERNAL CATALOG` |
| `SHARED` | System-shared datasets (e.g., TPC-H, TPC-DS benchmark data) | System built-in |

- `SHOW WORKSPACES` and `SHOW CATALOGS` return the same results
- `current_workspace()` and `current_catalog()` return the same value
- Three-level naming supports both `workspace.schema.table` and `catalog.schema.table`

**Non-MANAGED types do not support write operations**: EXTERNAL, SHARED, and the system built-in `sys` namespace are all read-only. Attempting to create tables or execute DML in them will raise permission errors:
- SHARED: `NoPermission: Only read actions are allowed on shared object`
- SYS: `NoPermission: Workspace sys is readonly, AT_CREATE_TABLE operation is not allowed`
- EXTERNAL: Depends on the external data source type; typically write operations are also not supported

These three namespace types can be queried via three-level naming (`catalog.schema.table`), but cannot be used as write targets and have no Studio layer (no VCluster, user management, or task scheduling).

## Workspace and Database Relationship

For users familiar with traditional databases (PostgreSQL, MySQL, Snowflake, etc.), Workspace is the **Database** in ClickZetta:

| Traditional Database | ClickZetta Lakehouse |
|---|---|
| Database | Workspace |
| Schema | Schema |
| Table | Table |
| `database.schema.table` | `workspace.schema.table` |

The two are fully equivalent at the SQL level with the same three-level naming structure. The main difference is that Workspace, in addition to serving as a namespace like a Database, also includes the Studio development environment (VCluster, user management, task scheduling, etc.) — making it a heavier concept.

**Impact on dbt users**: dbt's `database` config maps to the ClickZetta workspace, `{{ this }}` renders as `workspace.schema.table`, and `target.database` returns the workspace name — consistent with other dbt adapters.

## Virtual Cluster (VCluster)

A Virtual Cluster is compute resource started on demand, stopped when done, and incurs no cost when idle — similar to hailing a ride, you call for it when needed and leave when finished.

A Virtual Cluster consists of multi-instance virtual compute clusters and the compute services running within them, providing CPU, memory, and temporary storage resources for jobs.

**Three Types**:

| Type | Use Case | Characteristics |
|---|---|---|
| **General (GP VC / GENERAL)** | Offline ETL, data development | Jobs share resources, fair scheduling |
| **Analytics (AP VC / ANALYTICS)** | Online queries, high-concurrency analysis | Multiple compute instances, automatic scaling |
| **Sync (Integration VC / SYNC)** | Data sync jobs | Optimized specifically for data synchronization |

**Billing Method**: Charged by CRU (Compute Resource Unit) × hours; different cluster types have different CRU step sizes.

**Elasticity**:
- Analytics clusters support automatic scaling, adjusting compute instances based on concurrency
- All clusters support automatic suspension and resumption, pausing automatically when idle to save costs

## Schema

A Schema is a namespace within a workspace used to organize tables, views, dynamic tables, and other objects — similar to folders in a file system.

A Schema is a namespace for a group of data objects within a workspace, including tables, views, dynamic tables, materialized views, and more.

**Relationship with Workspace**:
- One workspace can contain multiple Schemas
- A Schema is the direct container for objects such as tables
- Full three-level naming: `workspace.schema.table` (similar to `database.schema.table` in PostgreSQL/Snowflake)

## Table

A table is the basic unit for storing structured data in the Lakehouse, consistent with the concept of tables in relational databases.

A table is the most fundamental data storage object in the Lakehouse, storing data in formatted two-dimensional form.

**Storage Format**: Uses Parquet format by default, supporting efficient compression and columnar queries.

**Table Types**: The Lakehouse provides multiple table types; see [Concept Index](concepts.md#table-type-comparison) for details.

## Dynamic Table

A dynamic table is a data table that updates automatically. You simply define the processing logic, and it will automatically compute and store the latest data at the configured frequency, eliminating the hassle of manually running ETL.

A dynamic table is a data object that refreshes automatically and incrementally based on a query definition. At creation, the data processing logic is defined through a SQL query; during refresh, it automatically retrieves incremental data from the source table and processes it using incremental algorithms.

**Core Advantages**:
- **Incremental Computation**: Only processes data that has changed since the last refresh, significantly reducing compute resource consumption
- **Automatic Refresh**: Configurable refresh interval (minutes/hours/days), no manual triggering required
- **Version Management**: Supports Time Travel for querying historical versions and UNDROP for recovering accidental deletions

**Use Cases**:
- DWD/DWS/ADS layer data processing
- Metric aggregation and report wide tables
- Replacing traditional periodic full-refresh ETL tasks

**Difference from Materialized Views**:
- Dynamic tables focus on data processing and do not rely on the query optimizer's query rewriting
- Materialized views focus on query acceleration; the optimizer automatically identifies and uses pre-stored results for query rewriting

## Materialized View

A materialized view stores pre-computed results of commonly used queries. Queries read cached results directly for faster performance — the optimizer automatically decides when to use it.

A materialized view is a special view that pre-computes and stores query results. Unlike regular views, materialized views physically exist in the Lakehouse and consume storage resources.

**Core Features**:
- The query optimizer automatically identifies and uses materialized views for query rewriting
- Uses periodic refresh mechanisms to keep data up to date
- Suitable for scenarios requiring pre-computed and reusable query results

## View

A view is a saved query shortcut that does not store data itself. It executes the underlying SQL in real-time for each query, similar to formula references in Excel.

A view is a virtual table that does not store actual data, only saving the query definition. The underlying SQL is executed dynamically at query time.

**Use Cases**:
- Simplifying complex queries and providing a logical abstraction layer
- Scenarios with low query complexity that do not involve heavy data processing

## Table Stream

A Table Stream is the Lakehouse's Change Data Capture (CDC) mechanism, equivalent to installing a "change listener" on a table that records every data insert, update, and delete for downstream tasks to consume.

A Table Stream is the Lakehouse's Change Data Capture (CDC) mechanism used to capture change data from table objects.

**How It Works**:
- A Table Stream **does not store actual data**; it only records and maintains the data version offset of the source table
- When queried, it returns all change records from the initial offset to the current latest version
- When consumed through DML operations (INSERT/DELETE/UPDATE/MERGE), the offset updates automatically

**Two Types**:

| Type | Tracking Scope | Use Case |
|---|---|---|
| **STANDARD** | All DML changes (INSERT, UPDATE, DELETE) | ETL scenarios requiring complete change data capture |
| **APPEND_ONLY** | INSERT operations only | Log/event scenarios with append-only data |

**Relationship with Dynamic Tables**:
- Table Stream is the underlying CDC mechanism responsible for capturing changes
- Dynamic tables are advanced data processing features that perform data transformation based on incremental computation
- The two can work together: Table Stream captures changes → Dynamic Table performs transformation and aggregation

**Typical Operations**:
```sql
-- Create a Table Stream
CREATE TABLE STREAM my_stream ON TABLE source_table
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'STANDARD');

-- Consume Stream data (offset updates automatically)
INSERT INTO target_table SELECT * FROM my_stream;
```

## Pipe

A Pipe is a continuously running data ingestion pipeline, similar to a water pipe — whenever new data arrives at the source, it automatically flows into the Lakehouse without manual triggering.

A Pipe is the Lakehouse's continuous data ingestion pipeline object, used to continuously ingest data from Kafka or object storage (OSS/S3/COS) into tables.

**Core Features**:
- A Pipe is a **SQL object** created and managed through DDL
- After creation it runs continuously, automatically reading data from the source and writing to the target table
- No need to configure Cron scheduling; the Pipe itself is a continuously running streaming task

**Difference from Studio Sync Tasks**:

| Dimension | Pipe | Studio Sync Task |
|---|---|---|
| Creation Method | SQL DDL | Studio visual interface |
| Management Method | SQL commands | Studio interface + cz-cli |
| Data Sources | Kafka, object storage | Relational databases, Kafka, object storage |
| Use Case | Users familiar with SQL | Users preferring visual configuration |

**Two Types**:
- **Kafka Pipe**: Continuously consumes data from Kafka topics and writes to Lakehouse tables
- **Object Storage Pipe**: Continuously scans new files from OSS/S3/COS and ingests them

## Volume

A Volume is the Lakehouse's entry point for accessing files, equivalent to "mounting" object storage such as OSS/S3/COS so that you can read and write files within it directly using SQL.

A Volume is the Lakehouse's object storage mount point, used to access files in external storage such as OSS/COS/S3, or to serve as the Lakehouse's built-in file storage space.

**Four Types**:

| Type | Description | Creation Method | Storage Location |
|---|---|---|---|
| **External Volume** | Mounts user-owned object storage (OSS/COS/S3), data stays in place | `CREATE EXTERNAL VOLUME` | User-owned cloud storage |
| **Managed Volume** | Lakehouse-managed internal storage, platform handles storage management | `CREATE VOLUME` | Lakehouse internal storage |
| **User Volume** | Per-user file space for uploading temporary files, import/export | Created automatically by the system | Lakehouse internal storage |
| **Table Volume** | Per-table file space storing the table's data files | Created automatically (one per table) | Lakehouse internal storage |

**Relationship with Tables**:
- Volume manages **files**; Table manages **structured data**
- Volume is the channel for data entering the lake; Table is the target of data processing
- Use `COPY INTO` to import file data from Volume into Table

**Typical Operations**:
```sql
-- View file list in an External/Managed Volume
SELECT * FROM DIRECTORY(VOLUME schema_name.vol_name);

-- Import data from Volume into a table
COPY INTO orders FROM VOLUME my_schema.my_vol USING CSV OPTIONS('header'='true');

-- Upload a local file to User Volume
PUT 'file:///local/data.csv' TO USER VOLUME;

-- View User Volume file list
SHOW USER VOLUME DIRECTORY;

-- Import data from User Volume into a table
COPY INTO orders FROM USER VOLUME USING CSV OPTIONS('header'='true') FILES('data.csv');
```

## Time Travel

Time Travel lets you look back at historical data like a "time machine" — you can query data snapshots at any past point, recover accidentally dropped tables, or roll back mistakenly modified data.

Time Travel is the Lakehouse's historical data access feature that allows users to access data at any point in time within a defined time range.

**Core Mechanism**:
- Based on MVCC (Multi-Version Concurrency Control), each data change generates a new version
- Retains 1 day of historical data by default, configurable from 0 to 90 days
- Supports querying historical versions, recovering accidentally dropped tables (UNDROP), and rolling back data (RESTORE)

**Three Capabilities**:

| Capability | Command | Use Case |
|---|---|---|
| Historical Query | `SELECT * FROM table TIMESTAMP AS OF '...'` | Compare data changes at different points in time |
| Recover Dropped Table | `UNDROP TABLE table_name` | Recover a table after it has been DROPped |
| Rollback Data | `RESTORE TABLE table_name TO TIMESTAMP AS OF '...'` | Rollback after data is mistakenly modified/deleted |

**Typical Operations**:
```sql
-- Query data at a specific point in time (TIMESTAMP AS OF only accepts literals, not expressions)
SELECT * FROM orders TIMESTAMP AS OF '2024-01-15 09:00:00';

-- Recover a dropped table
UNDROP TABLE orders;

-- Rollback a table to a specified point in time
RESTORE TABLE orders TO TIMESTAMP AS OF '2024-01-15 10:00:00';
```

## Data Lifecycle (TTL)

Data Lifecycle is a mechanism that sets an "expiration date" on data. Data that has not been updated beyond the configured time is automatically cleaned up, helping control storage costs.

Data Lifecycle is the Lakehouse's automatic data cleanup mechanism; expired data that has not been updated is automatically reclaimed.

**Difference from Time Travel**:
- Time Travel: Retains historical versions for querying and recovery
- Data Lifecycle: Automatically cleans up expired data for storage cost control

## External Catalog

An External Catalog allows you to query tables in external systems without moving the data, similar to installing a "read-only view into remote databases" within the Lakehouse.

An External Catalog is the Lakehouse's federated query feature for accessing data in external data sources (Hive, Databricks, Snowflake Iceberg, etc.) without needing to copy the data.

**Core Features**:
- **Read-Only Access**: INSERT/UPDATE/DELETE operations are not supported
- **No Data Copy**: Data remains in the external system; the Lakehouse only reads metadata and data files
- **Unified Entry Point**: Query external data through standard SQL just like querying local tables

**Supported Data Sources**:

| Data Source | Connection Method | Description |
|---|---|---|
| **Apache Hive** | Hive Metastore URIs | Access Hive tables through Hive Metastore |
| **Databricks Unity Catalog** | Databricks API | Access tables in Databricks |
| **Iceberg REST Catalog** | Iceberg REST API | Access any data catalog compatible with the Iceberg REST protocol |
| **Snowflake Open Catalog** | Iceberg REST API + OAuth | Snowflake's managed catalog service based on the Iceberg REST protocol |

**Typical Operations**:
```sql
-- Query a table in an external Catalog
SELECT * FROM ext_catalog.ext_schema.ext_table;

-- Join query between local and external tables
SELECT l.order_id, e.customer_name
FROM local_orders l
JOIN ext_catalog.sales.customers e ON l.customer_id = e.id;
```

## Data Share

Data Share lets you "grant" tables or views to other lakehouse instances. The recipient reads your original data in real time without copying, similar to a read-only link for a shared document.

Data Share is the Lakehouse's cross-instance data sharing feature that allows real-time sharing of tables or views with other lakehouse instances without copying data.

**Core Features**:
- **No Copy**: The consumer reads the provider's original data directly when querying
- **Real-Time Sync**: Changes on the provider side are immediately visible to the consumer
- **Read-Only Access**: Consumers can only query; they cannot modify, delete, or re-share

**Operation Flow**:
```
Provider: CREATE SHARE → GRANT TO SHARE → ALTER SHARE ADD INSTANCE
                                                    ↓
Consumer: SHOW SHARES → DESC SHARE → CREATE SCHEMA FROM SHARE → SELECT query
```

**Typical Operations**:
```sql
-- Provider: Create Share and grant privileges
CREATE SHARE my_share;
GRANT SELECT, READ METADATA ON TABLE public.orders TO SHARE my_share;
ALTER SHARE my_share ADD INSTANCE consumer_instance;

-- Consumer: Create Schema and query
CREATE SCHEMA shared_data FROM SHARE provider_instance.my_share.public;
SELECT * FROM shared_data.orders;
```

## Lakehouse Studio

Lakehouse Studio is the web-based operational interface of Singdata Lakehouse, equivalent to the product's "cockpit" — data integration, development scheduling, and operations monitoring are all completed here, with no command line needed.

Lakehouse Studio is the web-based graphical interface provided by Singdata Lakehouse. It is a **unified data development and governance platform** that integrates data integration, development scheduling, operations monitoring, data catalog, and other capabilities.

**Main Modules**:
- **Data Sync**: Configure offline/real-time data sync tasks
- **Task Development**: Web IDE for SQL/Python/Shell task development
- **Task Scheduling**: Configure Cron expressions and task dependencies
- **Operations Monitoring**: View task execution status, logs, and alerts
- **Data Catalog**: Global search and filter for table metadata
- **Data Quality**: Configure data quality check rules
- **Compute Management**: Manage compute clusters
- **Agent**: AI Agent integration, supporting conversational data analysis and MCP Server management

---

See the [Product Object Model](object_model_design.md) for detailed product concepts.
