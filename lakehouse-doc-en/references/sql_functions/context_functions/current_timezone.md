# CURRENT_TIMEZONE

#### Introduction

The `CURRENT_TIMEZONE` function returns the timezone setting of the current database session. It takes no parameters and returns a string representing the timezone name of the current session (for example, `Asia/Shanghai`). The default timezone is determined by system configuration and can be changed with the `SET` command.

#### Syntax

```sql
CURRENT_TIMEZONE()
```

#### Return Value

`CURRENT_TIMEZONE` returns a string representing the current session's timezone setting, in IANA timezone name format (for example, `Asia/Shanghai`).

#### Examples

1. Query the timezone setting of the current session:

```sql
SELECT CURRENT_TIMEZONE();
```

   Result:

   ```
   Asia/Shanghai
   ```
