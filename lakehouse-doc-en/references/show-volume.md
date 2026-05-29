# SHOW VOLUMES

## Syntax

```sql
SHOW VOLUMES [IN schema_name] [LIKE 'pattern' | WHERE expr] [LIMIT num]
```

## Parameters

1. `LIKE pattern`: Optional parameter for pattern matching and filtering by volume name. Supports case-insensitive matching using SQL wildcards `%` (matches any number of characters) and `_` (matches a single character). Example: `LIKE '%testing%'`. Note: Cannot be used simultaneously with the `WHERE` clause.

2. `IN schema_name`: Optional parameter for specifying a particular schema name, listing all volumes under that schema.

3. `WHERE expr`: Optional parameter for filtering based on the fields displayed by the `SHOW VOLUMES` command, supporting precise filtering of results using expressions.

## Display Fields

| Field | Description |
| --- | --- |
| volume_name | Volume name |
| create_time | Volume creation time |
| external | Whether it is an external Volume |
| workspace_name | Workspace name to which the Volume belongs |
| url | Volume URL address |
| recursive_file_lookup | Whether recursive file lookup is enabled |
| connection | Volume connection information |

## Examples

```sql
SHOW VOLUMES;
```

```sql
SHOW VOLUMES WHERE volume_name = 'zettapark_csv';
```

```sql
SHOW VOLUMES WHERE external = true;
```

```sql
SHOW VOLUMES WHERE workspace_name = 'xxx';
```

```sql
SHOW VOLUMES WHERE recursive_file_lookup = false;
```

Query which volumes use xxx.storage_connection:

```sql
SHOW VOLUMES WHERE connection = 'xxx.storage_connection';
```

## Description

This command lists all Volume information under the current schema and supports filtering results based on specified conditions via the WHERE clause.

---

## SHOW VOLUME DIRECTORY

View the file listing under an external Volume or Named Volume.

```Plain
SHOW VOLUME DIRECTORY <volume_name> [SUBDIRECTORY '<path>']
```

```SQL
-- View all files in the Volume root directory
SHOW VOLUME DIRECTORY my_oss_vol;

-- View a specific subdirectory
SHOW VOLUME DIRECTORY my_oss_vol SUBDIRECTORY 'data/2024/';
```

### Return Columns

| Column | Description |
|--------|-------------|
| `relative_path` | File relative path |
| `url` | File full URL |
| `size` | File size (bytes) |
| `last_modified_time` | Last modified time |

> ⚠️ **Note**: External Volume file listings may have cache delays. If a file has been uploaded but does not appear, run `ALTER VOLUME <name> REFRESH` to refresh directory metadata before querying again.

---

## SHOW USER VOLUME DIRECTORY

View the file listing in the current user's User Volume (personal internal storage).

```Plain
SHOW USER VOLUME DIRECTORY [SUBDIRECTORY '<path>']
```

```SQL
-- View User Volume root directory
SHOW USER VOLUME DIRECTORY;

-- View subdirectory
SHOW USER VOLUME DIRECTORY SUBDIRECTORY 'uploads/';
```

Return columns are the same as `SHOW VOLUME DIRECTORY`.

## Related Documents

- [SHOW VOLUMES](show-volume.md)
- [ALTER VOLUME](alter-volume.md)
- [Volume Overview](volume-overview.md)
