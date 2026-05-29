### EXTRACT

####  Description
The extract function `EXTRACT(field FROM source)` is used to extract the specified `field` value from the given `source`. This function can handle different types of date-time expressions, including strings, timestamps, etc.

#### Parameter Description
- `field` (keyword): The date-time field to be extracted, with the following options:
  - `YEAR`, `(Y, YEARS, YR, YRS)` - Year
  - `QUARTER`, `(QTR)` - Quarter (1 - 4)
  - `MONTH`, `(MON, MONS, MONTHS)` - Month (1 - 12)
  - `WEEK`, `(W, WEEKS)` - Indicates the week number of the year. Note that the week calculation starts on Monday, and the first week of the year is the first week with more than three days in that year. In the ISO week date system, the first few days of January may belong to the 52nd or 53rd week of the previous year, and similarly, the last few days of December may belong to the 1st week of the next year. For example, 2005-01-02 is the 53rd week of 2004, and 2012-12-31 is the 1st week of 2013.
  - `DAY`, `(D, DAYS)` - Day of the month (1 - 31)
  - `DAYOFWEEK`, `(DOW)` - Day of the week, 1 corresponds to Sunday, 7 corresponds to Saturday
  - `DAYOFWEEK_ISO`, `(DOW_ISO)` - Day of the week based on ISO 8601 standard, 1 corresponds to Monday, 7 corresponds to Sunday
  - `DAYOFYEAR`, `(DOY)` - Day of the year (1 - 365/366)
  - `HOUR`, `(H, HOURS, HR, HRS)` - Hour (0 - 23)
  - `MINUTE`, `(M, MIN, MINS, MINUTES)` - Minute (0 - 59)
  - `SECOND`, `(S, SEC, SECONDS, SECS)` - Second (0 - 59)
- `source` (date/timestamp): The input date-time expression, which can be a string, timestamp, etc.

#### Return Result
The return result is an integer (int).

####  Example
The following is an example of using the `EXTRACT` function:
```sql
-- Extract the year from a string type timestamp
SELECT EXTRACT(YEAR FROM TIMESTAMP '2019-08-12 01:00:00.123456');
-- Result: 2019

-- Extract the week number of the year from a string type timestamp
SELECT EXTRACT(WEEK FROM TIMESTAMP '2019-08-12 01:00:00.123456');
-- Result: 33

-- Extract the day of the month from a string type date
SELECT EXTRACT(DAY FROM DATE '2019-08-12');
-- Result: 12

-- Extract the quarter from the current timestamp
SELECT EXTRACT(QUARTER FROM CURRENT_TIMESTAMP());
-- Result: depends on the current date

-- Extract the day of the week from a string type date (based on ISO 8601 standard)
SELECT EXTRACT(DAYOFWEEK_ISO FROM DATE '2019-08-12');
-- Result: 1
```
Through the above examples, you can see the application of the `EXTRACT` function in different scenarios. This function can conveniently extract the required date and time fields from various input formats, facilitating further data analysis and processing.