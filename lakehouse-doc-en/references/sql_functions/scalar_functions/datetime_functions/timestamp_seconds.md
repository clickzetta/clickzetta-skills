### TIMESTAMP\_SECONDS 

#### Description

The `TIMESTAMP_SECONDS` function is used to convert a number of seconds (`bigint` type) representing time into a timestamp (`timestamp` type). This function conveniently converts the number of seconds since the Unix epoch (00:00:00 UTC on January 1, 1970) into date and time format.

#### Syntax
```
timestamp_seconds(seconds)
```
#### Parameters

* `seconds`: A parameter of type `bigint`, representing the number of seconds since the Unix epoch.

#### Return Result

* Returns a result of type `timestamp`, representing the date and time corresponding to the input seconds.

#### Usage Example

1. Calculate the current Unix timestamp and convert it to timestamp format:
```sql
SELECT TIMESTAMP_SECONDS(UNIX_TIMESTAMP()) as res;
+---------------------+
|         res         |
+---------------------+
| 2025-01-21 16:04:50 |
+---------------------+
```
This will return the current date and time when the query is executed.

2. Convert a specific number of seconds to a timestamp:
```sql
SELECT TIMESTAMP_SECONDS(1695364065L) as res;
+---------------------+
|         res         |
+---------------------+
| 2023-09-22 14:27:45 |
+---------------------+
```
This will return `2023-09-22 14:27:45`, indicating the date and time corresponding to the input seconds.

3. Calculate the Unix timestamp for a specific date and time and convert it to timestamp format:
```sql
SELECT TIMESTAMP_SECONDS(UNIX_TIMESTAMP('2023-09-22 14:27:45')) as res;
+---------------------+
|         res         |
+---------------------+
| 2023-09-22 14:27:45 |
+---------------------+
```
This will return `2023-09-22 14:27:45`, which is the same as the input date and time.

By using the `TIMESTAMP_SECONDS` function, you can easily convert between different time formats and representations to better handle and analyze data.