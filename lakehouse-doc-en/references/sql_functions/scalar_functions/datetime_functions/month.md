### MONTH 
```sql
MONTH(date)
```
####  Description
The MONTH function is used to extract the month part from a given date value and return the result as an integer.

#### Parameter Description
* **date** (date): The date value from which the month needs to be extracted.

#### Return Result
Returns an integer representing the month part of the date parameter.

####  Example
1. Extract the month from the current timestamp:
```sql
SELECT MONTH(CURRENT_TIMESTAMP());
```
2. Extract the month from a specified string format date:
```sql
SELECT MONTH('2022-04-01');
Result: 4
```


3. Extract the month from the current timestamp and compare it with the same month last year:
```sql
SELECT MONTH(CURRENT_TIMESTAMP()) - MONTH(CURRENT_TIMESTAMP()- INTERVAL '1 YEAR');
Result: 0
```


4. Extract the month from multiple date values in different formats and summarize the results:
```sql
SELECT MONTH('2022-04-01'), MONTH('01-APR-2022'), MONTH('2022/04/01');
4, null, null
```


#### Notes
* When the input parameter is not a valid date value, the MONTH function will return an error.
* Please ensure that the input date format matches the date format supported by the system to avoid parsing errors.