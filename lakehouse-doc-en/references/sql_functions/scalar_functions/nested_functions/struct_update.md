### STRUCT_UPDATE 

#### Description
The `STRUCT_UPDATE` function is used to update a specified field in a structure (struct), replacing the value corresponding to the given field name with a new expression value (expr). Note that the type of the new value can be different from the original value.

#### Parameters
* `struct`: The structure (struct) to be updated.
* `name`: The name of the field to be updated, which must be a string constant.
* `expr`: The new expression value used to replace the original field value, which can be of any type.

#### Return Value
Returns a new structure (struct) with the same structure as the original, but with the specified field's value updated.

#### Example
1. Suppose we have a structure `s1` with two fields: the value of `"a"` is 1, and the value of `"b"` is 2. We can use the `STRUCT_UPDATE` function to update the value of the field `"a"` to the string `"hello"`:
```sql
SELECT STRUCT_UPDATE(named_struct('a', 1, 'b', 2), 'a', 'hello');
```
The execution result:
```json
{"a":"hello", "b":2}
```
2. Similarly, we can also update the value of the field `"b"` to the string `"hello"`:
```sql
SELECT STRUCT_UPDATE(named_struct('a', 1, 'b', 2), 'b', 'hello');
```
The execution result:
```json
{"a":1, "b":"hello"}
```
3. Besides strings, we can also use other types of expressions to update field values, such as updating the value of field `"a"` to the current timestamp:
```sql
SELECT STRUCT_UPDATE(named_struct('a', 1, 'b', 2), 'a', TIMESTAMP "2023-04-01 12:00:00");
```
The execution result:
```json
{"a":2023-04-01 12:00:00, "b":2}
```
Through the above example, you can see that the `STRUCT_UPDATE` function is very flexible and easy to use when updating struct fields.