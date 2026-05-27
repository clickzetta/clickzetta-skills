# Table

In Singdata Lakehouse, a Table is the basic unit for storing data and is the core structure for organizing data. Lakehouse tables use columnar storage, which is highly efficient for processing analytical queries because it allows queries to read only the required column data instead of entire rows. This storage structure is particularly suitable for data warehousing and big data analytics scenarios, significantly improving data processing speed.

## Table Types

Lakehouse provides multiple table types for different scenarios:

| Table Type | Description | Use Case |
|---|---|---|
| **Regular Table (Table)** | Structured two-dimensional data, manually INSERT/UPDATE/DELETE | Raw data storage, ODS layer |
| **Dynamic Table** | Data objects that auto-incrementally refresh based on query definitions | DWD/DWS/ADS layers, metric aggregation |
| **Materialized View** | Special views that pre-compute and store query results | Pre-computed query results, query rewriting |
| **View** | Virtual table, no data stored, dynamically computed at query time | Simplifying complex queries, logical abstraction |
| **External Table** | Data stored in external systems; Lakehouse manages only metadata | Federated queries, data lake access |

## Storage Format

Lakehouse tables use the **Parquet** columnar storage format by default, offering the following advantages:

- **Efficient compression**: Columnar storage keeps same-type data contiguous, achieving high compression ratios
- **Query optimization**: Only reads the columns required by the query, reducing I/O
- **Schema evolution**: Supports adding columns, changing column types, and other schema changes

## Table Constraints

Table constraints ensure the integrity and accuracy of data in the table. Lakehouse supports the following constraints:

### NOT NULL

The **NOT NULL** constraint ensures that values in a column cannot be NULL. This is set at table creation time, and once set, the constraint cannot be removed to ensure the column always has valid data.

### PRIMARY KEY

The **PRIMARY KEY** is used to ensure the uniqueness of each record in the table. In big data scenarios, checking every key one by one to guarantee data uniqueness is impractical and inefficient due to the typically massive data volumes, so using primary key constraints is generally not recommended in big data environments. However, Lakehouse still provides primary key support to meet data integrity requirements in specific scenarios. In the Lakehouse architecture, when a table with a defined primary key receives real-time data writes, the system automatically deduplicates based on the primary key values, which is especially important for Change Data Capture (CDC) scenarios. For example, you can synchronize MySQL binlog logs to Lakehouse in real time to ensure data consistency. After setting the primary key, you need to process data through the [Real-time Data Interface](java_reference/realtime-upload.md). During CDC real-time writes, the system automatically deduplicates based on the primary key to maintain data accuracy and integrity.

#### Lakehouse Primary Key Support and Default Behavior

Lakehouse supports two ways of directly specifying a primary key, and by default, its behavior is set to `ENABLE VALIDATE RELY`. This means that when you specify a primary key at table creation without explicitly specifying other behaviors, the system automatically enables primary key validation and dependency.

Under this default behavior, whether for real-time writes or SQL-based data writes, the system performs deduplication based on the defined primary key. If an attempt is made to insert a record with a duplicate primary key value, the system will reject the insert operation to ensure primary key uniqueness. For example:

```sql
create table test_primary(id int primary key,name string);
desc extended test_primary;
insert into test_primary values(1,"1");
insert into test_primary values(2,"1");
-- Insert succeeds because primary key values 1 and 2 are not duplicates
insert into test_primary values(1,"1");
-- Insert fails because primary key value 1 already exists
select * from test_primary;
```

As shown above, under the default `ENABLE VALIDATE RELY` mode, the system strictly enforces primary key uniqueness, performing primary key conflict checks for both single-record and batch inserts.

#### Custom Primary Key Behavior

If, based on actual business needs, you want deduplication to be performed only by the real-time write mechanism and not by SQL writes when inserting data, you can achieve this by setting the primary key behavior to `disable NOVALIDATE RELY`. Here is an example:

```sql
create table test_primary_di(id int primary key disable NOVALIDATE RELY ,name string);
insert into test_primary_di values(1,"1");
insert into test_primary_di values(2,"1");
-- Insert succeeds, primary key check performed as expected
insert into test_primary_di values(1,"1");
-- Insert succeeds because in disable NOVALIDATE RELY mode, SQL writes do not perform primary key deduplication
```

Note that in `disable NOVALIDATE RELY` mode, although real-time writes still deduplicate based on the primary key, SQL-based write operations are not subject to primary key uniqueness constraints, which may lead to duplicate primary keys in the data. Therefore, when choosing this mode, you need to carefully consider and manage the source and method of data writes to avoid potential data quality issues.

## Related Documents

- [Create Table](create-table-ddl.md)
- [ALTER TABLE](alter-table.md)
- [DROP TABLE](drop-table.md)
- [Dynamic Table](dynamic-table-introduce.md)
- [Materialized View](MATERIALIZEDVIEW.md)
- [View](VIEW.md)
- [External Table](external-table-guide.md)
