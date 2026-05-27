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

This command is used to list all Volume information under the current schema, and supports filtering results based on specified conditions via the WHERE clause.
