# Synonym

A Synonym creates an **alias** for a data object in the Lakehouse, allowing the same object to be accessed by different names without copying any data. Synonyms belong to a schema, and names must be unique within the same schema.

Synonyms can be created for the following object types: table, table stream, dynamic table, materialized view, volume, and function.

## Typical Use Cases

| Scenario | Description |
|------|------|
| Simplify cross-schema references | Create a synonym in `schema02` for a table in `schema01` — no need to write the full path in queries, and data stays in sync in real time |
| Maintain compatibility with old names | After renaming a table, create a synonym for the old name so existing SQL does not need to be updated |
| Abstraction layer isolation | Protects client applications from changes to the names or locations of underlying objects |

## Create Syntax

```SQL
CREATE [TABLE|VOLUME|FUNCTION] SYNONYM [schema_name.]synonym_name FOR object [COMMENT ''];

object ::= workspace_name.schema_name.object_name | schema_name.object_name | object_name
```

**Object type keywords**:

- `TABLE` (default): Used for table, table stream, dynamic table, and materialized view. The keyword can be omitted.
- `VOLUME`: **Must** be specified when creating a synonym for a volume; otherwise the system defaults to looking for a table object with that name.
- `FUNCTION`: **Must** be specified when creating a synonym for a function; otherwise the system defaults to looking for a table object with that name.

## Drop Syntax

```SQL
DROP [TABLE|VOLUME|FUNCTION] SYNONYM [IF EXISTS] [schema.]synonym_name;
```

## Permission Management

```SQL
-- Grant permission to create synonyms
GRANT CREATE SYNONYM ON SCHEMA schema_name TO USER user_name;

-- Grant permission to drop synonyms
GRANT DROP SYNONYM ON ALL SYNONYMS IN SCHEMA schema_name TO USER user_name;
```

Query permissions on a synonym are the same as permissions on the base object: granting permissions on a synonym is equivalent to granting permissions on the base object, and vice versa.

## Usage Examples

### Creating a Synonym for a Table

```SQL
CREATE TABLE public.students (name STRING, class STRING);

-- Create synonym
CREATE SYNONYM students_sy FOR public.students;

-- Query via synonym
SELECT * FROM students_sy;

-- Drop synonym
DROP SYNONYM students_sy;
```

### Creating a Synonym for a Table Stream

```SQL
CREATE SYNONYM students_stream_sy FOR public.students_stream;
DROP SYNONYM students_stream_sy;
```

### Creating a Synonym for a Dynamic Table

```SQL
CREATE SYNONYM event_group_minute_sy FOR public.event_group_minute;
DROP SYNONYM event_group_minute_sy;
```

### Creating a Synonym for a Materialized View

```SQL
CREATE SYNONYM event_group_mv_sy FOR event_group_mv;
DROP SYNONYM event_group_mv_sy;
```

### Creating a Synonym for a Volume (VOLUME keyword required)

```SQL
CREATE VOLUME SYNONYM hz_csv_volume_sy FOR public.hz_csv_volume;
DROP VOLUME SYNONYM hz_csv_volume_sy;
```

### Creating a Synonym for a Function (FUNCTION keyword required)

```SQL
CREATE FUNCTION SYNONYM s_upper FOR public.swu_udf_upper;
DROP FUNCTION SYNONYM s_upper;
```

## Viewing Synonyms

```SQL
-- List all synonyms in the current schema
SHOW SYNONYMS;

-- Filter by condition
SHOW SYNONYMS IN SCHEMA public WHERE synonym_name = 'students_sy';
-- Result:
-- +--------------+-------------------------+-------------+-----------------------+
-- | synonym_name |       create_time       | target_type |       target_name     |
-- +--------------+-------------------------+-------------+-----------------------+
-- | students_sy  | 2024-06-14 10:21:00.504 | TABLE       | ql_ws.public.students |
-- +--------------+-------------------------+-------------+-----------------------+
```

## Related Documentation

- [CREATE SYNONYM](create-synonym.md) — Complete syntax
- [DROP SYNONYM](drop-synonym.md) — Drop syntax
- [SHOW SYNONYMS](show-synonyms.md) — Listing synonyms
