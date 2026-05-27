### MINUTE 
```
MINUTE(timestamp)
```
####  Description

The MINUTE function is used to extract the minute part from a given timestamp type expression. This function accepts a timestamp type parameter and returns an integer representing the minute part of that time.

#### Parameter Description

* timestamp: A timestamp type expression, which can be a string, timestamp, etc.

#### Return Result

Returns an integer representing the minute part of the timestamp parameter.

#### Usage Example

1. Extract the minute part from a string type time:
```
SELECT MINUTE('2022-01-01 10:23:15.321');
-- Result: 23
```
```markdown
2. Extract the minute part from the current timestamp:
```
```
SELECT MINUTE(TIMESTAMP "2022-01-02 03:21:00");
-- Result: 21
```
```markdown
3. Extract the minute part from a string type time and use it in conjunction with other time operations:
```
```
SELECT MINUTE('2022-01-01 10:23:15.321') + INTERVAL '1' MINUTE;
-- Result: 24
```
4. Extract the minute part from the current timestamp and convert it to string format:
```
SELECT CAST(MINUTE(TIMESTAMP "2022-01-02 03:21:00") AS STRING);
-- Result: 21
```
