# DATE

`DATE` is a date data type that stores three parts: year, month, and day, without time or timezone information. It is suitable for storing date data unrelated to time, such as birthdays and event dates.

## Syntax

```Plain
DATE'yyyy-MM-dd'
```

## Parameters

| Parameter | Format | Description |
|------|------|------|
| `yyyy` | Four digits | Year, e.g. `2024` |
| `MM` | Two digits | Month, range 01 to 12 |
| `dd` | Two digits | Day, range 01 to 31 (depending on the month) |

## Examples

1. Use a DATE literal:

   ```SQL
   SELECT DATE'2024-01-15';
   ```

   Returns: `2024-01-15`

2. Convert a string to DATE:

   ```SQL
   SELECT CAST('2024-01-15' AS DATE);
   ```

   Returns: `2024-01-15`

3. Calculate the number of days between two dates:

   ```SQL
   SELECT DATEDIFF(DATE'2024-04-01', DATE'2024-03-15');
   ```

   Returns: `17`

4. Date addition/subtraction (using INTERVAL):

   ```SQL
   SELECT DATE'2024-01-15' + INTERVAL 30 DAY;
   ```

   Returns: `2024-02-14`

5. Convert DATE to TIMESTAMP:

   ```SQL
   SELECT CAST(DATE'2024-01-15' AS TIMESTAMP);
   ```

   Returns: `2024-01-14T16:00:00.000Z` (converted to UTC time; the timezone offset depends on the session timezone setting)

6. Invalid date conversion returns NULL:

   ```SQL
   SELECT CAST('2024-13-01' AS DATE);
   ```

   Returns: `NULL`

7. NULL value handling:

   ```SQL
   SELECT CAST(NULL AS DATE);
   ```

   Returns: `NULL`

## Notes

- `DATE` is a data type, not a function. Date literal syntax is `DATE'yyyy-MM-dd'`; do not write `DATE('2024-01-15')`.
- When the month or day is outside the valid range, CAST conversion returns NULL without raising an error.
- DATE does not include time information; to store time, use the `TIMESTAMP` type.
- When converting DATE to TIMESTAMP, the time part defaults to `00:00:00` and is converted according to the session timezone.
- Date comparisons can use `<`, `>`, `=` and other operators directly without additional conversion.
- Avoid using non-existent dates (such as `2024-02-30`); such values return NULL after conversion.
