## DATE_SUB Function

### Description

The `DATE_SUB` function calculates the date after adding or subtracting a specified number of days from a given date. This function returns a new date value. If the calculation result exceeds the system date range, it returns `NULL`.

### Syntax

```
date_sub(date, int)
```

### Parameters

* `date`: The date on which to perform the calculation, type is `DATE`.
* `int`: The number of days to add or subtract, type is integer.

### Return Result

Returns a new date value of type `DATE`.

### Examples

The following examples demonstrate how to use the `DATE_SUB` function for date calculations:

1. Calculate the date 3 days before May 31, 2020:

   ```sql
   SELECT date_sub('2020-05-31', 3);
   ```

   Result:

   ```
   2020-05-28
   ```

2. Calculate the date 1 day before February 29, 2020.

   ```sql
   SELECT date_sub('2020-02-29', 1);
   ```

   Result:

   ```
   2020-02-28
   ```

Please note that the `DATE_SUB` function only applies to columns of date type. If the input parameter type is incorrect, an error will be returned.
