### DAYOFYEAR


###  Description
The `DAYOFYEAR` function is used to calculate and return the day of the year for a given date (datetime). This function is particularly useful for date-type data, helping users quickly understand the progress of a specific date within the entire year.

### Parameter Description
- `expr`: The input parameter is data of type `date` or `timestamp_ltz`.

### Return Result
Returns an integer representing the day of the year for the given date. The result ranges from 1 to 365 (common year) or 366 (leap year).

### Usage Example
1. Calculate the current day of the year:
   ```sql
   SELECT DAYOFYEAR(CURRENT_TIMESTAMP());
   ```
The result will show the number of days the current date is in the current year.

2. Calculate which day of the year a specific date is:
   ```sql
   SELECT DAYOFYEAR('2023-02-10');
   ```
The result will return 41, indicating that February 10, 2023, is the 41st day of the year.

3. Calculate the number of days for dates in different years:
   ```sql
   SELECT DAYOFYEAR('2022-03-31'), DAYOFYEAR('2024-03-31');
   ```
The result will return two integers, 90 (March 31, 2022, is the 90th day of that year) and 91 (March 31, 2024, is the 91st day of that year because 2024 is a leap year).

4. Use the `DAYOFYEAR` function in a query combined with other conditions:
   ```sql
   SELECT * FROM orders WHERE DAYOFYEAR(order_date) BETWEEN 100 AND 120;
   ```
This query will return all order records where `order_date` is between the 100th and 120th day of the current year.

### Notes
- Ensure the date format entered is correct, otherwise it may cause the function to return errors or unexpected results.
- The determination of the current year is based on the current time in the time zone of the input date.