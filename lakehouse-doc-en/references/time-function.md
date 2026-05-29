### Date and Time Format Description

#### Overview

When handling and displaying date and time information, we usually need to organize and format this information according to a certain format. This document provides a set of commonly used date and time format symbols, along with their meanings, formats, and examples, to help you better understand and use these symbols.

#### Detailed Explanation of Format Symbols

| Symbol | Description   | Format Example  | Example Value  |
|--------|---------------|-----------------|----------------|
| G      | Era           | AD; Anno Domini | AD            |
| y      | Year          | year            | 2020; 20       |
| D      | Day of the year | number(3)     | 189            |
| M      | Month         | month           | 7; 07; Jul; July |
| d      | Day of the month | number(2)    | 28             |
| Q      | Quarter       | number/text     | 3; 03; Q3; 3rd quarter |
| E      | Day of the week | text          | Tue; Tuesday   |
| a      | AM/PM         | am-pm           | PM             |
| h      | Hour (12-hour clock) | number(2) | 12             |
| K      | Hour in AM/PM (0-11) | number(2) | 0              |
| k      | Hour (24-hour clock) | number(2) | 0              |
| H      | Hour (24-hour clock) | number(2) | 0              |
| m      | Minute        | number(2)       | 30             |
| s      | Second        | number(2)       | 55             |
| S      | Millisecond/Microsecond | fraction | 978         |
| V      | Time zone ID  | zone-id         | America/Los_Angeles; Z; -08:30 |
| z      | Time zone name | zone-name      | Pacific Standard Time; PST |
| O      | Localized time zone offset | offset-O | GMT+8; GMT+08:00; UTC-08:00; |
| X      | Time zone offset | offset-X     | Z; -08; -0830; -08:30; -083015; -08:30:15; |
| Z      | Time zone offset | offset-Z     | +0000; -0800; -08:00; |
| ‘‘     | Single quote  | literal         | ’              |

#### Examples of Symbol Usage

- Year:
  - `yyyy`: Four-digit year representation, e.g., 2022.
  - `yy`: Two-digit year representation, e.g., 22.

- Month:
  - `M`: Single-digit month representation, e.g., 3, 12.
  - `MM`: Two-digit month representation, e.g., 03, 12.

- Day of the month:
  - `d`: Single-digit day of the month representation, e.g., 5, 20.
  - `dd`: Two-digit day of the month representation, e.g., 05, 20.

- Hour, 24-hour clock:
  - `H`: Single-digit hour in 24-hour clock representation, e.g., 1, 23.
  - `HH`: Two-digit hour in 24-hour clock representation, e.g., 01, 23.

- Minute:
  - `m`: Single-digit minute representation, e.g., 4, 59.
  - `mm`: Two-digit minute representation, e.g., 04, 59.

- Second:
  - `s`: Single-digit second representation, e.g., 8, 59.
  - `ss`: Two-digit second representation, e.g., 08, 59.

- Millisecond/Microsecond:
  - `S`: Supports 1-9 digits, representing milliseconds (first 3 digits), microseconds (middle 3 digits), and nanoseconds (last 3 digits). Singdata currently only supports microsecond precision, so nanoseconds will be discarded when parsing time strings, and the nanosecond part will be set to zero when generating time strings. If less than 9 digits, precision decreases from right to left.

#### Examples

Here are some examples of date and time formats using the above symbols:

- `yyyy-MM-dd HH:mm:ss.SSSS`: 2022-01-10 10:05:02.1232
- `yyyy/MM/dd HH:mm:ss.SSSS`: 2022/01/10 10:05:0