### weekday

### Description

The `weekday` function is used to calculate and return the day of the week for a given date (`date` type) or timestamp (`timestamp` type). This function is very useful for scenarios that require data processing or statistics based on the day of the week.

### Parameter Description

* `expr`: `date` or `timestamp_ltz` type, representing the date or timestamp for which the day of the week needs to be calculated.

### Return Result

Returns an integer representing the day of the week. Where 0 represents Monday, 1 represents Tuesday, and so on, with 6 representing Sunday.

### Usage Example

1. Calculate the day of the week for the current time:
   ```sql
   SELECT weekday(current_timestamp()) as res;
   ```
The result will return the day of the week when the query is executed.

2. Calculate the day of the week for a specific date:
   ```sql
   SELECT weekday('2022-03-31') as res;
   +-----+
   | res |
   +-----+
   | 3   |
   +-----+
   ```
3. Calculate which day of the week the timestamp belongs to:
   ```sql
   SELECT weekday(timestamp_ltz '2022-03-31 13:15:00')as res;
   +-----+
   | res |
   +-----+
   | 3   |
   +-----+
   ```
### Notes

* When the input date or timestamp is invalid, the `weekday` function will return an error.
* This function may have differences in the calculation of weekdays for different regions, please adjust according to the actual situation.

### Conclusion

The `weekday` function is a simple and practical tool that can help users quickly get the day of the week for a given date or timestamp. Through the above examples, users can better understand and use this function.