### DATE_FORMAT_pg 
```
date_format_pg(expr, fmt)
```
####  Description
The `date_format_pg` function is used to convert different types of time expressions into string form according to the specified format. This function is compatible with PostgreSQL database date formatting features.

#### Parameter Description
| Parameter | Type | Description |
| --- | --- | --- |
| expr | date/timestamp_ltz/string | The input time expression, which can be in the format of a string, timestamp, datetime, etc. |
| fmt | string | A string describing the format, refer to the PostgreSQL official documentation for specific formats. |

#### Supported Formats
Below are some of the supported formats and their descriptions:

| Format | Description |
| --- | --- |
| `HH` | Hour (12-hour format, 01-12) |
| `HH12` | Hour (12-hour format, 01-12) |
| `HH24` | Hour (24-hour format, 00-23) |
| `MI` | Minute (00-59) |
| `SS` | Second (00-59) |
| `MS` | Millisecond (000-999) |
| `US` | Microsecond (000000-999999) |
| `YYYY` | Year (4 or more digits) |
| `MM` | Month (01-12) |
| `DD` | Day of the month (01-31) |
| `D` | Day of the week, Sunday (1) to Saturday (7) |

#### Return Type
- string: The formatted string.

#### Usage Example
```sql
-- Convert a string type time expression to date format
SELECT date_format_pg('2022-05-01', 'YYYY-MM-DD');

-- Result: '2022-05-01'

-- Convert the current timestamp to a string with hours, minutes, and seconds
SELECT date_format_pg(TIMESTAMP "2022-05-01 12:34:56", 'YYYY-MM-DD HH24:MI:SS');

-- Result: '2022-05-01 12:34:56'

-- Convert the current time to ISO 8601 format
SELECT date_format_pg(TIMESTAMP "2022-05-01 12:34:56", 'YYYY-MM-DD"T"HH24:MI:SS.MS');

-- Result: '2022-05-01T12:34:56.MS'
```
#### Notes
- Please ensure that the format string in the `fmt` parameter is correct, otherwise the conversion result may not meet expectations.
- This function may behave differently under different regional settings, for example, the names of months and weekdays may change according to localization settings.
- For more supported formats and details, please refer to the [PostgreSQL official documentation](https://www.postgresql.org/docs/current/functions-formatting.html).