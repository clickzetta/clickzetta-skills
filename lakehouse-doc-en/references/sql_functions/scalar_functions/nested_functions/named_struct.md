### NAMED_STRUCT

####  Description
The `named_struct` function is used to create a struct with specified field names and corresponding field values. This function can combine multiple fields and their values into a whole, making it convenient to display data in a structured form in query results.

#### Syntax Format
```
named_struct(f1, v1, f2, v2, ..., fN, vN)
```
#### Parameter Description
- `f1, f2, ..., fN`: Field names, type is string, representing the names of each field in the struct.
- `v1, v2, ..., vN`: Field values, types are `T1, T2, ..., TN`, representing the values corresponding to each field in the struct.

#### Return Type
- Returns a struct containing fields such as `f1:T1, f2:T2, ..., fN:TN`.

#### Usage Example

**Example 1: Creating a simple named struct**
```sql
SELECT named_struct('id', 1, 'name', 'Alice');
```
Return Results:
```
{"id":1,"name":"Alice"}
```
**Example 2: Creating Complex Structures with Other Functions**
```sql
SELECT named_struct('user', named_struct('id', 1, 'name', 'Alice'), 'created_time', '2022-01-01 10:00:00');
```
Return Results:
```
{"user":{"id":1,"name":"Alice"},"created_time":"2022-01-01 10:00:00"}
```
**Example 3: Using Named Structs in Queries**
```sql
SELECT id, named_struct('name', name, 'age', age) AS user_info
FROM users;
```
Assume the `users` table contains the fields `id`, `name`, and `age`, and the return result is:
```
id | user_info
--- | ---------------------------------------------------------------------------------
1  | {"name":"Alice","age":30}
2  | {"name":"Bob","age":25}
...
```
#### Notes
- Please ensure that the values of the field names `f1, f2, ..., fN` are valid strings, otherwise it may cause the function to fail.
- When field names conflict with existing field names, you need to use aliases or other methods to avoid conflicts.
- When using the `named_struct` function, please pay attention to the matching of field value types with the field types in the structure to ensure data correctness.