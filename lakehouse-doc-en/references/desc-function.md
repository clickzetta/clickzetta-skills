# DESC FUNCTION

The `DESCRIBE FUNCTION` command is used to view detailed information about a created function, including its name, parameters, return type, function body, and more.

## Syntax

```sql
DESC[RIBE] FUNCTION [EXTENDED] [schema_name.]<function_name>;
```

## Parameter Description

| Parameter | Description |
|---|---|
| `DESC` / `DESCRIBE` | Both are equivalent and can be used interchangeably |
| `EXTENDED` | Optional. Retrieves extended information about the function, including comment, determinism, data access properties, owner, and creation time |
| `function_name` | The name of the function. If the function resides in a specific schema, use the `schema_name.function_name` format |

## Usage Examples

### Example 1: View basic function information

```sql
DESC FUNCTION my_schema.calculate_total;
```

### Example 2: View extended function information

```sql
DESC FUNCTION EXTENDED my_schema.calculate_total;
```

## Related Documentation

- [CREATE FUNCTION](create-sql-function.md)
- [DROP FUNCTION](drop-function.md)
- [SHOW FUNCTIONS](show-functions.md)
