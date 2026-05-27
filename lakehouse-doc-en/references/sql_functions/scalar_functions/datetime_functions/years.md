### YEARS
```sql
years(expr)
```
#### Description
Returns the number of years from the epoch (1970-01-01 00:00:00) to the specified timestamp.
#### Parameters
* `expr`: An expression of type DATE / TIMESTAMP_LTZ / TIMESTAMP_NTZ
#### Returns
* `bigint` type, representing the number of years since the epoch.
#### Examples
```sql
SELECT years(timestamp_ntz '1970-01-01 00:00:00');
-- Result: 0
```

```sql
SELECT years(timestamp_ntz '2000-01-01 00:00:00');
-- Result: 30
```

```sql
SELECT years(timestamp_ntz '2020-08-09 03:04:05');
-- Result: 50
```
