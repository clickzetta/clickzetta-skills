# Data Sharing

Data Sharing is Lakehouse's zero-copy cross-instance data authorization feature — you define the tables or views to share, and the recipient instance reads your original data directly, with no copying and no sync delay. **Only supported between instances within the same cloud and service region; cross-cloud or cross-region sharing is not supported.**

---

## I Want to Share Data with Another Account

Three steps: Create a Share → Grant data objects → Specify recipient instances. Both SQL and the Studio UI support the full workflow — choose whichever you prefer.

| Scenario | Approach | Reference |
|------|------|---------|
| Share an entire table with another instance (SQL) | CREATE SHARE + GRANT SELECT + ALTER SHARE ADD INSTANCE | [Cross-Account Data Sharing Guide](data_sharing_between_accounts_guide.md) |
| Share an entire table with another instance (UI) | Data Management → Data Sharing → + New Share | Via Studio |
| Share only certain rows or columns from a table | Create a View to filter data first, then share the View | [Cross-Enterprise Real-Time Data Sharing](quickstart_datashare_between_companies.md) |
| Share all tables under a Schema | GRANT SELECT ON ALL TABLES IN SCHEMA | [Data Sharing SQL Reference](data-sharing.md) |

> ⚠️ Creating a Share requires the `instance_admin` role. Adding data objects to a Share requires the `workspace_admin` role, or both `SELECT` and `READ METADATA` on the table/view with `WITH GRANT OPTION`.

> ⚠️ A single Share can contain at most 1000 table or view objects, and can only include data objects from the same workspace.

---

## I Want to Receive and Use Data Shared with Me

The consumer needs to first view the received Share, then create a local read-only Schema mapped to the shared data.

| Scenario | Approach | Reference |
|------|------|---------|
| View which shares I have received | `SHOW SHARES` (look for `INBOUND` type) or Studio "Shared with Me" tab | [Data Sharing](data-sharing.md) |
| View which data objects are in a share | DESC SHARE &lt;provider&gt;.&lt;share_name&gt; | [DESC SHARE](desc-share.md) |
| Create a local Schema to access shared data | CREATE SCHEMA ... FROM SHARE &lt;provider&gt;.&lt;share&gt;.&lt;schema&gt; | [Cross-Account Data Sharing Guide](data_sharing_between_accounts_guide.md) |
| Extract data via Studio UI | Data Sharing → Shared with Me → Click "Extract" | [Data Sharing](data-sharing.md) |

> ⚠️ Schemas created via Share are read-only — you cannot create tables, views, or other objects in them, and write operations on shared data are not allowed.

> ⚠️ Re-sharing received data is prohibited. Consumers can copy data via `CREATE TABLE AS SELECT`; providers should carefully consider the scope of what they share.

---

## I Want to Use the Studio UI

Studio provides a complete data sharing management interface, suitable for users unfamiliar with SQL or for routine management operations.

| Operation | Path | Required Role |
|------|------|---------|
| Create a new share | Data Management → Data Sharing → + New Share | `instance_admin` |
| View shares I have sent | Data Management → Data Sharing → My Shares | `instance_admin` or `workspace_admin` |
| Add/remove shared data objects | Click share name → Edit | `workspace_admin` (workspace owning the share) |
| Add/remove recipient instances | Click share name → Recipient Instances → Add/Remove | `instance_admin` |
| View shares received | Data Management → Data Sharing → Shared with Me | `instance_admin` or `workspace_admin` |
| Extract shared data (consumer) | Shared with Me → Click "Extract" | `workspace_admin` (target workspace) |

> The consumer needs to provide their service instance name to the provider. The instance name can be found in the top-right corner of the homepage or in the service instance URL.

---

## I Want to Use SQL Commands

The complete SQL workflow, suitable for automation scripts or scenarios requiring fine-grained control.

