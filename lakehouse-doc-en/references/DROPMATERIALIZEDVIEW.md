## Description

This statement is used to delete an existing materialized view in order to release related resources.

For more details, please refer to [Materialized View](<MATERIALIZEDVIEW.md>).

## Syntax
```SQL
DROP MATERIALIZED VIEW [ IF EXISTS ] mv_name;
```
## Parameter Description

- **IF EXISTS**: Optional parameter, indicating that if the materialized view does not exist, no error will be thrown.
- **mv_name**: The name of the materialized view to be deleted.

## Example

1. Delete the materialized view named `my_mv`:
```SQL
DROP MATERIALIZED VIEW my_mv;
```
```markdown
2. Delete the materialized view named `my_mv`, if the view does not exist, no error is thrown:
```
```SQL
DROP MATERIALIZED VIEW IF EXISTS my_mv;
```
```markdown
3. Delete multiple materialized views, namely `mv1`, `mv2`, and `mv3`:
```
```SQL
DROP MATERIALIZED VIEW mv1, mv2, mv3;
```
## Precautions

- Before performing a delete operation, ensure that the materialized view is no longer referenced by other database objects to avoid errors.
- Deleting a materialized view may affect queries and applications that depend on it, so make sure you have made the necessary backups and preparations before performing the delete operation.
- Using the `IF EXISTS` parameter can avoid errors caused by the non-existence of the materialized view. It is recommended to use this parameter in actual operations.