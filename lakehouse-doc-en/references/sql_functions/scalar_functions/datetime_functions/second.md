### SECOND 
```
SECOND(timestamp)
```
####  Description
SECOND function is used to extract the minute part from a given timestamp type expression. This function accepts a timestamp type parameter and returns an integer representing the minute part of that time.

#### Parameter Description
- timestamp: A timestamp type expression, which can be a string, timestamp, etc.

#### Return Result
Returns an integer representing the minute part of the timestamp parameter.

####  Example
1. Extract the minute part from a string type time:
```
SELECT SECOND('2022-01-01 10:23:15.321');
-- Result: 15
```
2. Extract the minute part from the current timestamp:
```
SELECT SECOND(TIMESTAMP "2022-01-02 03:21:00");
-- Result: 0
```
3. Extract the minute part from the time in string format and use it in conjunction with other time operations:
```
SELECT SECOND('2022-01-01 10:23:15.321') + INTERVAL '1' MINUTE;
-- Result: 15
```
4. Extract the minute part from the current timestamp and convert it to string format:
```
SELECT CAST(SECOND(TIMESTAMP "2022-01-02 03:21:00") AS STRING);
-- Result: 0
```