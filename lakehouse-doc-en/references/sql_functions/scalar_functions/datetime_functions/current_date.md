### CURRENT_DATE 
```
CURRENT_DATE()
```
####  Description
The CURRENT_DATE function is a non-deterministic function used to return the current date at the time the query is executed. It should be noted that multiple calls to CURRENT_DATE() during the same query will return the same result.

#### Parameters
This function does not require any parameters.

#### Return Result
The return value type is date.

#### Usage Example
The following example will help you better understand the usage of the CURRENT_DATE function:

1. Query the current date:
   ```sql
   SELECT CURRENT_DATE();
   2022-01-01
   ```



2. Use the current date in more complex queries:
   ```sql
   SELECT user_id, order_date, current_date() - INTERVAL 7 DAY AS week_ago_date
   FROM orders;
   +-----------+------------+-------------------+
   | user_id  | order_date | week_ago_date    |
   +-----------+------------+-------------------+
   | 1         | 2022-01-05 | 2021-12-25         |
   | 2         | 2022-01-03 | 2021-12-27         |
   | 3         | 2021-12-29 | 2021-12-22         |
   +-----------+------------+-------------------+
   ```

3. Filter out users who placed orders in the past week:
   ```sql
   SELECT user_id, order_date
   FROM orders
   WHERE order_date >= CURRENT_DATE() - INTERVAL 1 WEEK;
   +-----------+------------+
   | user_id  | order_date |
   +-----------+------------+
   | 1         | 2022-01-05 |
   | 4         | 2022-01-02 |
   +-----------+------------+
   ```
