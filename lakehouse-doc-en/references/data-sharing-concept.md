# Data Sharing

Data sharing is Singdata Lakehouse's cross-instance data sharing feature, allowing real-time sharing of tables or views with other service instances without copying data.

## What Is Data Sharing

Traditional data sharing requires copying data from one system to another, which not only consumes storage resources but also requires maintaining synchronization pipelines, resulting in data update latency.

Lakehouse data sharing uses a **zero-copy** approach: the data provider creates a Share object and authorizes it, and the consumer creates a read-only schema via `CREATE SCHEMA FROM SHARE` to directly access the original data. Data changes are reflected instantly without synchronization.

## Core Principles

```
Provider Instance                         Consumer Instance
+-------------------+                     +-------------------+
|  source_table_a   |                     |                   |
|  source_table_b   |                     |  CREATE           |
|  source_view_c    |--- Share -------->  |  SCHEMA           |
|                   |  (authorized)       |  FROM SHARE       |
|  Access Control   |                     |                   |
|                   |                     |  Read-only Query  |
+-------------------+                     +-------------------+
```

- **No data movement**: Consumers directly read the provider's original data when querying
- **Real-time synchronization**: Provider data changes are immediately visible to consumers
- **Controllable permissions**: Providers can add/remove shared data objects or consumer instances at any time
- **Read-only access**: Consumers can only query; they cannot modify, delete, or re-share

## Comparison with Data Synchronization

| Dimension | Data Sharing | Data Synchronization |
|---|---|---|
| Data Copy | No copying, direct access to original data | Data copied to consumer side |
| Real-time | Real-time, provider changes immediately visible | Has latency, depends on sync frequency |
| Storage Cost | Consumer does not incur storage cost | Consumer incurs additional storage cost |
| Compute Cost | Consumer uses own compute resources for queries | Sync task consumes compute resources |
| Data Modification | Consumer read-only, cannot modify | Consumer can modify copied data |
| Use Case | Cross-team/cross-company data collaboration | Data migration, independent analysis |

## Core Concepts

### Share Object

A Share is the carrier for data sharing, containing:
- **Data objects**: Tables or views to be shared (up to 1,000)
- **Recipient instances**: Consumer service instances authorized for access
- **Permissions**: `SELECT` (query data) and `READ METADATA` (view metadata)

### Provider

The data owner, responsible for:
1. Creating a Share object
2. Adding data objects to share into the Share
3. Configuring recipient instances (consumer's service instance name)

### Consumer

The data user, responsible for:
1. Viewing shared Share objects
2. Executing `CREATE SCHEMA FROM SHARE` to create a read-only schema
3. Querying the shared data

## Typical Application Scenarios

### Scenario 1: Cross-enterprise Data Collaboration

Company A needs to provide sales data to partner Company B for analysis:
- Company A creates a Share and adds the sales table to it
- Company A adds Company B's service instance as a recipient
- Company B creates a Schema from Share and can query Company A's sales data in real time
- No need to establish high-cost real-time synchronization pipelines

### Scenario 2: Cross-department Data Sharing Within an Enterprise

Corporate headquarters shares unified master data (customers, products, regions) with various business departments:
- Headquarters creates a Share containing all master data tables
- Adds each business department's service instance as a recipient
- Each department gets the latest master data in real time without maintaining it separately

### Scenario 3: Data Products as a Service

A data service provider offers processed data products to clients:
- Creates a Share containing data product tables
- Adds recipient instances by client
- Clients access the data product in real time; the provider can control the access scope at any time

## Notes

- **Share scope limit**: A Share can contain at most 1,000 tables or views
- **Partial data sharing**: To share a subset of data in a table, create a View first and then share the View
- **Secondary sharing prohibited**: Shared data cannot be re-shared to other instances
- **Data copy risk**: Consumers can copy data via `CREATE TABLE AS SELECT`; providers should carefully choose the sharing scope
- **Workspace isolation**: Share objects can only contain data objects from the same workspace

## Operation Flow

```
Provider: CREATE SHARE --> GRANT TO SHARE --> ALTER SHARE ADD INSTANCE
                                                        |
Consumer: SHOW SHARES --> DESC SHARE --> CREATE SCHEMA FROM SHARE --> SELECT
```

## Related Documentation

- [Data Sharing Complete Guide](data-sharing.md)
- [CREATE SHARE](create-share.md)
- [GRANT TO SHARE](grant-to-share.md)
- [SHOW SHARES](show-shares.md)
- [DESC SHARE](desc-share.md)
