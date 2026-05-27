### Date and Time Formats

#### Overview

When handling and displaying date and time information, it is crucial to correctly format and parse this information. CZ provides a series of date and time format symbols to allow users to represent and process date and time data according to different needs.

#### Date and Time Format Symbols

| Symbol | Description | Supported Type | Example |
|:------:|:-----------:|:--------------:|:-------:|
| y   | Year | 4-digit number | 2022  |
| M   | Month | 1 or 2-digit number | 3; 03  |
| d   | Date | 1 or 2-digit number | 5; 05  |
| H   | Hour (24-hour format) | 1 or 2-digit number | 10; 23 |
| m   | Minute | 1 or 2-digit number | 5; 59  |
| s   | Second | 1 or 2-digit number | 8; 59  |
| S   | Millisecond/Microsecond | 1 to 6-digit number | 324123; 123456 |
| '  | Character literal | Text | 'yyyy' |

#### Detailed Explanation

1. Year (y)
   - `yyyy`: Represents a four-digit year, for example, 2022.

2. Month (M)
   - `M`: Represents a month without a leading zero.
   - `MM`: Represents a month with a leading zero, for example, 03 or 12.

3. Date (d)
   - `d`: Represents a date without a leading zero.
   - `dd`: Represents a date with a leading zero, for example, 05 or 20.

4. Hour (24-hour format, H)
   - `H`: Represents an hour without a leading zero.
   - `HH`: Represents an hour with a leading zero, for example, 01 or 23.

5. Minute (m)
   - `m`: Represents a minute without a leading zero.
   - `mm`: Represents a minute with a leading zero, for example, 04 or 59.

6. Second (s)
   - `s`: Represents a second without a leading zero.
   - `ss`: Represents a second with a leading zero, for example, 08 or 59.

7. Millisecond/Microsecond (S)
   - `S`: Represents milliseconds and microseconds, which can be 1 to 6 digits. From left to right, it is milliseconds (3 digits), microseconds (3 digits). Nanoseconds (3 digits) are ignored in CZ. If the number of digits in S is less than 6, the precision is reduced from the right. CZ currently only supports microsecond-level timestamp precision.

8. Character Literal (')
   - `'`: Used to insert text characters, for example, `'Hello World'`.

#### Examples

Here are some examples using different date and time formats:

1. `yyyy-MM-dd HH:mm:ss.SSSS`: 2022-01-10 10:05:02.123456
2. `yyyy/MM/dd HH:mm:ss.SSSS`: 2022/01/10 10:05:02.123456
3. `yyyy'year'MM'month'dd'day' HH'hour'mm'minute'ss'second'SSS'millisecond'`: 2022year01month10day 10hour05minute02second123millisecond
4. `'Today is y year MM month dd day d day' HH:mm:ss.SSSS`: Today is 2022year01month10day 5day 10:05:02.123456
5. `yyyy'Hello World'yMdH'-MM-dd HH:mm:ss.SSSS`: 2022Hello WorldyMdH-01-10 10:05:02.123456

With the above format symbols and examples, users can flexibly create and parse date and time strings as needed. Please note that when parsing time strings, each part will be parsed according to the requirements of the format symbols. If the input string does not match the specified format, the date and time information cannot be correctly parsed. Therefore, please ensure that the input string strictly follows the selected date and time format.