### YEAROFWEEK 
```
yearofweek(expr)
```
####  Description

The YEAROFWEEK function is used to return the ISO week-numbered year corresponding to a given date (expr). The ISO week-numbered year is calculated according to the international standard ISO 8601, which sets the first day of each week as Monday.

#### Parameter Description

* expr: The input date or timestamp, of type date or timestamp_ltz.

#### Return Result

Returns an integer value representing the ISO week-numbered year of the given date.

####  Example

1. Get the ISO week-numbered year based on the current time:
```
SELECT YEAROFWEEK(NOW()) as res;
+------+
| res  |
+------+
| 2025 |
+------+
```
2. Calculate the ISO week number year for a specified date:
```
SELECT YEAROFWEEK('2022-03-31')as res;
+------+
| res  |
+------+
| 2022 |
+------+
```
3. Calculate the ISO week number year for a given timestamp:
```
SELECT YEAROFWEEK(TIMESTAMP "2022-03-31 03:21:00")as res;
+------+
| res  |
+------+
| 2022 |
+------+
```
4. Calculate and compare the ISO week number years of two different dates:
```
SELECT YEAROFweek('2022-03-31') AS year1, YEAROFweek('2023-03-31') AS year2;
+-------+-------+
| year1 | year2 |
+-------+-------+
| 2022  | 2023  |
+-------+-------+
```