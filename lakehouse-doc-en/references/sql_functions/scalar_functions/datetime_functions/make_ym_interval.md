# MAKE_YM_INTERVAL

### Description

The `MAKE_YM_INTERVAL` function is used to create a time interval measured in years and months. This function can accept two parameters, which are the number of years and the number of months, both of which are optional. The created interval type is `interval year to month`.

### Parameters

* `years`: Integer type, representing the number of years.
* `months`: Integer type, representing the number of months.

### Return Type

Returns a value of type `interval year to month`.

###  Example

1. Create a time interval of 1 year:
   ```sql
   SELECT MAKE_YM_INTERVAL(1);
   +---------------------+
   | MAKE_YM_INTERVAL(1) |
   +---------------------+
   | 1-0                 |
   +---------------------+
   ```
2. Create a time period of 2 years and 3 months:
   ```sql
   SELECT MAKE_YM_INTERVAL(2, 3);
   +------------------------+
   | MAKE_YM_INTERVAL(2, 3) |
   +------------------------+
   | 2-3                    |
   +------------------------+
   ```
3. Create a time period that only includes 6 months:
   ```sql
   SELECT MAKE_YM_INTERVAL(0, 6);
   +------------------------+
   | MAKE_YM_INTERVAL(0, 6) |
   +------------------------+
   | 0-6                    |
   +------------------------+
   ```
### Notes

* When there is only one parameter, `months` defaults to 0.
* When `NULL` is used as a parameter, the function returns `NULL`. To create an interval with only months, use `MAKE_YM_INTERVAL(0, 6)` instead of `MAKE_YM_INTERVAL(NULL, 6)`.

