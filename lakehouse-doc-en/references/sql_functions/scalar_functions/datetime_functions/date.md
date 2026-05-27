### DATE 

####  Description

The DATE function is used to convert different types of date expressions into the date type, i.e., DATE type. It can handle various input formats, including strings, time, timestamps, etc. The DATE function has the same functionality as CAST(expr as DATE).

#### Supported Parameters

* expr: Can be a string, time, timestamp, or other expressions that can be converted into a date type.

#### Return Result

* Returns a result of date type, formatted as 'YYYY-MM-DD'.

#### Usage Example

1. String to date:
```sql
SELECT DATE('2022-01-01');
-- Result: 2022-01-01
```
```sql
SELECT DATE('2022/01/01'); The required format must be in YYYY-MM-DD format
-- Result: null
```
2. Time to Date:
```sql
SELECT DATE('22:12:30'); The required format must be in YYYY-MM-DD format
-- Result: null
```
```sql
SELECT DATE(TIMESTAMP "2022-01-01 22:12:30");
-- Result: 2022-01-01
```
#### Notes

* When the input string cannot be recognized as a valid date, the DATE function will return NULL.
* During the conversion process, the DATE function will automatically ignore the timezone information in the input expression and only retain the date part.
* If the input time exceeds the time range supported by the database, it may cause the conversion to fail or return unexpected results.