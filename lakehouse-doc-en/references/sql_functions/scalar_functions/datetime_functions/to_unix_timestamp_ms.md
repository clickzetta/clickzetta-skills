### TO_UNIX_TIMESTAMP_MS 

#### Description
The `TO_UNIX_TIMESTAMP_MS` function is used to convert various types of time expressions into a Unix timestamp (milliseconds). A Unix timestamp is the total number of milliseconds from 00:00:00 UTC on January 1, 1970, to the specified time. This function can handle multiple input formats, including strings, timestamps, etc.

#### Parameters
* `expr`: The input time expression, which can be a string, timestamp, etc.

#### Return Value
Returns a value of type `bigint`, representing the Unix timestamp (milliseconds) after converting the input time expression.

#### Usage Example

1. Convert from string to Unix timestamp (milliseconds):
```sql
SELECT TO_UNIX_TIMESTAMP_MS('2022-02-01 10:23:32.123');
-- Result: 1643682212123
```
In this example, the string `'2022-02-01 10:23:32.123'` is converted to a Unix timestamp (milliseconds).

2. Get the Unix timestamp (milliseconds) from the current time:
```sql
SELECT TO_UNIX_TIMESTAMP_MS(NOW());
-- Result: The result will vary depending on the time
```
In this example, the `NOW()` function is used to get the current time and convert it to a Unix timestamp (milliseconds).

3. Convert from string to Unix timestamp (milliseconds), considering time zone differences:
```sql
SELECT TO_UNIX_TIMESTAMP_MS('2022-02-01 10:23:32.123');
-- Result: 1643682212123
```

4. Convert from timestamp to Unix timestamp (milliseconds):

```sql
SELECT TO_UNIX_TIMESTAMP_MS(TIMESTAMP "2022-02-01 10:23:32.123");
-- Result: 1643682212123
```
In this example, the timestamp `TIMESTAMP "2022-02-01 10:23:32.123"` is converted to a Unix timestamp (milliseconds).

#### Notes
- The input time expression needs to conform to the supported format, otherwise, the conversion may fail.
- Time zone differences need to be considered during the conversion to ensure the accuracy of the result.
- Please ensure that the input parameters match the expected data types when using this function.