### HOUR 

#### Description
The HOUR function is used to extract the hour part from a given timestamp type expression. This function is very useful for handling time data and calculating time intervals.

#### Syntax
```sql
hour(timestamp_ltz) 
```
#### Parameters
- timestamp_ltz: Represents a timestamp type expression from which the hour part is to be extracted.

#### Return Result
Returns an integer representing the hour part of the input expression.

#### Usage Example

1. Extract the hour part from the current timestamp:
```sql
SELECT hour( NOW());
```
This will return the hour part of the current time.

2. Extract the hour part from the specified timestamp:
```sql
SELECT hour(TIMESTAMP  '2022-01-01 10:00:00');
```
This will return 10, indicating the hour part of the specified time.

3. Extract the hour part from a table containing timestamps:
Suppose we have a table named `orders` that contains a column named `order_time` of type timestamp. We can extract the hour part of each order as follows:
```sql
SELECT order_id, hour(order_time) as hour
FROM orders;
```
This will return the ID and hour part of each order in the `orders` table.

4. Use in combination with other time functions:
```sql
SELECT order_id, 
       hour(order_time) as hour, 
       day(order_time) as day, 
       month(order_time) as month
FROM orders;
```
This will return the ID, hour part, day, and month of each order in the `orders` table.
