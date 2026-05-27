### DAYOFWEEK\_ISO 
```
dayofweek_iso(expr)
```
####  Description

The `DAYOFWEEK_ISO` function is used to calculate and return the day of the week (represented as an integer) for a given date (`date` or `timestamp_ltz` type). Monday corresponds to the number 1, and Sunday corresponds to the number 7.

#### Parameter Description

* `expr`: The input date or timestamp. This parameter accepts values of type `date` or `timestamp_ltz`.

#### Return Result

Returns an integer representing the day of the week for the given date. The range of the return result is from 1 to 7, where 1 represents Monday, 2 represents Tuesday, and so on, up to 7 representing Sunday.

#### Usage Example

1. Calculate the day of the week for the current date:
```
SELECT dayofweek_iso(CURRENT_TIMESTAMP());
```
2. Calculate the day of the week for a specific date:
```
SELECT dayofweek_iso('2022-03-31');
+-----------------------------+
| dayofweek_iso('2022-03-31') |
+-----------------------------+
| 4                           |
+-----------------------------+
```

3. Calculate the day of the week for a timestamp:
```
SELECT dayofweek_iso(TIMESTAMP "2022-03-31 03:21:00");
+-----+
| res |
+-----+
| 4   |
+-----+
```
#### Notes

* Please ensure that the input date or timestamp format is correct, otherwise the function may not execute properly.
* When the input timestamp does not have a date part (for example, only time), the function will calculate the day of the week based on the timezone information of the timestamp.