### ADD\_DAYS 

####  Description

The `ADD_DAYS` function is used to add `numDays` days to the given date `startDate`, returning a new date. If the calculation result exceeds the date range supported by the system, it returns `null`.

#### Function Syntax
```
add_days(startDate, numDays)
```
#### Parameter Description

* `startDate`: Date type, represents the start date.
* `numDays`: Integer type, represents the number of days to add.

#### Return Result

Returns a new date, date type.

#### Usage Example

1. Example of adding days:
   ```sql
   SELECT add_days('2020-05-31', 10);
   +----------------------------+
   | add_days('2020-05-31', 10) |
   +----------------------------+
   | 2020-06-10                 |
   +----------------------------+
   ```
2. Example of Reducing Days:
   ```sql
   SELECT add_days('2020-05-31', -3);
   +----------------------------+
   | add_days('2020-05-31', -3) |
   +----------------------------+
   | 2020-05-28                 |
   +----------------------------+
   ```
3. Example of Cross-Year Date Calculation:
   ```sql
   SELECT add_days('2020-12-31', 365);
   +-----------------------------+
   | add_days('2020-12-31', 365) |
   +-----------------------------+
   | 2021-12-31                  |
   +-----------------------------+
   ```
4. Example of Exceeding Date Range:
   ```sql
   SELECT add_days('0001-01-01', 100000);
   +--------------------------------+
   | add_days('0001-01-01', 100000) |
   +--------------------------------+
   | 0274-10-17                     |
   +--------------------------------+
   ```
#### Precautions

* Ensure that the `startDate` parameter is in a valid date format, otherwise the function will return `null`.
* When the added days cause the result to exceed the date range supported by the system, the function will return `null`.