### MONTHS_BETWEEN Function

```sql
months_between(timestamp1, timestamp2[, roundOff])
```

#### Description

Returns the number of months between two dates. If timestamp1 is later than timestamp2, the result is positive; otherwise, it is negative.

The difference in the time portion (hours, minutes, seconds) is calculated based on 31 days per month. If the day of timestamp1 and timestamp2 are the same (e.g., both are the 5th), or if both are the last day of their respective months, the time portion is ignored.

#### Parameters

* `timestamp1`: The first date/timestamp. Supports STRING, DATE, and TIMESTAMP types.
* `timestamp2`: The second date/timestamp. Supports STRING, DATE, and TIMESTAMP types.
* `roundOff` (optional): BOOLEAN type. When true (default), the result is rounded to 8 decimal places; when false, the full precision is returned.

#### Returns

DOUBLE type.

#### Examples

1. Basic usage (default roundOff=true, 8 decimal places):

    ```sql
    SELECT months_between('1997-02-28 10:30:00', '1996-10-30');
    -- Result: 3.94959677
    ```

2. Disable rounding to return full precision:

    ```sql
    SELECT months_between('1997-02-28 10:30:00', '1996-10-30', false);
    -- Result: 3.9495967741935485
    ```

3. When both dates are month-end, the time portion is ignored:

    ```sql
    SELECT months_between('2002-03-31 10:30:00', '2002-02-28');
    -- Result: 1 (Feb 28 is the last day of February, Mar 31 is the last day of March)
    ```

#### Notes

* When any parameter is NULL, the result is NULL.
* When the day of both dates is the same, or both are month-end, the time portion is ignored and the result is an integer number of months.
* The time portion difference is converted based on 31 days per month (i.e., 31x24x3600 seconds).
