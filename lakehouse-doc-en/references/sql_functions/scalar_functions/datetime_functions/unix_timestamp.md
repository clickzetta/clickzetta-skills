### UNIX\_TIMESTAMP 

####  Description

The `UNIX_TIMESTAMP` function is used to obtain the UNIX timestamp of the current time or a specified time, which is the total number of seconds from 00:00:00 UTC on January 1, 1970, to the specified time. If no parameters are specified, it returns the UNIX timestamp of the current time by default.

#### Syntax
```
unix_timestamp([expr [, fmt]])
```
#### Parameter Description

* `expr`: Can be of type date, timestamp_ltz, or string, representing the time to be converted to a UNIX timestamp. If this parameter is not specified, the current time is used by default.
* `fmt`: String type, representing the format of the input time. If this parameter is not specified, the system's default time format will be used for parsing.

#### Return Result

Returns a value of type bigint, representing the UNIX timestamp.

#### Usage Example

1. Get the UNIX timestamp of the current time:
```
SELECT UNIX_TIMESTAMP() as res;
+------------+
|    res     |
+------------+
| 1737447675 |
+------------+
```
2. Get the UNIX timestamp for a specified time:
```
SELECT UNIX_TIMESTAMP('2022-02-23 10:00:00')as res;
+------------+
|    res     |
+------------+
| 1645581600 |
+------------+
```
3. Get the UNIX timestamp in a specified time format:
```
SELECT UNIX_TIMESTAMP('2022-02-23 10:00:00', 'yyyy-MM-dd HH:mm:ss')as res;
+------------+
|    res     |
+------------+
| 1645581600 |
+------------+
```

4. Convert string type time to UNIX timestamp:

```
SELECT UNIX_TIMESTAMP('2022-02-23 10:00:00', 'yyyy-MM-dd HH:mm:ss')as res;
+------------+
|    res     |
+------------+
| 1645581600 |
+------------+
```

5. Convert timestamp type time to UNIX timestamp:

```
SELECT UNIX_TIMESTAMP(TIMESTAMP "2022-02-23 10:00:00")as res;
+------------+
|    res     |
+------------+
| 1645581600 |
+------------+
```

6. Convert date type time to UNIX timestamp:

```
SELECT UNIX_TIMESTAMP(DATE '2022-02-23')as res;
+------------+
|    res     |
+------------+
| 1645545600 |
+------------+
```
#### Precautions

* When the input time format is incorrect or unrecognizable, the function will return NULL.
* If the specified time exceeds the time range supported by the system, the function will return NULL.
* When using this function, it is recommended to explicitly specify the format of the input time to avoid parsing errors caused by different system default time formats.