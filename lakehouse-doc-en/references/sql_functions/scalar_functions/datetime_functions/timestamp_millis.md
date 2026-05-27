### TIMESTAMP\_MILLIS 
```sql
timestamp_millis(millis)
```
####  Description

The TIMESTAMP\_MILLIS function is used to convert the number of milliseconds since the Unix epoch (00:00:00 UTC on January 1, 1970) into a timestamp format.

#### Parameter Description

* *millis*: bigint type, representing the number of milliseconds since the Unix epoch.

#### Return Result

Returns a value in timestamp format, representing the exact date and time corresponding to the input milliseconds.

#### Usage Example

1. Convert the current time's milliseconds into timestamp format:
```sql
SELECT TIMESTAMP_MILLIS(UNIX_TIMESTAMP() * 1000) as res;
+---------------------+
|         res         |
+---------------------+
| 2025-01-21 16:02:51 |
+---------------------+
```
2. Convert specific milliseconds to a timestamp and display the result:
```sql
SELECT TIMESTAMP_MILLIS(1695364065000 + 123456) as res;
+-------------------------+
|           res           |
+-------------------------+
| 2023-09-22 14:29:48.456 |
+-------------------------+
```
3. Convert the past time in milliseconds to a timestamp and compare it with the current timestamp:
```sql
 SELECT TIMESTAMP_MILLIS(1623370800000)as res1, CURRENT_TIMESTAMP() as res2;
+---------------------+----------------------------+
|        res1         |            res2            |
+---------------------+----------------------------+
| 2021-06-11 08:20:00 | 2025-01-21 16:04:16.042245 |
+---------------------+----------------------------+
```