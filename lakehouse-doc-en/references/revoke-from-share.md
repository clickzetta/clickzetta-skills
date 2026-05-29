# REVOKE FROM SHARE

## Description

The `REVOKE FROM SHARE` statement is used to revoke table or view privileges previously granted to a SHARE object, thereby removing that object from the SHARE. After execution, consumers will no longer be able to access the corresponding table or view through the SHARE.

Only SHAREs with the type (`kind` attribute) `OUTBOUND` are supported; INBOUND SHAREs imported from external sources cannot be operated on.

## Syntax

```Plain
REVOKE [ PERMISSIONS ] ON { TABLE table_name | VIEW view_name } FROM SHARE share_name;
```

## Parameter Description

| Parameter | Required | Description |
|-----------|----------|-------------|
| `PERMISSIONS` | No | The list of privileges to revoke. Valid values are `SELECT` (query data) and `READ METADATA` (view metadata). When omitted, all privileges are revoked |
| `TABLE table_name` | Choose one | The table name for which to revoke privileges |
| `VIEW view_name` | Choose one | The view name for which to revoke privileges |
| `share_name` | Yes | The name of the target SHARE |

## Usage Examples

### Example 1: Revoke both query and metadata privileges on a table

```SQL
REVOKE SELECT, READ METADATA ON TABLE doc_test.employees FROM SHARE doc_test_share;
```

After execution, consumers will be unable to query the `doc_test.employees` table or view its metadata.

### Example 2: Revoke only query privileges while retaining metadata privileges

```SQL
REVOKE SELECT ON TABLE doc_test.orders FROM SHARE sales_share;
```

### Example 3: Revoke query privileges on a view

```SQL
REVOKE SELECT ON VIEW report_schema.monthly_summary FROM SHARE analytics_share;
```

### Example 4: Verify after revoking

After revoking privileges, use `SHOW GRANTS TO SHARE` to confirm that the object has been removed from the SHARE:

```SQL
SHOW GRANTS TO SHARE doc_test_share;
```

If the result no longer includes the table, the revocation was successful.

## Notes

- Revoked privileges take effect immediately; consumers will immediately lose access to the object.
- To re-authorize, use `GRANT TO SHARE` to add it back.
- The revocation operation does not affect the SHARE itself or other authorized objects, nor does it affect consumer instance configuration (`ALTER SHARE INSTANCE`).
- To completely delete a SHARE, use `DROP SHARE`.

## Permission Requirements

The user executing `REVOKE FROM SHARE` must have administrative privileges or OWNERSHIP on the corresponding SHARE.

## Related Statements

- [GRANT TO SHARE](grant-to-share.md): Add a table or view to a SHARE
- [CREATE SHARE](create-share.md): Create a SHARE object
- [DROP SHARE](drop-share.md): Delete a SHARE object
