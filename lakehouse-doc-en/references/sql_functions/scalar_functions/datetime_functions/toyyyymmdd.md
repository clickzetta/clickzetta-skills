# TOYYYYMMDD 

## Description

The `TOYYYYMMDD` function is used to convert different types of time expressions into a date format, specifically `YYYYMMDD`. This function accepts parameters of type `date` or `timestamp` and returns an integer type result.

## Syntax
```
TOYYYYMMDD(expr)
```
## Parameters

* `expr`: A time expression of type `date` or `timestamp`.

## Return Result

Returns an integer representing the input time expression in `YYYYMMDD` format.

## Example

1. Using the current timestamp:
   ```sql
   SELECT TOYYYYMMDD(now());
   ```
Assuming the current timestamp is `2022-01-01 15:00:00`, the return result is `20220101`.

2. Using a date in string format:
   ```sql
   SELECT TOYYYYMMDD('2023-04-15') as res;
   +----------+
   |   res    |
   +----------+
   | 20230415 |
   +----------+
   ```
3. Using Timestamps to Convert to Dates:
   ```sql
   SELECT TOYYYYMMDD(TIMESTAMP "2024-05-25 03:21:00") as res;
   +----------+
   |   res    |
   +----------+
   | 20240525 |
   +----------+
   ```

4. Use the current timestamp and format it as a date:
   ```sql
   SELECT TOYYYYMMDD(CURRENT_TIMESTAMP() - INTERVAL '1 day') as res ;
   +----------+
   |   res    |
   +----------+
   | 20250120 |
   +----------+
   ```
## Notes

* When the input time expression cannot be converted to a date, the function will return `NULL`.
* Please ensure that the input time expression is in the correct format, otherwise it may lead to incorrect results.

## Summary

The `TOYYYYMMDD` function provides a convenient way to convert different types of time expressions into date format. By using this function, users can easily obtain the integer representation of a date, making it convenient for date calculations and comparisons.