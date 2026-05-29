# SQL Commands

Singdata Lakehouse supports standard ANSI SQL, extended with incremental computation (Dynamic Table), change data capture (Table Stream), vector search, federated queries, and more. This manual covers the complete syntax reference for all SQL statements.

Migrating from another platform? See [SQL Syntax Compatibility Reference](sql-reference.md) for compatibility notes with Spark SQL / Databricks.

---

## Query and Data Manipulation

| Page | Description |
|------|-------------|
| [Query Syntax](dql.md) | SELECT, JOIN, GROUP BY, window functions, Time Travel, EXPLAIN |
| [Data Write and Modification](dml.md) | INSERT, UPDATE, DELETE, MERGE INTO, TRUNCATE |
| [Data Import and Export](unload-data-summary.md) | COPY INTO for file import, COPY INTO VOLUME for data export |

## Table and View Objects

| Page | Description |
|------|-------------|
| [Tables](table.md) | Full DDL for regular tables: create, partition, bucket, primary key, ALTER, DROP |
| [Views](view.md) | Create, drop, and inspect views |
| [Materialized Views](materialized_ddl.md) | Create, refresh, alter, and drop materialized views |
| [Dynamic Tables](dynamic-table.md) | Core incremental computation object: create, refresh configuration, ALTER, refresh history |
| [Table Stream](table-stream-title.md) | CDC change capture object: create, inspect, drop |
| [External Tables](create-external-table.md) | Table definitions for external data sources such as Kafka external tables |
| [Indexes](SQL_Index_Guide.md) | Create and manage bloom filter indexes, inverted indexes, and vector indexes |

## Storage, Connections, and Ecosystem

| Page | Description |
|------|-------------|
| [Schema](schema.md) | Create, alter, switch, and drop schemas |
| [Volume](volume-introduction.md) | Create internal/external volumes, file operations (PUT/GET/LIST/REMOVE) |
| [Pipe](pipe-syntax.md) | Create and manage continuous data ingestion pipelines |
| [Connection](connection.md) | Create and manage API, storage, and catalog connection objects |
| [External Catalog & Schema](external_catalog_schema.md) | Federated queries: create and use external catalogs and external schemas |
| [Synonym](synonym.md) | Create and manage cross-schema object aliases |
| [Data Sharing (Share)](share-ddl.md) | Provider and consumer operations for cross-instance data sharing |

## Workspace and Access Management

| Page | Description |
|------|-------------|
| [Compute Cluster (VCluster)](compute-resource-ddl.md) | Create, start/stop, configure, and drop compute clusters |
| [Job Management](job-manage.md) | View, describe, and cancel running jobs |
| [User Management](authority-management.md) | Add, modify, and remove workspace users |
| [Roles and Privileges](role-privilege-manage.md) | Create roles and grant or revoke privileges |
| [User-Defined Functions](user-external-function.md) | Create and manage external functions and SQL functions |

## Basic Syntax

| Page | Description |
|------|-------------|
| [Basic Commands](sql-reference.md) | Object identifier conventions, comment syntax, session parameters, general DDL patterns |

---

## Quick Reference

**Object Naming Conventions**

Singdata Lakehouse uses a three-part naming scheme: `workspace_name.schema_name.object_name`. The first part can be omitted when you are in the current workspace; the first two parts can be omitted when you are in the current schema.

**General DDL Patterns**

Most objects support four operations: `CREATE [OR REPLACE] ... [IF NOT EXISTS]`, `DROP ... [IF EXISTS]`, `DESC[RIBE]`, and `SHOW ...S [LIKE 'pattern']`.

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Object Model](object_model_design.md) | Concepts, selection guidance, and how each object type works |
| [INFORMATION_SCHEMA](information_schema_guide.md) | Query metadata via SQL: table structure, job history, privilege assignments |
| [SQL Functions](functions.md) | Complete built-in function reference |
