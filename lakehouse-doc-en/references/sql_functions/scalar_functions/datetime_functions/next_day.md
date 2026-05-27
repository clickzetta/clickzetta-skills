### NEXT_DAY Function

```sql
next_day(start_date, day_of_week)
```

#### Description

Returns the date of the first occurrence of day_of_week after start_date.

#### Parameters

* `start_date`: The starting date. Supports STRING, DATE, and TIMESTAMP types.
* `day_of_week`: STRING type, representing the day of the week. The following formats are supported (case-insensitive):
  * 2-letter abbreviations: SU, MO, TU, WE, TH, FR, SA
  * 3-letter abbreviations: SUN, MON, TUE, WED, THU, FRI, SAT
  * Full names: SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY

#### Returns

DATE type.

#### Examples

1. Find the next Tuesday:

    ```sql
    SELECT next_day('2015-01-14', 'TU');
    -- Result: 2015-01-20
    ```

2. Using the full name:

    ```sql
    SELECT next_day('2015-01-14', 'WEDNESDAY');
    -- Result: 2015-01-21
    ```

3. Timestamp input is supported (only the date portion is returned):

    ```sql
    SELECT next_day('2015-07-23 12:12:12', 'Mon');
    -- Result: 2015-07-27
    ```

#### Notes

* When any parameter is NULL, the result is NULL.
* When day_of_week is not a valid day-of-week name, the result is NULL.
* When start_date is not a valid date format, the result is NULL.
* day_of_week is case-insensitive.
