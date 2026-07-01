# CURRENT_DATABASE

#### Introduction

The `CURRENT_DATABASE` function returns the default Schema name of the current session. It takes no parameters and returns a string value.

> ⚠️ **Note**: Singdata Lakehouse has no separate Database tier. `CURRENT_DATABASE()` actually returns the current Schema name and is equivalent to `CURRENT_SCHEMA()`.

#### Syntax

```sql
CURRENT_DATABASE()
```

#### Return Value

`CURRENT_DATABASE` returns a string representing the default Schema name of the current session.

#### Examples

1. Query the default Schema name of the current session:

```sql
SELECT CURRENT_DATABASE();
```

   Example result:

   ```
   semantic_model_test
   ```
