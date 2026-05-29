### CURRENT_TIMESTAMP Function
```
current_timestamp()
```
#### Function Description
The `CURRENT_TIMESTAMP` function is a non-deterministic function used to return the timestamp at the start of the current query execution. Within the same query, no matter how many times the `CURRENT_TIMESTAMP` function is called, the returned timestamp is the same. This function is very useful for recording the start time of query execution, especially in time-sensitive data analysis and transaction processing.

#### Parameter Description
No parameters need to be provided.

#### Return Type
This function returns a timestamp of type `timestamp_ltz`.

#### Usage Example
1. Query the current timestamp:
   ```sql
   SELECT current_timestamp();
   ```
The execution result:
   ```
   2022-01-01 15:17:22.098368
   ```
2. Record the current timestamp when inserting data:
   ```sql
   INSERT INTO my_table (id, name, created_at) VALUES (1, 'John Doe', current_timestamp());
   ```
This statement will use the current timestamp as the value for the `created_at` field when inserting a new record.

3. Compare the difference between the timestamps before and after the query:
```sql
SELECT current_timestamp() AS start_time;
-- Execute some query operations --
SELECT current_timestamp() AS end_time;
```
This will record the start and end timestamps of the query separately, which can be used to analyze the execution time of the query.

4. Use in conjunction with time intervals to calculate future or past points in time:
   ```sql
   SELECT current_timestamp() + INTERVAL '1 day' AS tomorrow_date;
   ```
The execution result:
    ```
    2024-04-08 20:03:39.170094
    ```