# SESSION_CONFIGS

#### Introduction

The `SESSION_CONFIGS` function returns a map of all system parameters in the current session, with both keys and values as strings. Its primary use is reading business parameters inside Dynamic Table parameterized definitions (for example, `SESSION_CONFIGS()['dt.args.bizdate']`). It can also be used to inspect the current session's system configuration.

#### Syntax

```sql
SESSION_CONFIGS()
```

#### Return Value

Returns `MAP<STRING, STRING>` containing all system parameters for the current session. Use the subscript operator `['key']` to read a specific parameter value; returns `NULL` if the key does not exist.

#### Examples

1. View all system parameters for the current session:

```sql
SELECT SESSION_CONFIGS();
```

Example result (a map):

```
{"cz.sql.adhoc.default.format":"ARROW","cz.sql.local.udf.enabled":"false",...}
```

2. Read a business date parameter in a Dynamic Table parameterized definition:

```sql
SELECT SESSION_CONFIGS()['dt.args.bizdate'];
```

This pattern is the core usage for Dynamic Table parameterization. See [Dynamic Table Parameters](../../dynamic-table-parameters.md) for details.

#### Notes

- The content returned by `SESSION_CONFIGS()` depends on the current session. Results may differ across sessions or at different execution times; do not hard-code specific values in examples.
- Reading a key that does not exist returns `NULL` without raising an error.
- When a Dynamic Table is refreshed, parameters injected via `ALTER DYNAMIC TABLE ... SET DT_ARGS(...)` appear in `SESSION_CONFIGS()` with the `dt.args.*` prefix, available for reference in SQL definitions.
