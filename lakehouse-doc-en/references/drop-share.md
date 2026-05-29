# DROP SHARE

## Description

The `DROP SHARE` statement is used to delete an existing SHARE object. After deletion, all consumer instances will immediately lose access to data through that SHARE, and the operation is irreversible.

## Syntax

```Plain
DROP SHARE [ IF EXISTS ] share_name;
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `share_name` | Yes | The name of the SHARE to delete |
| `IF EXISTS` | No | If the SHARE does not exist, skip without raising an error |

## Usage Examples

### Example 1: Drop a SHARE

```SQL
DROP SHARE sales_share;
```

### Example 2: Use IF EXISTS to avoid errors

```SQL
DROP SHARE IF EXISTS doc_test_share;
```

### Example 3: Check consumers before dropping

Before dropping, it is recommended to first check the consumer instances of the SHARE to understand the impact:

```SQL
SHOW SHARES WHERE KIND = 'OUTBOUND';
```

Example return (the `to_instance` column shows configured consumers):

```Plain
+------------+----------+-------------------+--------------------+---------+-------------+---------+
| share_name | provider | provider_instance | provider_workspace | scope   | to_instance | kind    |
+------------+----------+-------------------+--------------------+---------+-------------+---------+
| sales_share| tyhfosmf | f8866243          | quick_start        | PRIVATE | 49d58da9    | OUTBOUND|
+------------+----------+-------------------+--------------------+---------+-------------+---------+
```

Execute the drop after confirming there are no active consumers:

```SQL
DROP SHARE sales_share;
```

## Notes

- After dropping a SHARE, all configured consumer instances will **immediately** lose access, which may cause errors in consumer queries or tasks.
- Dropping a SHARE does not delete the tables or views included in the SHARE; it only removes the sharing relationship.
- The operation is irreversible. To restore sharing, you must recreate the SHARE and reconfigure permissions and consumer instances.
- It is recommended to notify relevant consumers before dropping to avoid business disruptions.

## Permission Requirements

The user executing `DROP SHARE` must have the DROP privilege or OWNERSHIP on the corresponding SHARE.

## Related Statements

- [CREATE SHARE](create-share.md): Create a SHARE object
- [ALTER SHARE](alter-share.md): Modify the target instances of a SHARE
- [SHOW SHARES](show-shares.md): Query the list of existing SHAREs
