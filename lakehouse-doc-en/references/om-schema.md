# Schema

A Schema is a **namespace** within a workspace, used for logical grouping and permission isolation of data objects such as tables, views, and functions.

Analogy to relational databases: a workspace is equivalent to a database instance, and a schema is equivalent to a database. Multiple schemas can be created within a single workspace, for example, divided by business domain as `ods`, `dwd`, `ads`.

## Key Purposes of Schema

| Purpose | Description |
|------|------|
| Logical grouping | Group related tables and views by business domain or data layer |
| Name isolation | Objects with the same name can exist in different schemas without conflicts |
| Permission control | Grant access permissions at the schema level as a whole |
| Default context | Set the current schema with `USE SCHEMA` to simplify SQL writing |

## Hierarchy

```
Workspace
├── Schema A (e.g., ods)
│   ├── Tables
│   └── Views
└── Schema B (e.g., ads)
    └── Tables
```

## Common Operations

```sql
-- Create a schema
CREATE SCHEMA ods;

-- Switch the current schema
USE SCHEMA ods;

-- Reference objects across schemas
SELECT * FROM ads.dim_user;
```

## Related Documentation

- [CREATE SCHEMA](create-schema.md)
- [SHOW SCHEMAS](show-schemas.md)
- [External Schema](external-schema.md) — Schema mapped to external data sources
