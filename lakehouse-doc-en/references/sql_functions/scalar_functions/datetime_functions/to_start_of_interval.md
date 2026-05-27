### TO_START_OF_INTERVAL
```sql
to_start_of_interval(ts, interval)
```

#### Function
Truncates the timestamp `ts` to the start of the specified `interval`. Note that when the `interval` is in minutes, it must be a divisor of 1 day (i.e., it should evenly divide into 1440 minutes).

#### Parameters
- `ts`: timestamp
- `interval`: interval_day_time/interval_year_month

#### Return Value
- `timestamp`

#### Example
```sql
> SELECT
  to_start_of_interval(ts, INTERVAL 5 MINUTE),
  to_start_of_interval(ts, INTERVAL 1 DAY)
FROM VALUES
  (TIMESTAMP '1933-06-22 04:44:08.999'),
  (TIMESTAMP '1970-12-31 04:59:59.999'),
  (TIMESTAMP '1996-03-31 07:03:33.123') t(ts);
1933-06-22 04:40:00     1933-06-22 00:00:00
1970-12-31 04:55:00     1970-12-31 00:00:00
1996-03-31 07:00:00     1996-03-31 00:00:00
```