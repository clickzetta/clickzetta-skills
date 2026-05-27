# Lakehouse Cross-instance Data Sharing Guide (Share)

## Overview

Cross-instance Data Sharing allows you to securely share tables or views from your Lakehouse with users in other instances without copying data. Through `CREATE SHARE` and `GRANT` commands, you can finely control the sharing scope and permissions. This guide is organized by business scenario to help you quickly master data sharing configuration methods.

### Quick Navigation

* [Create Data Share](#create-data-share) -- Define a share object
* [Grant Tables to Share](#grant-tables-to-share) -- Add tables to a share
* [Add Consumer Instance](#add-consumer-instance) -- Specify target instances that can access the share
* [View Share Information](#view-share-information) -- Monitor share status
* [Revoke Share](#revoke-share) -- Remove share permissions or delete the share

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `CREATE SHARE` | Create a share object | Define a data sharing container |
| `GRANT ... TO SHARE` | Grant table/view to a share | Configure share content |
| `ALTER SHARE ... ADD INSTANCE` | Add consumer instance | Specify share targets |
| `SHOW SHARES` | View share list | Monitor share status |
| `DROP SHARE` | Drop a share | Clean up abandoned shares |

***

## Prerequisites

The following examples use a simulated shared table `shared_sales`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS shared_sales (
    sale_id INT,
    product STRING,
    amount DOUBLE,
    sale_date DATE
);

-- Insert test data
INSERT INTO shared_sales VALUES
(1, 'Phone', 5000, '2024-06-01'),
(2, 'Laptop', 8000, '2024-06-02');
```

***

## Create Data Share

Use `CREATE SHARE` to define a share object, which serves as the container for data sharing.

```sql
-- Create a share
CREATE SHARE sales_share;
```

> **Tip**: A newly created share is empty; use `GRANT` to add tables or views.

***

## Grant Tables to Share

Use the `GRANT` command to grant read permissions on tables or views to a share object.

```sql
-- Grant table read permission to the share
GRANT SELECT ON TABLE shared_sales TO SHARE sales_share;
```

**Supported Permissions**:
* `SELECT`: Allows the consumer instance to query table data.
* `READ METADATA`: Allows the consumer instance to view table structure (schema).

***

## Add Consumer Instance

Use `ALTER SHARE` to add a target Lakehouse instance to the share, enabling it to access shared data.

```sql
-- Add a consumer instance (replace with the actual instance ID)
ALTER SHARE sales_share ADD INSTANCE 'consumer_instance_id';
```

> **Note**: The consumer instance must be under the same Singdata platform account system, or have cross-account sharing policies configured.

***

## View Share Information

Use `SHOW SHARES` to view all share configurations for the current instance.

```sql
-- View share list
SHOW SHARES;

-- View share details
DESC SHARE sales_share;
```

**Returned Information**:
* `share_name`: Share name
* `kind`: Share type (OUTBOUND / INBOUND)
* `objects`: List of shared tables/views

***

## Revoke Share

Use `REVOKE` or `DROP SHARE` to remove share permissions.

```sql
-- Revoke table share permission
REVOKE SELECT ON TABLE shared_sales FROM SHARE sales_share;

-- Drop the share
DROP SHARE sales_share;
```

> **Tip**: Dropping a share does not affect source table data; it only cuts off the access channel for consumer instances.

***

## Clean Up Test Data

After completing share verification, it is recommended to clean up test data:

```sql
-- Drop test table
DROP TABLE IF EXISTS shared_sales;
DROP SHARE IF EXISTS sales_share;
```

> **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Read-only Sharing**: Shares only support `SELECT` permissions; consumer instances cannot modify source table data.
2. **Real-time**: When a consumer instance queries shared tables, it reads the latest data from the source instance with no synchronization delay.
3. **Network Policies**: Cross-cloud or cross-region sharing requires network policies (such as PrivateLink) to be correctly configured.
4. **Permission Inheritance**: Row-level permissions or dynamic masking policies on shared tables are synchronously applied to consumer instances.
5. **Billing**: Compute resource costs from share queries are borne by the consumer instance; storage costs are borne by the provider.

***

## Related Documentation

* [Data Sharing](data-sharing.md)
* [CREATE SHARE](create-share.md)
* [GRANT TO SHARE](grant-to-share.md)
