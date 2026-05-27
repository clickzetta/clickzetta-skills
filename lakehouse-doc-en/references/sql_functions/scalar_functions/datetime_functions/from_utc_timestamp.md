### FROM_UTC_TIMESTAMP 
```sql
from_utc_timestamp(expr, timeZone)
```
####  Description
The FROM_UTC_TIMESTAMP function is used to convert a timestamp type data `expr` representing UTC time to a local timestamp in the specified time zone `timeZone`.

####  Description
- `expr`: A timestamp type data representing UTC time.
- `timeZone`: The target time zone, represented as a string.

#### Return Result
The converted local timestamp, of type timestamp_ltz.

#### Usage Example
1. Convert the UTC time '1970-01-01' to Beijing time:
```sql
SELECT from_utc_timestamp('1970-01-01', 'Asia/Shanghai');
1970-01-01 08:00:00
```

2. Convert multiple UTC timestamps to US Eastern Time:
```sql
SELECT from_utc_timestamp('2022-01-01 03:21:00', 'America/New_York');
SELECT from_utc_timestamp('2022-02-01 03:21:00', 'America/New_York');
2021-12-31 22:21:00 
2022-01-31 22:21:00    
```

3. Convert the current UTC time to Sydney, Australia time:

```sql
SELECT from_utc_timestamp(current_timestamp(), 'Australia/Sydney');
2024-04-08 06:32:21 
```

#### Precautions
- Ensure the input timestamp format is correct, otherwise, the conversion may fail.
- The timezone string should use the standard timezone representation, such as 'Asia/Shanghai' or 'America/New_York'. If the timezone string is incorrect, it may lead to unexpected conversion results.
- During the conversion process, pay attention to the impact of daylight saving time. Some countries and regions implement daylight saving time during specific periods, which may cause time deviations.