# Singdata Lakehouse Primary Key Usage Guide

## Primary Key Constraint Overview

> **Important Differences from Traditional Databases**
>
> Singdata Lakehouse's Primary Key is a **declarative constraint**, and its behavior is fundamentally different from traditional databases such as MySQL and PostgreSQL:
>
> - **Uniqueness is not enforced by default (configurable)**: In `DISABLE NOVALIDATE RELY` mode, the system does not validate primary key uniqueness during writes, and duplicate primary key data can be written. Even in the default `ENABLE VALIDATE RELY` mode, uniqueness validation only applies to the SQL write path; the deduplication logic for real-time write (CDC) paths is handled by the write interface itself.
> - **Core purpose of the primary key**: (1) Declares data semantics to the query optimizer for query optimization; (2) Serves as the operation key for real-time writes (CDC UPSERT/DELETE), determining which record is updated or deleted.
> - **Application-level uniqueness**: If strict uniqueness is required for business purposes, it must be enforced by the application code and cannot rely solely on the Lakehouse primary key constraint.

**PRIMARY KEY** is used to declare the unique identifier column(s) for records in a table. In big data scenarios, validating uniqueness for every write operation is extremely expensive, so the Lakehouse primary key constraint provides flexible behavior configuration. In the Lakehouse architecture, when a table with a defined primary key undergoes real-time data writes, the system automatically deduplicates data based on the primary key value. This is especially important in Change Data Capture (CDC) scenarios. For example, you can synchronize MySQL database binlog logs to the Lakehouse in real-time to ensure data consistency. After setting up the primary key, you need to handle data through the [real-time data interface](java_reference/realtime-upload.md).

## Lakehouse Primary Key Support and Default Behavior

Lakehouse supports two ways to directly specify a primary key, and by default, its behavior is set to `ENABLE VALIDATE RELY`. This means that when you specify a primary key when creating a table and do not explicitly specify other behaviors, the system automatically enables primary key validation and dependency.

Under this default behavior, whether it is a real-time write operation or a data write via SQL, the system will deduplicate based on the defined primary key. If an attempt is made to insert a record with a duplicate primary key value, the system will reject the insert operation to ensure primary key uniqueness. For example:

```sql
create table test_primary(id int primary key,name string);
desc extended test_primary;
-- Insert succeeds because primary key values 1 and 2 are not duplicated
insert into test_primary values(1,"1");
insert into test_primary values(2,"1");
-- Insert fails because primary key value 1 already exists
insert into test_primary values(1,"1");
select * from test_primary;
```

From the above example, it can be seen that in the default `ENABLE VALIDATE RELY` mode, the system strictly enforces primary key uniqueness, and primary key conflict checks are performed for both single-record inserts and batch inserts.

## Customizing Primary Key Behavior

If, based on actual business requirements, you want primary key deduplication to be performed only by the real-time write mechanism and not by SQL writes, you can achieve this by setting the primary key behavior to `DISABLE NOVALIDATE RELY`. Here is a specific example:

```sql
create table test_primary_di(id int primary key DISABLE NOVALIDATE RELY ,name string);
insert into test_primary_di values(1,"1");
insert into test_primary_di values(2,"1");

insert into test_primary_di values(1,"1");
-- Insert succeeds because in DISABLE NOVALIDATE RELY mode, SQL writes do not deduplicate by primary key
```

Note that in `DISABLE NOVALIDATE RELY` mode, while real-time writes still deduplicate based on the primary key, SQL write operations are not constrained by primary key uniqueness, which may result in duplicate primary keys in the data. Therefore, when choosing this mode, you need to consider and manage the source and method of data writes to avoid potential data quality issues.

# Primary Key Table Creation Syntax

* Primary key table without partitioning or bucketing

```
CREATE TABLE pk_table
(
    id int,
    col string,
PRIMARY KEY (id)
);
CREATE TABLE pk_table
(
    id int PRIMARY KEY,
    col string
);
```

* Primary key table with bucketing.
  1. **When DISABLE NOVALIDATE RELY is not specified**:

     * Cluster Key must include the primary key column(s)
     * Sort Key must include the primary key
  2. **When DISABLE NOVALIDATE RELY is specified**:

     * Cluster Key does not need to include the primary key column(s)
     * Sort Key does not need to include the primary key

