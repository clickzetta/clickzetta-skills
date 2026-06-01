# Data Sharing (Share)

Data Sharing (Share) lets you securely share tables or views in Lakehouse with users in other instances — no data copying required. Once the provider grants access, the consumer reads the original data in real time; any updates on the provider side are immediately visible to the consumer.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [CREATE SHARE](create-share.md) | Create a share object |
| [ALTER SHARE](alter-share.md) | Modify a share object, including adding/removing target instances |
| [GRANT TO SHARE](grant-to-share.md) | Add tables or views to a share object |
| [REVOKE FROM SHARE](revoke-from-share.md) | Remove previously granted objects from a share |
| [DROP SHARE](drop-share.md) | Drop a share object |
| [DESC SHARE](desc-share.md) | View the details of a share object |
| [SHOW SHARES](show-shares.md) | List all share objects in the current instance |
| [CREATE SCHEMA FROM SHARE](create-schema-from-share.md) | Consumer mounts shared data by creating a read-only schema in the local workspace |

---

## Typical Workflow

**Provider: Create and authorize a share**

```SQL
-- 1. Create a share object
CREATE SHARE my_share;

-- 2. Add a table to the share
GRANT select, read metadata ON TABLE public.orders TO SHARE my_share;

-- 3. Authorize the consumer instance
ALTER SHARE my_share ADD INSTANCE consumer_instance;
```

**Consumer: Mount and query shared data**

```SQL
-- Mount shared data as a local read-only schema (specify the schema name from the share)
CREATE SCHEMA my_shared_data FROM SHARE provider_instance.my_share.shared_schema;

-- Query directly — no data copying needed
SELECT * FROM my_shared_data.orders;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Cross-Instance Data Sharing Guide](sql_share_guide.md) | Complete operation guide organized by business scenario, including permission configuration and FAQs |
