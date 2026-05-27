### SUB\_DAYS 

#### Description

The DATE\_SUB function is used to calculate the date after subtracting a specified number of days from a given date. This is a very practical date calculation function that can help you easily handle date and time-related calculation issues.

#### Syntax
```sql
SUB_DAYS(startDate, numDays)
```
#### Parameters

* `startDate`: Start date, must use a valid date format (e.g., 'YYYY-MM-DD').
* `numDays`: Number of days to subtract, must be an integer.

#### Return Result

Returns a new date representing the date after subtracting `numDays` from `startDate`. If the result exceeds the system's date range, it returns null.

####  Example

1. Calculate the date 10 days before today:
```sql
SELECT SUB_DAYS(CURRENT_DATE(), 10);
```
2. Calculate the date 3 days before May 31, 2020:
```sql
SELECT SUB_DAYS('2020-05-31', 3) as res;
+------------+
|    res     |
+------------+
| 2020-05-28 |
+------------+
```
3. Calculate the date 20 days before January 1, 2025:
```sql
SELECT SUB_DAYS('2025-01-01', 20) as res;
+------------+
|    res     |
+------------+
| 2024-12-12 |
+------------+
```
4. Calculate the date 5 days after December 31, 2023:
```sql
SELECT SUB_DAYS('2023-12-31', 5) as res;
+------------+
|    res     |
+------------+
| 2023-12-26 |
+------------+
```
#### Precautions

* Ensure that the startDate parameter uses a valid date format, otherwise it may lead to inaccurate calculation results.
* If the calculation result exceeds the system's date range, the function will return null. Please ensure to handle this situation appropriately in actual applications.

By using the DATE\_SUB function, you can easily perform date calculations, thereby better managing and analyzing data related to dates and times.