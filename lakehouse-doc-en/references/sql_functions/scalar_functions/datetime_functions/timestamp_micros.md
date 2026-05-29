### TIMESTAMP_MICROS 

#### Description

The `TIMESTAMP_MICROS` function is used to convert a `bigint` type value representing microseconds into a `timestamp` type timestamp. This function takes one input parameter and returns a corresponding timestamp result.

#### Parameters

* `micros`: A `bigint` type value representing the number of microseconds since the Unix epoch (00:00:00 UTC on January 1, 1970).

#### Return Value

Returns a `timestamp` type timestamp representing the specific date and time corresponding to the input parameter.

#### Example Usage

**Example 1**: Convert microsecond value to timestamp
```sql
SELECT TIMESTAMP_MICROS(1695364065L * 1000L * 1000L + 123456L) as res;
+----------------------------+
|            res             |
+----------------------------+
| 2023-09-22 14:27:45.123456 |
+----------------------------+
```
#### Precautions

* Please ensure that the input microsecond value is of type `bigint`, otherwise the conversion may fail.
* This function is only applicable for converting time points since the Unix epoch; for values beyond this range, the results may be inaccurate.
* In practical applications, it is recommended to use standard date-time formats for input and output to avoid potential parsing errors.

Through the above examples and explanations, you can better understand and use the `TIMESTAMP_MICROS` function to accurately convert microsecond values to corresponding timestamps.