| Operation | SQL Command | Reference |
|------|---------|---------|
| Create a Share | `CREATE SHARE <name>` | [CREATE SHARE](create-share.md) |
| Grant a table to a Share | GRANT SELECT, READ METADATA ON TABLE &lt;t&gt; TO SHARE &lt;s&gt; | [GRANT TO SHARE](grant-to-share.md) |
| Grant a view to a Share | GRANT SELECT, READ METADATA ON VIEW &lt;v&gt; TO SHARE &lt;s&gt; | [GRANT TO SHARE](grant-to-share.md) |
| Grant all tables in a Schema | GRANT ... ON ALL TABLES IN SCHEMA &lt;s&gt; TO SHARE &lt;share&gt; | [GRANT TO SHARE](grant-to-share.md) |
| Add a recipient instance | ALTER SHARE &lt;s&gt; ADD INSTANCE &lt;instance&gt; | [ALTER SHARE](alter-share.md) |
| Remove a recipient instance | ALTER SHARE &lt;s&gt; REMOVE INSTANCE &lt;instance&gt; | [ALTER SHARE](alter-share.md) |
| Revoke data object authorization | REVOKE SELECT, READ METADATA ON TABLE &lt;t&gt; FROM SHARE &lt;s&gt; | [REVOKE FROM SHARE](revoke-from-share.md) |
| Consumer creates a read-only Schema | CREATE SCHEMA ... FROM SHARE &lt;provider&gt;.&lt;share&gt;.&lt;schema&gt; | [Data Sharing](data-sharing.md) |
| Delete a Share | `DROP SHARE <name>` | [DROP SHARE](drop-share.md) |

> ⚠️ `GRANT SELECT ON ALL TABLES IN SCHEMA` automatically includes tables **created in the future** under that Schema — use with caution.

---

## I Want to View and Manage Existing Shares

| Scenario | SQL | Notes |
|------|-----|------|
| View all Shares (including received) | `SHOW SHARES` | `OUTBOUND` = shares I sent; `INBOUND` = shares I received |
| View details of a specific Share | `DESC SHARE <name>` | Shows included data objects and recipient instances |
| View authorization details of a Share | SHOW GRANTS TO SHARE &lt;name&gt; | Use when troubleshooting permission configuration |
| Delete a Share | `DROP SHARE <name>` | Takes effect immediately; consumers lose access instantly and it cannot be undone |

---

## Not Sure How to Proceed?

```
What is my role?
├── Data Provider (I have data and want to share it)
│   ├── Share an entire table → CREATE SHARE + GRANT SELECT ON TABLE
│   ├── Share partial data (row/column filter) → Create a View first, then GRANT SELECT ON VIEW
│   └── Share an entire Schema → GRANT SELECT ON ALL TABLES IN SCHEMA (note: includes future tables)
│
└── Data Consumer (someone shared data with me)
    ├── First confirm what was received → SHOW SHARES (look for INBOUND)
    ├── View share contents → DESC SHARE <provider_instance>.<share_name>
    └── Create a local access entry → CREATE SCHEMA FROM SHARE

Preferred method?
├── Have SQL access → Refer to the SQL command table above
└── Prefer UI → Studio Data Management → Data Sharing
```

---

## Related Documentation

- [Data Sharing Concepts](data-sharing-concept.md) — Core principles, Share object structure, permission model
- [Data Sharing Complete Reference](data-sharing.md) — Full operation steps and permission details
- [Cross-Account Data Sharing Guide](data_sharing_between_accounts_guide.md) — End-to-end operation example
- [Cross-Enterprise Real-Time Data Sharing](quickstart_datashare_between_companies.md) — Complete case with view filtering
- [Data Sharing SQL Guide](SQL_Share_Guide.md) — SQL command reference
- [CREATE SHARE](create-share.md) · [ALTER SHARE](alter-share.md) · [GRANT TO SHARE](grant-to-share.md) · [REVOKE FROM SHARE](revoke-from-share.md) · [SHOW SHARES](show-shares.md) · [DESC SHARE](desc-share.md) · [DROP SHARE](drop-share.md)
