# Schema

Schema DDL commands are used to create, modify, switch, and drop Schema namespaces within a workspace.

---

## Contents

| Page | Description |
|------|-------------|
| [CREATE SCHEMA](create-schema.md) | Create a new Schema in the current workspace |
| [ALTER SCHEMA](alter-schema.md) | Modify Schema properties or rename a Schema |
| [DROP SCHEMA](drop-schema.md) | Drop a Schema and all objects it contains |
| [USE SCHEMA](use-schema.md) | Switch the default Schema for the current session |
| [DESC SCHEMA](desc-schemas.md) | View Schema properties and details |
| [SHOW SCHEMAS](show-schemas.md) | List all Schemas in the current workspace |

---

## Common Operations

### Create a Schema

```sql
-- Create a Schema
CREATE SCHEMA IF NOT EXISTS dwd;

-- Create with a comment
CREATE SCHEMA IF NOT EXISTS ads COMMENT = 'Application-facing aggregation layer';
```

### View and Switch

```sql
-- List all Schemas
SHOW SCHEMAS;

-- View Schema details
DESC SCHEMA dwd;

-- Switch the default Schema for the current session
USE SCHEMA dwd;
```

### Modify and Drop

```sql
-- Rename a Schema
ALTER SCHEMA old_name RENAME TO new_name;

-- Drop a Schema (must be empty or use CASCADE)
DROP SCHEMA IF EXISTS temp_schema;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Command Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [External Catalog & Schema](external_catalog_schema.md) | External Schema in federated queries |
| [Schema (Object Model)](om-schema.md) | Schema concepts, namespaces, and permission management |
