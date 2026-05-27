### TIMESTAMPADD 

#### Description
The TIMESTAMPADD function (alias: DATEADD) is used to add or subtract a specified number (count) of units (unit) to a given timestamp (ts). If count is positive, the corresponding units are added to the timestamp; if count is negative, the corresponding units are subtracted from the timestamp.

#### Supported Time Units
The time units (unit) can take the following keywords (case insensitive):
- MICROSECOND
- MILLISECOND
- SECOND
- MINUTE
- HOUR
- DAY
- DAYOFYEAR
- WEEK
- MONTH
- QUARTER
- YEAR

#### Function Parameters
- unit: timestamp_ltz type, representing the time unit to be added or subtracted.
- count: bigint type, representing the number to be added or subtracted.
- ts: timestamp_ltz type, representing the current timestamp.

#### Return Value
Returns a new timestamp (timestamp_ltz).

####  Example
1. Add 1 year to the timestamp '2020-10-10 01:02:03':
   ```sql
   SELECT TIMESTAMPADD(YEAR, 1, '2020-10-10 01:02:03');
   ```
Result: `2021-10-10 01:02:03`

2. Decrease 30 minutes from the timestamp '2020-10-10 01:02:03':
   ```sql
   SELECT TIMESTAMPADD(MINUTE, -30, '2020-10-10 01:02:03');
   ```
Result: `2020-10-10 00:32:03`

3. Add 100 days to the timestamp '2021-01-01 12:00:00':
   ```sql
   SELECT TIMESTAMPADD(DAY, 100, '2021-01-01 12:00:00');
   ```
Result: `2021-04-10 12:00:00`

4. Add 2 months to the timestamp '2020-10-10 01:02:03':
   ```sql
   SELECT TIMESTAMPADD(MONTH, 2, '2020-10-10 01:02:03');
   ```
Result: `2020-12-10 01:02:03`

5. Add 1 quarter to the timestamp '2020-10-10 01:02:03':
   ```sql
   SELECT TIMESTAMPADD(QUARTER, 1, '2020-10-10 01:02:03');
   ```
Result: `2021-01-10 01:02:03`

By using the TIMESTAMPADD function, you can easily add or subtract from a timestamp to meet different business needs.