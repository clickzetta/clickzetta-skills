### QUARTER

###  Description

The DATE\_QUARTER function is used to obtain the quarter information of a specified date value. The year is divided into four periods, each quarter containing three months. This function converts the input date value to the corresponding quarter and returns an integer representing the quarter.

### Syntax
```
QUARTER(date)
```
#### Parameter Description

* **date** (date): The date type from which the quarter needs to be extracted.

### Return Result

Returns an integer representing the quarter of the input date. 1 represents the first quarter (January-March), 2 represents the second quarter (April-June), 3 represents the third quarter (July-September), and 4 represents the fourth quarter (October-December).

### Example

Here are some examples of using the QUARTER function:

1. Calculate the quarter of the current date:
```sql
SELECT QUARTER(CURRENT_TIMESTAMP()) as res;
+-----+
| res |
+-----+
| 1   |
+-----+
```
2. Calculate the quarter of a specified date:
```sql
SELECT QUARTER(date'2022-12-31') as res;
+-----+
| res |
+-----+
| 4   |
+-----+
```
### Notes

* The input date value must be in a valid date format, otherwise, the function will fail to execute.
* If the input date value is the current time or a future date, the returned quarter information is still valid.