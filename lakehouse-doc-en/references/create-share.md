# CREATE SHARE

## Overview

Data sharing is like a read-only link to a shared document — after the provider grants access, the consumer reads the original data in real time without copying it. When the provider's data is updated, the consumer can see the changes immediately.

The `CREATE SHARE` statement is used to create a SHARE object for sharing data with other Lakehouse instances (accounts). The created SHARE object has its `kind` attribute set to `OUTBOUND`, indicating that data is being provided externally.

After creating a SHARE, you need to use `GRANT TO SHARE` to add tables or views to the SHARE, and then use `ALTER SHARE ADD INSTANCE` to specify the target instances for sharing.

## Syntax

```Plain
CREATE SHARE [ IF NOT EXISTS ] share_name [ COMMENT 'comment' ];
```

## Parameter Description

| Parameter | Required | Description |
|------|----------|------|
| `share_name` | Yes | The name of the SHARE, which must be unique within the same account |
| `IF NOT EXISTS` | No | If the SHARE already exists, skip without raising an error |
| `COMMENT 'comment'` | No | A descriptive comment for the SHARE |

**share_name Naming Rules:**
- Supports letters, underscores, and digits; special characters and spaces are not allowed
- Must start with a letter or underscore; letters are automatically converted to lowercase
- Length: 1–255 bytes
- Must be unique within the same account

## Usage Examples

### Example 1: Create a Basic SHARE

```SQL
CREATE SHARE share_demo;
```

### Example 2: Create a SHARE with a Comment

```SQL
CREATE SHARE IF NOT EXISTS doc_test_share COMMENT 'Share for documentation testing';
```

### Example 3: Create a SHARE and Add a Table

After creating a SHARE, use `GRANT TO SHARE` to add a table:

```SQL
-- Step 1: Create the SHARE
CREATE SHARE IF NOT EXISTS sales_share;

-- Step 2: Add a table to the SHARE (grant SELECT and metadata viewing privileges)
GRANT SELECT, READ METADATA ON TABLE sales_schema.orders TO SHARE sales_share;

-- Step 3: View the granted objects in the SHARE
SHOW GRANTS TO SHARE sales_share;
```

`SHOW GRANTS TO SHARE` example output:

```Plain
+--------------+------------+-----------+----------+---------------------------------+------------+--------------+--------------+--------------+-------------------------+
| granted_type | privilege  | conditions| granted_on | object_name                  | granted_to | grantee_name | grantor_name | grant_option | granted_time            |
+--------------+------------+-----------+----------+---------------------------------+------------+--------------+--------------+--------------+-------------------------+
| PRIVILEGE    | READ METADATA |        | SCHEMA   | quick_start.sales_schema        | SHARE      | sales_share  | qiliang      | false        | 2026-05-19 22:56:42.377 |
| PRIVILEGE    | SELECT TABLE  |        | TABLE    | quick_start.sales_schema.orders | SHARE      | sales_share  | qiliang      | false        | 2026-05-19 22:56:42.377 |
| PRIVILEGE    | READ METADATA |        | TABLE    | quick_start.sales_schema.orders | SHARE      | sales_share  | qiliang      | false        | 2026-05-19 22:56:42.377 |
+--------------+------------+-----------+----------+---------------------------------+------------+--------------+--------------+--------------+-------------------------+
```

### Example 4: View All OUTBOUND SHAREs

```SQL
SHOW SHARES WHERE KIND = 'OUTBOUND';
```

Example output (partial):

```Plain
+------------+----------+-------------------+--------------------+-------+-------------+---------+
| share_name | provider | provider_instance | provider_workspace | scope | to_instance | kind    |
+------------+----------+-------------------+--------------------+-------+-------------+---------+
| sales_share| tyhfosmf | f8866243          | quick_start        | PRIVATE|            | OUTBOUND|
+------------+----------+-------------------+--------------------+-------+-------------+---------+
```

## Notes

- After creating a SHARE, you must use `GRANT TO SHARE` to add tables or views for the SHARE to contain shareable data.
- You must use `ALTER SHARE ADD INSTANCE` to specify the consumer instance before the other party can access the SHARE.
- A SHARE can contain multiple tables and views, and can be shared with multiple target instances.

## Consumer-Side Operations

After the provider completes authorization and uses `ALTER SHARE ADD INSTANCE` to add the consumer instance to the SHARE, the consumer follows these steps in their own Lakehouse instance to access the shared data:

**Step 1: View Available INBOUND SHAREs**

```SQL
SHOW SHARES WHERE KIND = 'INBOUND';
```

**Step 2: View Objects Contained in the SHARE**

```SQL
DESC SHARE <share_name>;
```

**Step 3: Mount the SHARE in a Local Schema**

```SQL
CREATE SCHEMA <local_schema_name> FROM SHARE <provider_instance_id>.<share_name>;
```

`provider_instance_id` is the provider instance ID, which can be found in the `provider_instance` column of the `SHOW SHARES` result.

**Step 4: Query Shared Tables Directly**

```SQL
SELECT * FROM <local_schema_name>.<table_name>;
```

After mounting, shared tables are queried in the same way as local tables and always reflect the provider's latest data.

## Related Statements

- [GRANT TO SHARE](grant-to-share.md): Add tables or views to a SHARE
- [ALTER SHARE](alter-share.md): Add or remove target instances
- [REVOKE FROM SHARE](revoke-from-share.md): Remove table or view privileges from a SHARE
- [SHOW SHARES](show-shares.md): View the list of SHAREs
- [DROP SHARE](drop-share.md): Delete a SHARE