```
-- With DISABLE NOVALIDATE RELY
CREATE TABLE pk_table
(
    id int,
    col string,
    cluster_key string,
    PRIMARY key (id) DISABLE NOVALIDATE RELY
) 
CLUSTERED BY ( cluster_key)  INTO 16 BUCKETS;
-- Without DISABLE NOVALIDATE RELY
CREATE TABLE pk_table
(
    id int,
    col string,
    cluster_key string,
    PRIMARY key (id)
) 
CLUSTERED BY (id, cluster_key) SORTED BY (id) INTO 16 BUCKETS;


```

* Primary key table with partitioning.
  1. **When DISABLE NOVALIDATE RELY is not specified**:
     * Partition Key must include the primary key column(s)
  2. **When DISABLE NOVALIDATE RELY is specified**:
     * Partition Key does not need to include the primary key column(s)

```
-- With DISABLE NOVALIDATE RELY
CREATE TABLE pk_table
(
    id int,
    col string,
    pt string,
    PRIMARY key (id)DISABLE NOVALIDATE RELY
) PARTITIONED BY (pt);
-- Without DISABLE NOVALIDATE RELY
CREATE TABLE pk_table
(
    id int,
    col string,
    pt string,
    PRIMARY key (id, pt)
) PARTITIONED BY (pt);
```

# Usage Notes

**Type Selection Recommendations**

* Prefer numeric types (such as int/bigint)
* Avoid variable-length types (such as string/varchar) to reduce index space usage
* Do not use floating-point types (float/double)
* Do not use nested types

**Constraints**

* Primary key columns must be defined as NOT NULL
* Schema Evolution is not supported (primary key cannot be modified after table schema changes)

# Usage Examples

## Create Table

When creating a Lakehouse table, you can specify a primary key. Primary key tables support two write modes:

- **`ENABLE VALIDATE RELY` (default)**: Primary key uniqueness is enforced during SQL writes (INSERT), and inserts with duplicate primary keys are rejected.
- **`DISABLE NOVALIDATE RELY`**: Primary key uniqueness is not validated during SQL writes, allowing duplicate primary key writes; however, real-time write interface (CDC) writes still deduplicate by primary key.

> **Note**: Primary key tables in `DISABLE NOVALIDATE RELY` mode do not deduplicate through SQL, but still support SQL operations such as SELECT and INSERT; adding columns and modifying columns via SQL are not supported.

Below is an example of creating a table:

```sql
CREATE TABLE igs_test_upsert (
    id int PRIMARY KEY,
    event varchar(100),
    event_time STRING
);
```

## SDK Real-time Write Stream

### Create Real-time Write Stream

When creating a real-time write stream using the SDK, you need to specify the operation type (CDC) and related options. Below is an example of creating a real-time write stream:

```java
RowStream stream = client.newRealtimeStreamBuilder()
    .operate(RowStream.RealtimeOperate.CDC)
    .options(options)
    .schema(schema)
    .table(table)
    .build(); // Close the stream and release stream resources, must be called
stream.close();
```

### Specify Operation Type

Depending on requirements, different operation types can be specified:

* `Stream.Operator.UPSERT`: Insert or update a row. If the target row does not exist, insert it; if it already exists, update it.
* `Stream.Operator.DELETE_IGNORE`: Delete a row. If the target row does not exist, it is automatically ignored.

### Write Using the Native Java SDK

```java
Row row = stream.createRow(Stream.Operator.UPSERT); // Insert or update row
Row rowToDelete = stream.createRow(Stream.Operator.DELETE_IGNORE); // Delete row
```

## Write Using Lakehouse Real-time Sync

Refer to the documentation [Multi-table Real-time Sync](multitable_realtime_sync.md)

## Write Using FLINK CONNECTOR

Flink connector is built on the RealtimeStream SDK and used for real-time data synchronization. See [Flink Connector](flink-write-connector.md)

## References

[Java Real-time Programming Interface](java_reference/realtime-upload.md)

[Using Java SDK to Read Kafka Data for Real-time Upload](use-java-sdk-realtime-uploaddata.md)

[Singdata Lakehouse Multi-table Real-time Sync Implementing CDC](sql_table_stream_guide.md)
