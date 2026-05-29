### TRUNC 
```
trunc(expr, fmt)
```
####  Description
The TRUNC function is used to truncate the date expression `expr` according to the specified `fmt` format, returning a new date.
#### Parameter Description
* **expr** (date): The date expression to be truncated.
* **fmt** (string): A string used to specify the truncation precision, case insensitive. Valid values are as follows:
	+ 'YEAR', 'YYYY', 'YY': Truncate to the first day of the year in which `expr` is located (January 1st).
	+ 'QUARTER': Truncate to the first day of the quarter in which `expr` is located.
	+ 'MONTH', 'MM', 'MON': Truncate to the first day of the month in which `expr` is located.
	+ 'WEEK': Truncate to the Monday of the week in which `expr` is located.
#### Return Result
Returns a date value representing the date truncated according to the specified `fmt`.
#### Usage Example
```sql
-- Truncate the date to the first day of the year
SELECT trunc('2022-02-03', 'YEAR'); -- Result is 2022-01-01

-- Truncate the date to the first day of the quarter
SELECT trunc('2022-02-03', 'QUARTER'); -- Result is 2022-01-01

-- Truncate the date to the first day of the month
SELECT trunc('2022-02-03', 'MONTH'); -- Result is 2022-02-01

-- Truncate the date to the Monday of the week
SELECT trunc('2022-02-03', 'WEEK'); -- Result is 2022-01-31

-- Truncate the date to the first day of the quarter and return the result as a string
SELECT trunc('2022-02-03', 'QUARTER') AS quarter_start; -- Result is "2022-01-01"

-- Truncate the date to the first day of the month and convert to time format
SELECT trunc('2022-02-03', 'MONTH') AS month_start_time; -- Result is "2022-02-01 00:00:00"
```
#### Notes
* When expr is not a valid date expression, the TRUNC function will return NULL.
* When the fmt parameter is incorrect, the TRUNC function will return an error. Please ensure to use a valid fmt value.