# TIMESTAMP

The `TIMESTAMP` type is used to represent dates and timestamps, and can include timezone information. By default, timestamps are represented as local time (`TIMESTAMP_LTZ`). All operations are performed in the current session's timezone, and the output results are based on the timezone of the current Lakehouse service. Users can input timestamps in various formats, which are automatically converted to the `TIMESTAMP` type. The output result is in string format, with the format `'yyyy-MM-dd HH:mm:ss'`. If the user input includes milliseconds, the output result will also include milliseconds. The maximum precision supported is up to microseconds (us), and the precision depends on the precision of the timestamp at the time of writing.

## Syntax
```
TIMESTAMP | TIMESTAMP_LTZ
```
## Example
1. Using the default timestamp format:
```
SELECT TIMESTAMP '2022-12-31 00:00:00';
SELECT TIMESTAMP_LTZ '2022-12-31 00:00:00';
```

2. Using Different Formats of Timestamps: {#using-different-formats-of-timestamps}

```
SELECT TIMESTAMP '2022-12-31 00:00:00.123'; -- Includes milliseconds
+------------------------------------+
| TIMESTAMP'2022-12-31 00:00:00.123' |
+------------------------------------+
| 2022-12-31 00:00:00.123            |
+------------------------------------+
SELECT TIMESTAMP '2022-12-31T00:00:00.123Z'; -- ISO 8601 format, includes timezone information
+-------------------------------------+
| TIMESTAMP'2022-12-31T00:00:00.123Z' |
+-------------------------------------+
| 2022-12-31 08:00:00.123             |
+-------------------------------------+
```
3. Convert string to timestamp type:
```
SELECT CAST('2022-12-31 00:00:00' AS TIMESTAMP);
SELECT CAST('2022-12-31 00:00:00' AS TIMESTAMP_LTZ);
```
4. Using Different Precision Options:
```
SELECT TIMESTAMP  '2022-12-31 00:00:00.123456'; -- Microsecond precision
SELECT TIMESTAMP  '2022-12-31 00:00:00.123'; -- Millisecond precision
SELECT TIMESTAMP  '2022-12-31 00:00:00'; -- Second precision
```
## Notes
- When performing timestamp conversion, please be aware that time zone differences may cause discrepancies.
- Ensure that the input timestamp format matches the format supported by the system to avoid errors.