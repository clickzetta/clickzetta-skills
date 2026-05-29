# Basic Commands

Basic commands cover object identifier conventions, comment syntax, session parameter settings, and general DDL commands (CREATE, ALTER, DROP, UNDROP, DESC, SHOW) that apply to all object types.

---

## In This Chapter

| Page | Description |
|------|-------------|
| [Object Identifiers](object_identifier.md) | Naming rules, reserved words, quoted identifiers, three-part fully qualified names |
| [Comments](sql-comments.md) | Single-line comment (`--`) and multi-line comment (`/* */`) syntax |
| [SET (Session Parameters)](set-properties.md) | Set runtime parameters for the current session, such as timezone and query timeout |
| [ALTER WORKSPACE](alter-workspace.md) | Modify workspace-level configuration parameters |
| [CREATE (All Objects)](create.md) | General syntax and options for CREATE statements |
| [ALTER (All Objects)](alter.md) | General syntax and options for ALTER statements |
| [DROP (All Objects)](drop.md) | General syntax for DROP statements; supports IF EXISTS |
| [UNDROP (All Objects)](undrop.md) | Restore a dropped object within the data retention period |
| [DESC (All Objects)](describe.md) | View the structure and properties of an object |
| [DESC HISTORY (All Objects)](desc-history.md) | View the version history of an object |
| [SHOW (All Objects)](show.md) | List all objects of a given type; supports LIKE and WHERE filters |

---

## Common Operations

### Object Identifiers

```SQL
-- Three-part fully qualified name (cross-schema reference)
SELECT * FROM my_workspace.public.orders;

-- Two-part name (current workspace)
SELECT * FROM public.orders;

-- Backtick quoting for names with special characters
SELECT * FROM `my-schema`.`order-table`;
```

### Session Parameters

```SQL
-- Set query timeout (seconds)
SET QUERY_TIMEOUT = 300;

-- Set timezone
SET TIME_ZONE = 'Asia/Shanghai';
```

### General DDL

```SQL
-- View object details (table as example)
DESC TABLE public.orders;

-- View object version history
DESC HISTORY public.orders;

-- List all tables (supports pattern matching)
SHOW TABLES LIKE 'order%';

-- List all schemas
SHOW SCHEMAS;

-- Drop an object (IF EXISTS prevents errors)
DROP TABLE IF EXISTS public.temp_table;

-- Restore a dropped table (within retention period)
UNDROP TABLE public.temp_table;
```

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [SQL Commands Overview](sql-commands.md) | Categorized navigation for all SQL commands |
| [INFORMATION_SCHEMA](information_schema_guide.md) | Query metadata via SQL |
