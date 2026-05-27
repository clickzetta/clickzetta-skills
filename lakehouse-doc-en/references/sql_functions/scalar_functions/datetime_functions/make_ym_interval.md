### MAKE\_YM\_INTERVAL

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
   SELECT MAKE_YM_INTERVAL(NULL, 6);
   +---------------------------+
   | MAKE_YM_INTERVAL(NULL, 6) |
   +---------------------------+
   | null                      |
   +---------------------------+
   ```
### Notes

* When there is only one parameter, the system defaults the year to 1.
* When `NULL` is used as a parameter, it means that the parameter is not involved in the calculation of the time interval.

