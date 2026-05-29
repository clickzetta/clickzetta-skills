### CONVERT_TIMEZONE

####  Description
The `CONVERT_TIMEZONE` function is used to convert a specified timestamp from one time zone to another. This function can handle different types of time format inputs and automatically perform type conversion when necessary.

#### Syntax
```sql
CONVERT_TIMEZONE(source_tz, target_tz, ts)
CONVERT_TIMEZONE(target_tz, ts)
```
- `source_tz` string : Original time zone. If only two parameters are provided, the current session's time zone is used as the default original time zone.
- `target_tz` string : Target time zone.
- `ts` int or timestamp : Timestamp. If it is an integer type, the function will automatically convert it to a timestamp type.

#### Return Value
Converted timestamp.

#### Example 
```sql
-- Example 1: Convert timestamp from Moscow timezone to Los Angeles timezone
SELECT CONVERT_TIMEZONE('Europe/Moscow', 'America/Los_Angeles', '2022-01-01 00:00:00');

-- Return result: 2021-12-31 13:00:00

-- Example 2: Convert the current Brussels timezone timestamp to the target timezone
SELECT CONVERT_TIMEZONE('Europe/Brussels', 'Asia/Shanghai', '2022-03-23 00:00:00');

-- Return result: 2022-03-23 07:00:00

-- Example 3: Provide only the target timezone, convert the current session timezone timestamp to Tokyo timezone
SELECT CONVERT_TIMEZONE('Asia/Tokyo', 1674681600);

-- Return result: 2023-01-26 06:20:00

-- Example 4: Convert integer type timestamp from Beijing time to UTC time
SELECT CONVERT_TIMEZONE('UTC','Asia/Shanghai', 1674681600);

-- Return result: 2023-01-26 13:20:00
```
#### Notes
- Please ensure that the input timezone name is valid, otherwise the function will return an error.
- When the input timestamp format is incorrect or unrecognizable, the function will automatically attempt type conversion.
- If the input timestamp is already in the target timezone, the function will directly return that timestamp.

By using the `CONVERT_TIMEZONE` function, you can easily convert timestamps between different timezones, ensuring the accuracy and consistency of the data.