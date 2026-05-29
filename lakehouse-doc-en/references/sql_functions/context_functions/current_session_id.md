# CURRENT_SESSION_ID Function

```
current_session_id()
```

#### Description

The `CURRENT_SESSION_ID` function returns the Session ID of the current session.

#### Parameters

* No parameters.

#### Return Type

* Returns a `STRING` value representing the Session ID of the current session.

#### Examples

1. Get the current session ID

```sql
SELECT current_session_id();
+--------------------------------------+
| current_session_id()                 |
+--------------------------------------+
| 18ae19ca-8789-4029-93bd-512c6aebd3fa |
+--------------------------------------+
```
