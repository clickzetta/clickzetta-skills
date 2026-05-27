### NOW 
#### Description
The `now` function is a non-deterministic function used to return the current timestamp. During the execution of a query, no matter how many times the `now` function is called, the returned timestamp is the same, fixed from the moment the query starts.

#### Syntax
```
now()
```
#### Parameters
None

#### Return Result Type
`timestamp_ltz`

#### Usage Example
The following is a simple example of using the `now` function:
```sql
SELECT now();
```
After executing the above SQL statement, the result will be similar to the following, with the specific time varying according to the actual time of the query execution:
```
2022-01-01 15:17:22.098368
```
#### More Examples
1. Use the current timestamp as the record creation time when inserting data:
```sql
INSERT INTO my_table (id, name, created_at) VALUES (1, 'John Doe', now());
```
```markdown
2. When updating data, use the current timestamp as the record's last update time:
```
```sql
UPDATE my_table SET name = 'Jane Doe', updated_at = now() WHERE id = 1;
```
3. When selecting data, filter out records created in the past 24 hours:
```sql
SELECT * FROM my_table WHERE created_at > now() - INTERVAL '1 day';
```

4. Compare the current time with the last update time of the record to determine if the record has changed within the last hour:

```sql
SELECT * FROM my_table WHERE updated_at > now() - INTERVAL '1 hour';
```
By the above example, you can better understand the usage scenarios of the `CURRENT_TIMESTAMP` function in practical applications.