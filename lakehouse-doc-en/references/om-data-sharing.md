# Data Sharing

Data Sharing is Lakehouse's **zero-copy cross-account data authorization** feature. Within the same cloud and service region, it allows granting access to tables or views to other accounts. Data consumers can query in real time without copying data.

## Key Features

- **Zero copy**: Data never leaves the provider's account; consumers read it directly
- **Real-time sync**: After source data is updated, consumers immediately see the latest data
- **Pay-as-you-go**: Consumers use their own compute resources without paying for storage
- **Revocable**: Providers can revoke authorization at any time

## Comparison with Other Data Sharing Methods

| Method | Data Copy | Real-time | Applicable Scenarios |
|------|---------|--------|---------|
| **Data Sharing (Share)** | No copy | Real-time | Cross-account sharing within same cloud and region |
| ETL Sync | Copy required | Has latency | Cross-cloud, cross-system data migration |
| File Export | Copy required | One-time | Offline data exchange |

> Note: Data Sharing only supports sharing between accounts within the **same cloud and same service region**. Cross-cloud or cross-region sharing is not supported.

## Basic Workflow

```sql
-- Provider: create Share and grant access
CREATE SHARE my_share;
GRANT SELECT ON TABLE orders TO SHARE my_share;
ALTER SHARE my_share ADD INSTANCE <consumer_instance_name>;

-- Consumer: create Share reference and query
CREATE DATABASE FROM SHARE <provider_instance_name>.my_share;
SELECT * FROM shared_db.orders;
```

## Related Documents

- [Data Sharing Details](data-sharing.md)
- [Data Sharing Concept](data-sharing-concept.md)
- [Cross-Account Data Sharing Guide](data_sharing_between_accounts_guide.md)
