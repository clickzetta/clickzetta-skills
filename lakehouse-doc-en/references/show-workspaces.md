# SHOW WORKSPACES

## Overview

Lists all workspaces (Workspace / Catalog) in the current instance, including MANAGED, EXTERNAL, and SHARED types. Returns the same result as `SHOW CATALOGS`.

## Syntax

```Plain
SHOW WORKSPACES [ LIKE '<pattern>' ]
```

## Parameters

- `LIKE '<pattern>'`: Optional. Filters results by name. Supports `%` (matches any sequence of characters) and `_` (matches a single character) wildcards.

## Return Columns

| Column | Description |
|--------|-------------|
| `workspace_name` | Catalog name |
| `created_time` | Creation time |
| `category` | Type: `MANAGED` / `EXTERNAL` / `SHARED` |

## Examples

```sql
SHOW WORKSPACES;
```

Sample output (partial):

| workspace_name | created_time | category |
|----------------|--------------|----------|
| quick_start | 2025-01-15 10:27:21 | MANAGED |
| clickzetta_sample_data | 2025-01-15 10:27:21 | SHARED |
| databricks_main_catalog | 2025-11-20 12:00:49 | EXTERNAL |

```sql
-- Filter by name
SHOW WORKSPACES LIKE '%test%';
```

## Related Documentation

- [SHOW CATALOGS](show-catalog.md) — equivalent command
- [DESC WORKSPACE](desc-workspace.md) — view details of a single catalog
- [CREATE EXTERNAL CATALOG](create-external-catalog.md)
