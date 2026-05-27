### RAISE_ERROR Function

```
raise_error(message)
```

#### Description

The `RAISE_ERROR` function throws a runtime error during query execution and aborts the query. This function accepts an error message string as a parameter. When the function is executed, it throws an exception and displays the specified error message. It is often used in combination with the `IF` function to terminate query execution when specific conditions are met.

#### Parameters

* `message`: `STRING` type, the error message content. If the parameter is `NULL`, "null message" is displayed.

#### Return Type

* This function does not return a normal value.
* Throws an exception and aborts the query upon execution.
* The error message includes the provided `message` parameter.

#### Notes

* This function aborts query execution and should be used with caution.
* When used in production environments, ensure it is only triggered in necessary validation scenarios.
* Error messages should be clear and explicit for easier troubleshooting.
* A `NULL` parameter will display "null message"; avoid passing `NULL`.

#### Examples

1. Combined with IF: conditional error checking

```sql
SELECT IF(COUNT(*) > 0, raise_error('error_result'), 6666)
FROM (SELECT 1 WHERE 1 = 0);
+---------------------------------------------------------+
| IF(COUNT(*) > 0, raise_error('error_result'), 6666)     |
+---------------------------------------------------------+
| 6666                                                    |
+---------------------------------------------------------+
```

2. Using in CASE WHEN

```sql
SELECT
  CASE
    WHEN status = 'active' THEN 'Active'
    WHEN status = 'inactive' THEN 'Inactive'
    ELSE raise_error('Unknown status: ' || status)
  END as status_label
FROM user_status;
```
