# CURRENT_SETTING

#### Introduction

The `CURRENT_SETTING` function reads the current value of a specified system parameter. If the parameter name does not exist, it returns an empty string rather than raising an error.

The difference from `SESSION_CONFIGS()`: `SESSION_CONFIGS()` returns a map of all configuration entries; `CURRENT_SETTING()` reads a single specified parameter value, suited for cases where only one configuration item needs to be queried.

#### Syntax

```Plain
CURRENT_SETTING(<setting_name>)
```

#### Parameters

`setting_name`: A string specifying the name of the system parameter to query. Returns an empty string if the parameter does not exist.

#### Return Value

Returns a string. If the parameter exists, returns its current value. If the parameter does not exist, returns an empty string `''`.

#### Examples

Query a parameter that does not exist to verify that an empty string is returned rather than an error:

```sql
SELECT CURRENT_SETTING('max_result_rows');
```

Result:

```
(empty string)
```

#### Related Documentation

- [SESSION_CONFIGS](session_configs.md)
