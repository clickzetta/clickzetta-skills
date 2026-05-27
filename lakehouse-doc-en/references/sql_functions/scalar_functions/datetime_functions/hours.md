### HOURS
```sql
hours(expr)
```
#### Description
Returns the number of hours from the epoch (1970-01-01 00:00:00) to the specified timestamp.
#### Parameters
* `expr`: An expression of type date/timestamp_ltz/timestamp_ntz
#### Returns
* `bigint` type, representing the number of hours since the epoch.
#### Examples
```sql
SELECT hours(timestamp_ntz '1970-01-01 00:00:00');
-- Result: 0
```

```sql
SELECT hours(timestamp_ntz '2000-01-01 00:00:00');
-- Result: 262968
```

```sql
SELECT hours(timestamp_ntz '2020-08-09 03:04:05');
-- Result: 443595
```
