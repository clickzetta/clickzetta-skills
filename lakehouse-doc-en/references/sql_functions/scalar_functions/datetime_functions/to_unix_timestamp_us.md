### TO_UNIX_TIMESTAMP_US 
```
to_unix_timestamp_us(expr)
```
####  Description
The `TO_UNIX_TIMESTAMP_US` function is used to convert various types of time expressions into Unix timestamps (microseconds), which is the total number of microseconds from January 1, 1970, 00:00:00 UTC to the specified time.

#### Parameter Description
* `expr`: Timestamp expression, which can be a string, timestamp, etc.

#### Return Type
The return type is `BIGINT`.

#### Usage Example
1. Convert from string to Unix timestamp (microseconds):
```sql
SELECT TO_UNIX_TIMESTAMP_US('2022-02-01 10:23:32.123456');
-- Result: 1643682212123456
```
2. Get Unix timestamp (microseconds) from the current time:
```sql
SELECT TO_UNIX_TIMESTAMP_US(NOW());
-- Result: Current time's Unix timestamp (microseconds)
```
3. Convert from timestamp to Unix timestamp (microseconds):
```sql
SELECT TO_UNIX_TIMESTAMP_US(TIMESTAMP "2022-02-01 10:23:32.123456");
-- Result: 1643682212123456
```
4. Convert the current timestamp to Unix timestamp (microseconds) and add an offset:
```sql
SELECT TO_UNIX_TIMESTAMP_US(TIMESTAMP "2022-02-01 10:23:32.123456") + 3600000000;
-- Result: Adds 1 hour (3600000000 microseconds) to the current timestamp
```
#### Notes
- Please ensure that the input time expression format is correct, otherwise it may cause conversion failure.
- The Unix timestamp (microseconds) returned by this function can be used for calculating time differences, operations between timestamps, etc.