## Description

List synonyms under the schema

## Syntax
```SQL
SHOW SYNONYMS [IN SCHEMA scname ] [WHRERE <expr>]
```
1. `IN schema_name`: Optional parameter, used to specify the schema name. With this parameter, users can view all synonyms under the specified schema.

2. `WHERE expr`: Optional parameter, allows users to filter based on the fields displayed by the `SHOW SYNONYMS` command. This parameter provides a more flexible query method, allowing filtering based on actual needs.

## Example

1. Filter by synonym name
```SQL
SHOW SYNONYMS WHERE     synonym_name = 'students_sy';
```
2. View synonyms under a specified schema

```SQL
  SHOW SYNONYMS IN public;
```