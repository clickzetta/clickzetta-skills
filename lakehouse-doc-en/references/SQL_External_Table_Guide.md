# Lakehouse External Table Query Guide

## Overview

External Tables allow Lakehouse to directly query data stored in external systems (such as Delta Lake, Hudi, Kafka) without importing the data into Lakehouse. External tables manage only metadata; the actual data files remain in external storage. This guide is organized by business scenario to help you quickly master external table creation and query methods.

### Quick Navigation

* [Create Delta External Table](#create-delta-external-table) -- Directly query Delta Lake data
* [Create Hudi External Table](#create-hudi-external-table) -- Directly query Hudi data
* [Create Kafka External Table](#create-kafka-external-table) -- Real-time query of Kafka topics
* [Query External Tables](#query-external-tables) -- Use standard SQL to query external data
* [Drop External Tables](#drop-external-tables) -- Clean up external table metadata

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE EXTERNAL TABLE ... USING DELTA` | Create Delta external table | Query Delta Lake format data |
| `CREATE EXTERNAL TABLE ... USING HUDI` | Create Hudi external table | Query Apache Hudi format data |
| `CREATE EXTERNAL TABLE ... USING KAFKA` | Create Kafka external table | Real-time query of Kafka message streams |
| `SELECT * FROM external_table` | Query external table | Cross-system federated query |
| `DROP EXTERNAL TABLE` | Drop external table | Clean up metadata (does not affect external data) |

***

## Prerequisites

The following examples assume external data is already stored in object storage or a Kafka cluster:

```sql
-- Ensure the corresponding Storage Connection and Volume have been created
-- This guide uses Delta Lake as an example to demonstrate the external table creation workflow
```

***

## Create Delta External Table

Use `CREATE EXTERNAL TABLE` with `USING DELTA` to mount a Delta Lake table.

```sql
-- Create a Delta external table
CREATE EXTERNAL TABLE delta_sales
USING DELTA
LOCATION 'volume:my_ext_vol/sales_delta/';
```

**Parameter Descriptions**:
* `USING DELTA`: Specifies the external data format as Delta Lake.
* `LOCATION`: Points to the Volume path where the Delta files are stored.

> **Tip**: After creating the external table, Lakehouse automatically reads the schema from the Delta log, so you don't need to manually define columns.

***

## Create Hudi External Table

Use `USING HUDI` to mount an Apache Hudi table.

```sql
-- Create a Hudi external table
CREATE EXTERNAL TABLE hudi_users
USING HUDI
LOCATION 'volume:my_ext_vol/users_hudi/';
```

**Use Cases**:
* Real-time data lake architectures where data is continuously written to Hudi by Flink/Spark.
* External data sources that require Upsert and incremental query support.

***

## Create Kafka External Table

Use `USING KAFKA` to map a Kafka topic as an external table, supporting real-time SQL queries.

```sql
-- Create a Kafka external table
CREATE EXTERNAL TABLE kafka_events
USING KAFKA
PROPERTIES (
    'bootstrap.servers' = 'kafka-broker:9092',
    'subscribe' = 'app_events',
    'startingOffsets' = 'latest'
);
```

> **Note**: Kafka external tables only support `SELECT` queries, not `INSERT`/`UPDATE`.

***

## Query External Tables

Once created, external tables can be queried using standard SQL with exactly the same syntax as querying local tables.

```sql
-- Query a Delta external table
SELECT product, SUM(amount) as total_sales
FROM delta_sales
GROUP BY product;

-- Query a Kafka external table (real-time messages)
SELECT * FROM kafka_events LIMIT 10;
```

**Performance Notes**:
* When querying external tables, Lakehouse reads data files directly from external storage; network latency may be higher than with local tables.
* For frequently queried data on external tables, consider using `COPY INTO` to import it into local tables.

***

## Drop External Tables

Use `DROP EXTERNAL TABLE` to remove external table metadata.

```sql
-- Drop an external table
DROP EXTERNAL TABLE delta_sales;
```

> **Tip**: Dropping an external table only removes the metadata reference in Lakehouse; it does not delete the actual data files in external storage.

***

## Clean Up Test Data

After completing external table verification, it is recommended to clean up metadata:

```sql
-- Drop external tables
DROP EXTERNAL TABLE IF EXISTS delta_sales;
DROP EXTERNAL TABLE IF EXISTS hudi_users;
DROP EXTERNAL TABLE IF EXISTS kafka_events;
```

***

## Notes

1. **Read-only Access**: External tables only support queries, not write operations such as `INSERT`, `UPDATE`, `DELETE`.
2. **Schema Synchronization**: External table schemas are managed by external systems. If the external table structure changes, you need to execute `REFRESH` or recreate the external table.
3. **Network Connectivity**: Querying external tables requires network connectivity between Lakehouse and the external storage (OSS/S3/Kafka).
4. **Format Support**: Currently supports mainstream external formats such as Delta Lake, Hudi, and Kafka. For Parquet/ORC files, consider querying directly via Volume or importing with `COPY INTO`.
5. **Permission Requirements**: Creating external tables requires read permission on the underlying Volume or Kafka.

***

## Related Documentation

* [External Table Introduction](external-table-guide.md)
* [Delta Lake External Table](delta-lake.md)
* [Hudi External Table](external-hudi-table.md)
* [Kafka External Table](kafka-external-table.md)
