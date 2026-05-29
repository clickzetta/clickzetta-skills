### WEEKOFYEAR

###  Description
The `WEEKOFYEAR` function is used to calculate and return the week number of a given date (`date` or `timestamp_ltz` type) within the year. Note that this function defines the start of the week as Monday, and the first week of the year is the one that contains the first Thursday of that year (i.e., has four or more days in that year).

### Parameter Description
- `expr`: The input date or timestamp (`date` or `timestamp_ltz`).

### Return Type
- Returns an integer representing the week number of the given date within the year.

###  Example
1. Calculate the week number of a specific date:
```sql
SELECT WEEKOFYEAR('2022-03-31'); -- Result: 13
```
2. For the current timestamp, calculate the week number it falls in:
```sql
SELECT WEEKOFYEAR(CURRENT_TIMESTAMP()); -- The result will be calculated based on the current timestamp
```
### Notes
- This function has certain requirements for the input date format, ensure that the input date format is correct.
- When the input timestamp (`timestamp_ltz`) spans the first Thursday of the year, the returned result may vary.
- When performing date calculations, be aware of the impact of time zones, especially for dates and timestamps that span different time zones.

The above is the detailed help documentation for the `WEEKOFYEAR` function, including function description, parameter explanation, return type, usage examples, and notes. I hope this information helps you better understand and use this function.