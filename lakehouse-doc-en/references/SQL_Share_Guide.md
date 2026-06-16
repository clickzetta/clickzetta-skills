# Lakehouse Cross-Instance Data Sharing Guide (Share)

## Overview

Cross-instance data sharing allows you to securely share tables or views in Lakehouse with users in other instances without copying data. Using `CREATE SHARE` and `GRANT` commands, you can precisely control the scope and permissions of sharing. This guide is organized by business scenario to help you quickly master data sharing configuration.

## SQL Commands Involved

| Command | Purpose | Use Case |
|---------|---------|----------|
| `CREATE SHARE` | Create a share object | Define a data sharing container |
| `GRANT ... TO SHARE` | Grant table/view access to a share | Configure share content |
| `ALTER SHARE ... ADD INSTANCE` | Add a consumer instance | Specify sharing targets |
| `SHOW SHARES` | View share list | Monitor share status |
| `DROP SHARE` | Delete a share | Clean up obsolete shares |

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

## Creating a Data Share

Use `CREATE SHARE` to define a share object as a container for data sharing.

```sql
-- Create a share
CREATE SHARE sales_share;
```

> 💡 **Tip**: A newly created share is empty by default. Use `GRANT` to add tables or views.

***

## Granting Shared Tables

Use the `GRANT` command to grant read access on a table or view to a share object.

```sql
-- Grant read access on a shared table
GRANT SELECT ON TABLE shared_sales TO SHARE sales_share;
```

**Supported permissions**:
* `SELECT`: Allows consumer instances to query table data.
* `READ METADATA`: Allows consumer instances to view the table schema.

***

## Adding Consumer Instances

Use `ALTER SHARE` to add a target Lakehouse instance to the share, enabling it to access the shared data.

```sql
-- Add a consumer instance (replace with the actual instance ID)
ALTER SHARE sales_share ADD INSTANCE 'consumer_instance_id';
```

> ⚠️ **Note**: Consumer instances must be under the same Singdata platform account, or a cross-account sharing policy must be configured.

***

## Viewing Share Information

Use `SHOW SHARES` to view all share configurations for the current instance.

```sql
-- View share list
SHOW SHARES;

-- View share details
DESC SHARE sales_share;
```

**Returned information**:
* `share_name`: Share name
* `kind`: Share type (OUTBOUND / INBOUND)
* `objects`: List of shared tables/views

***

## Revoking a Share

Use `REVOKE` or `DROP SHARE` to remove share permissions.

```sql
-- Revoke share permission on a table
REVOKE SELECT ON TABLE shared_sales FROM SHARE sales_share;

-- Delete the share
DROP SHARE sales_share;
```

> 💡 **Tip**: Deleting a share does not affect the source table data; it only cuts off the consumer instance's access channel.

***

## Cleaning Up Test Data

After completing share verification, it is recommended to clean up the test table:

```sql
-- Drop test table
DROP TABLE IF EXISTS shared_sales;
DROP SHARE IF EXISTS sales_share;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, so accidentally dropped tables can be recovered within the retention period.

***

## Notes

1. **Read-only sharing**: Shares only support `SELECT` permission; consumer instances cannot modify source table data.
2. **Real-time access**: When a consumer instance queries a shared table, it reads the latest data from the source instance directly with no synchronization delay.
3. **Network policy**: Cross-cloud or cross-region sharing requires that network policies (such as PrivateLink) are correctly configured.
4. **Permission inheritance**: Row-level permissions or dynamic data masking policies on shared tables also take effect on consumer instances.
5. **Billing**: Compute resource consumption from shared queries is borne by the consumer instance; storage costs are borne by the provider.

***

## FAQ

| Issue | Cause | Solution |
|-------|-------|----------|
| CREATE SHARE reports insufficient permissions | Requires the `instance_admin` role | Contact an administrator to grant `instance_admin` |
| Consumer cannot see the Share | Provider has not executed ADD INSTANCE | Provider executes `ALTER SHARE <share> ADD INSTANCE <consumer_instance>` |
| DESC SHARE reports Share not found | `instance_name` is incorrect | Confirm the exact value of the `provider_instance` field via `SHOW SHARES` |
| Consumer cannot find a table after mounting the Schema | The table was not included in the GRANT | Provider re-executes `GRANT SELECT, READ METADATA ON TABLE ... TO SHARE` |
| Only want to share certain columns or rows | Sharing the table directly exposes all data | Create a VIEW to filter the required columns/rows first, then add the VIEW to the Share |

***

## Related Documentation

* [Data Sharing](data-sharing.md)
* [CREATE SHARE](create-share.md)
* [GRANT TO SHARE](grant-to-share.md)
