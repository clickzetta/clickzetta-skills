# TIMESTAMP\_NTZ

## Description

timestamp\_ntz, also known as timestamp without time zone, is a database data type used to store date and time values without time zone information. This means that the stored time values are absolute and do not consider time zone changes. Regardless of the user's time zone, the time displayed in a timestamp without time zone field is the same. When using the timestamp without time zone type, it is usually necessary for the application or user to manage time zone conversions themselves, as the database does not automatically handle time zone information. This type is suitable for scenarios where time zone differences do not need to be considered. timestamp\_ntz is equivalent to datetime in Mysql.

## Syntax
```SQL
TIMESTAMP_NTZ
```
**Description**

The `timestamp_ntz` type is currently supported by JDBC client version 1.4.0 and above JDBC JAR packages.

### timestamp\_ntz constant format
```SQL
TIMESTAMP_NTZ

timestampString
{ 'yyyy[...]' |
  'yyyy[...]-[M]M' |
  'yyyy[...]-[M]M-[d]d' |
  'yyyy[...]-[M]M-[d]d ' |
  'yyyy[...]-[M]M-[d]d[T][H]H[:]' |
  'yyyy[..]-[M]M-[d]d[T][H]H:[m]m[:]' |
  'yyyy[...]-[M]M-[d]d[T][H]H:[m]m:[s]s[.]' |
  'yyyy[...]-[M]M-[d]d[T][H]H:[m]m:[s]s.[ms][ms][ms][us][us][us]' }
```
* `yyyy`: A year with at least four digits.
* `[M]M`: A one or two-digit month between 01 and 12.
* `[d]d`: A one or two-digit day between 01 and 31.
* `H[H]`: A one or two-digit hour between 00 and 23.
* `m[m]`: A one or two-digit minute between 00 and 59.
* `s[s]`: A one or two-digit second between 00 and 59.
* `[ms][ms][ms][us][us][us]`: Up to 6 decimal places for seconds.
```SQL
SELECT TIMESTAMP_NTZ'2020-12-31';
+---------------------------+
| TIMESTAMP_NTZ'2020-12-31' |
+---------------------------+
| 2020-12-31 00:00:00       |
+---------------------------+
SELECT TIMESTAMP_NTZ'2021-7-1T8:43:28.123456' as res;
+----------------------------+
|            res             |
+----------------------------+
| 2021-07-01 08:43:28.123456 |
+----------------------------+
SELECT TIMESTAMP_NTZ'2021-7-1 8:43:28.123456' as res;
+----------------------------+
|            res             |
+----------------------------+
| 2021-07-01 08:43:28.123456 |
+----------------------------+
```
If the format in the input string is correct, it will be converted to a timestamp.

## Difference between timestamp_ntz and timestamp_ltz

timestamp_ntz (timestamp without time zone): This type of timestamp records the "wall clock" time, which means the time without considering any time zone information. All operations are performed without considering the time zone. If the output format includes a time zone, the UTC indicator (Z) will be displayed. This means that no matter where you are in the world, the time recorded by timestamp_ntz is the same.

timestamp_ltz (timestamp with local time zone): This type of timestamp stores UTC time internally and performs all operations based on the current session's time zone. This means that when you query a field of type timestamp_ltz, the time you see will be converted to the time of your current session's time zone. This allows users to see the time converted to their local time zone when working in globally distributed systems.

As shown below: The local client's time zone is UTC+00. timestamp_ltz will convert the input time zone to store UTC time internally. Since the client is also in the UTC+00 time zone, the queried time will be converted to UTC+00 time. However, timestamp_ntz does not consider any time zone, so the queried time will be the same regardless of the client's time zone.
```SQL
SELECT timestamp_ltz'2022-03-30 06:00:00+08',timestamp_ntz'2022-03-30 06:00:00+08';
+---------------------------------------+---------------------------------------+
| timestamp_ltz'2022-03-30 06:00:00+08' | timestamp_ntz'2022-03-30 06:00:00+08' |
+---------------------------------------+---------------------------------------+
| 2022-03-29 22:00:00                   | 2022-03-30 06:00:00                   |
+---------------------------------------+---------------------------------------+
```
## Constraints and Limitations

* Writing `timestamp_ntz` is not supported by the Python SDK

## Specific Case

1. Convert `timestamp_ntz` to `timestamp_ltz`
```SQL
SELECT cast(timestamp_ntz'2022-03-30 06:00:00' as timestamp_ltz);
+-------------------------------------------------------+
| CAST(timestamp_ntz'2022-03-30 06:00:00' AS timestamp) |
+-------------------------------------------------------+
| 2022-03-30 06:00:00                                   |
+-------------------------------------------------------+
```
```markdown
## 2. Convert timestmap_lt to timestmap_ntz
```
```SQL
SELECT cast(timestamp_ltz'2022-03-30 06:00:00+08' as timestamp_ntz);
+--------------------------------------------------------------+
| CAST(timestamp_ltz'2022-03-30 06:00:00+08' AS timestamp_ntz) |
+--------------------------------------------------------------+
| 2022-03-30 06:00:00                                          |
+--------------------------------------------------------------+
```
```markdown
3. Use the timestamp_ntz field data type when creating a table
```
```SQL
CREATE    TABLE timestamp_wihtout_timezone (col timestamp_ntz);
```
```markdown
4. Insert timestamp_ntz type data
```
```SQL
INSERT    INTO timestamp_wihtout_timezone
VALUES    (timestamp_ntz '2022-03-30 06:00:00');
```
5. Using Functions for Processing

```SQL
SELECT    year(timestamp_ntz '2022-03-30 06:00:00');
+--------------------------------------------+
| `year`(timestamp_ntz'2022-03-30 06:00:00') |
+--------------------------------------------+
| 2022                                       |
+--------------------------------------------+
SELECT    month(timestamp_ntz '2022-03-30 06:00:00');
+---------------------------------------------+
| `month`(timestamp_ntz'2022-03-30 06:00:00') |
+---------------------------------------------+
| 3                                           |
+---------------------------------------------+
```

