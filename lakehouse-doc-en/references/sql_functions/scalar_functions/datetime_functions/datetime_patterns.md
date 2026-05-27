### DATETIME PATTERNS

#### Symbols

|Symbol|Meaning|Format|Example|
|---|---|---|---|
|**G**|era|text|AD; Anno Domini|
|**y**|year|year|2020; 20|
|**D**|day-of-year|number(3)|189|
|**M**|month-of-year|month|7; 07; Jul; July|
|**d**|day-of-month|number(2)|28|
|**Q**|quarter-of-year|number/text|3; 03; Q3; 3rd quarter|
|**a**|am-pm-of-day|am-pm|PM|
|**h**|clock-hour-of-am-pm (1-12)|number(2)|12|
|**K**|hour-of-am-pm (0-11)|number(2)|0|
|**k**|clock-hour-of-day (1-24)|number(2)|0|
|**H**|hour-of-day (0-23)|number(2)|0|
|**m**|minute-of-hour|number(2)|30|
|**s**|second-of-minute|number(2)|55|
|**S**|fraction-of-second|fraction|978|
|**V**|time-zone ID|zone-id|America/Los_Angeles; Z; -08:30|
|**z**|time-zone name|zone-name|Pacific Standard Time; PST|
|**O**|localized zone-offset|offset-O|GMT+8; GMT+08:00; UTC-08:00;|
|**X**|zone-offset ‘Z’ for zero|offset-X|Z; -08; -0830; -08:30; -083015; -08:30:15;|
|**x**|zone-offset|offset-x|+0000; -08; -0830; -08:30; -083015; -08:30:15;|
|**Z**|zone-offset|offset-Z|+0000; -0800; -08:00;|
|**’‘**|single quote|literal|’|


#### Explanation of Some Symbols
Year:
- yyyy Four-digit year representation, e.g., 2022

Month:
- M Single-digit month representation, e.g., 3, 12
- MM Double-digit month representation, e.g., 03, 12

Day of the month:
- d Single-digit day of the month representation, e.g., 5, 20
- dd Double-digit day of the month representation, e.g., 05, 20

Hour, 24-hour format:
- H Single-digit 24-hour format hour representation, e.g., 1, 23
- HH Double-digit 24-hour format hour representation, e.g., 01, 23

Minute:
- m Single-digit minute representation, e.g., 4, 59
- mm Double-digit minute representation, e.g., 04, 59

Second:
- s Single-digit second representation, e.g., 8, 59
- ss Double-digit second representation, e.g., 08, 59

Millisecond/Microsecond:
- S Can have 1-9 digits, from left to right representing milliseconds (3 digits), microseconds (3 digits), nanoseconds (3 digits). Singdata currently supports microsecond precision for timestamps, so nanoseconds will be discarded when parsing time strings, and the nanosecond part will be set to zero when generating time strings. When the number of S digits is less than 9, the precision will be reduced from the right.

Examples:
- yyyy-MM-dd HH:mm:ss.SSSS: 2022-01-10 10:05:02.1232
- yyyy/M/d H:m:s.SSSS: 2022/1/10 10:5:2.12
- yyyy'HelloWorldyMdH'-MM-dd HH:mm:ss.SSSS: 2022HelloWorldyMdH-01-10 10:05:02.1232