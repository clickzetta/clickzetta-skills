# Data Sharing

Data Sharing lets data in Lakehouse be **granted to other instances for access without any copying** — the provider simply creates a Share object and grants access, and the consumer can immediately query the original data in real time. The data never leaves the provider's account.

Think of it like giving someone read-only access to your bookshelf rather than lending them a book. They can come and read whenever they want; the book stays with you, and you can revoke the key at any time. This is different from ETL sync: sync copies a book to the other party and both copies evolve independently; sharing means both parties use the same book, so any change the provider makes is immediately visible to the consumer.

![](/.topwrite/assets/17-data-sharing.svg)

## Comparison with Other Data Exchange Methods

| Method | Data copied? | Latency | Consumer storage cost | Use cases |
|--------|-------------|---------|----------------------|-----------|
| **Data Sharing (Share)** | No | Real-time | Zero | Real-time cross-team / cross-company collaboration |
| Data Sync (ETL) | Yes | Delayed | Full storage consumed | Cross-cloud scenarios, independent processing needed |
| File export | Yes | One-time | File storage consumed | Offline data exchange |

> ⚠️ **Key limitation**: Data sharing is only supported between instances **within the same cloud provider and service region**. Cross-cloud or cross-region sharing is not supported (for example, an Alibaba Cloud Shanghai instance cannot share data with a Tencent Cloud instance).

## Core Mechanism

Data sharing is implemented through **metadata authorization** — no data is moved:

```
Provider Instance                      Consumer Instance
┌────────────────────┐                 ┌────────────────────┐
│  source_table_a    │                 │                    │
│  source_table_b    │                 │  CREATE SCHEMA     │
│  source_view_c     │ ──── Share ──── │  FROM SHARE        │
│                    │  (authorized)   │                    │
│  data stays here   │                 │  read-only query   │
└────────────────────┘                 └────────────────────┘
```

- **Provider**: Creates a Share object, adds tables/views to the Share, and configures which consumer instances are allowed access.
- **Consumer**: Runs `CREATE SCHEMA FROM SHARE` to create a read-only Schema, then queries data through that Schema.
- **Real-time sync**: When the provider's data changes, the consumer sees the latest data immediately without any action on their end.
- **Independent compute**: Consumer queries consume the consumer's own VCluster resources, independent of the provider.

## Typical Use Cases

| Scenario | Approach |
|----------|----------|
| Cross-enterprise data collaboration | Company A shares sales data with partner B; B analyzes it in real time without building a sync pipeline. |
| Corporate master data distribution | Headquarters shares customer/product master data tables with business units; each unit gets real-time updates. |
| Data product delivery | A data service provider shares processed data products with customers, controlling access per customer. |

## Quick Example

```sql
-- ===== Provider operations =====
-- Create a Share object
CREATE SHARE sales_share;

-- Grant table access to the Share
GRANT SELECT ON TABLE orders TO SHARE sales_share;
GRANT SELECT ON TABLE products TO SHARE sales_share;

-- Add the consumer instance (use the consumer's service instance name)
ALTER SHARE sales_share ADD INSTANCE partner_instance;

-- View Share configuration
DESC SHARE sales_share;

-- ===== Consumer operations =====
-- View accessible Shares
SHOW SHARES;

-- Create a read-only Schema (mapped to the provider's Share)
CREATE SCHEMA shared_sales FROM SHARE provider_instance.sales_share;

-- Query the shared data directly
SELECT * FROM shared_sales.orders LIMIT 10;
```

## Common Issues

### Issue 1: Cross-cloud / cross-region sharing fails

**Problem**: Attempting to share data from an Alibaba Cloud Shanghai instance to a Tencent Cloud instance.

**Symptom**: `ADD INSTANCE` executes successfully, but the consumer cannot access the data.

**Solution**: Data sharing only works within the same cloud provider and service region. For cross-cloud scenarios, use a data sync job to write data into the consumer's instance instead.

### Issue 2: Sharing an entire table when only partial data is needed

**Problem**: You only want to share data for a specific merchant from the orders table, but you shared the entire table.

**Solution**: Create a View that filters the required data first, then add the View to the Share:
```sql
CREATE VIEW orders_for_partner AS
    SELECT * FROM orders WHERE merchant_id = 1001;
GRANT SELECT ON VIEW orders_for_partner TO SHARE sales_share;
```

### Issue 3: Consumer copies data for secondary use

**Problem**: The consumer uses `CREATE TABLE AS SELECT` to copy shared data out and re-shares it.

**Solution**: Share itself prevents secondary sharing, but it cannot stop the consumer from copying data. The provider needs to constrain the consumer's data usage at the agreement level and be selective about which tables to share.

## Cost Impact

### Storage Cost

- The consumer incurs no storage costs; data is stored at the provider.
- The Share object itself stores only metadata, at near-zero cost.

### Compute Cost

- Provider: The Share itself incurs no compute costs.
- Consumer: Querying shared data consumes **the consumer's own** VCluster CRU, not the provider's.

## Lifecycle Management

```
Create Share → Add data objects → Configure consumer instances → Consumer creates Schema → Query → Revoke access
     ↓               ↓                    ↓                             ↓                    ↓          ↓
  Empty Share   GRANT TO SHARE       ADD INSTANCE                 FROM SHARE           Read-only   REVOKE/DROP
```

```sql
-- Remove a data object from the Share
REVOKE SELECT ON TABLE orders FROM SHARE sales_share;

-- Remove a consumer instance
ALTER SHARE sales_share REMOVE INSTANCE partner_instance;

-- Drop the Share (the consumer's Schema will become invalid)
DROP SHARE sales_share;

-- Consumer: drop the read-only Schema
DROP SCHEMA shared_sales;
```

## In This Section

| Page | Description |
|------|-------------|
| [Data Sharing Object Model](om-data-sharing.md) | Complete Share object description, core principles, and permission controls |
| [Data Sharing Concepts](data-sharing-concept.md) | Provider/consumer roles, operation flow, and important notes |

## Related Documentation

| Document | Description |
|----------|-------------|
| [Cross-Account Data Sharing Guide](data_sharing_between_accounts_guide.md) | End-to-end operation flow |
| [Studio Data Sharing](quickstart_datashare_between_companies.md) | Configure sharing via the Web UI |
| [Data Sharing SQL Commands](share-ddl.md) | Complete syntax for CREATE/ALTER/DROP SHARE |
