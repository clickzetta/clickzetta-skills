## Feature Introduction

The `CACHE TABLE` command allows users to pre-load cold data into the Vcluster during the AP VC startup phase or when executing Adhoc queries through SQL statements, thereby improving query speed. Currently, this feature is only applicable to ANALYTICAL VCLUSTER.

## Syntax
```
CACHE TABLE table_name;
```
## Parameter Description

- `table_name`: Specify the name of the table to be cached.

## Usage Example

1. Temporarily cache the specified table into Vcluster:
   ```
   CACHE TABLE tpc100g.lineitem, nation;
   ```
2. Temporarily cache multiple tables into Vcluster:
   ```
   CACHE TABLE tpc100g.lineitem, tpc100g.nation, tpc100g.region;
   ```
```markdown
3. View the current cache status:
```
   ```
   SHOW CACHED STATUS;
   ```
## Precautions

- Ensure that the table name is correctly specified when executing the `CACHE TABLE` command.