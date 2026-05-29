### STRUCT_INSERT

### Description
The `struct_insert` function is used to insert a new field into a structure (struct). The name of the new field is specified by the `name` parameter, and its value is specified by the `expr` parameter. The optional `indexToInsert` parameter is used to specify the insertion position. If `indexToInsert` is not specified or its value is 0, the new field will be inserted at the end of the structure. If `indexToInsert` is 1, the new field will be inserted after the first field, and so on.

### Functionality
- Add a new field to the structure.
- Control the insertion position of the new field through the `indexToInsert` parameter.

### Parameters
- `struct`: The structure into which the new field needs to be inserted.
- `name`: The name of the new field, must be a string constant.
- `expr`: The value of the new field, can be data of any type.
- `indexToInsert`: (Optional) Specifies the insertion position of the new field, an integer constant, default value is 0.

### Return Result
Returns a new structure, the structure of which depends on the inserted key-value pair and the specified insertion position.

### Usage Example
1. Add a new field to the end of the structure:
```sql
SELECT struct_insert(named_struct('a', 1, 'b', 2), 'x', 'hello');
-- Result: {"a":1, "b": 2, "x":"hello"}
```
2. Insert new fields at the beginning of the struct:
```sql
SELECT struct_insert(named_struct('a', 1, 'b', 2), 'x', 'hello', 0);
-- Result: {"x":"hello", "a":1, "b": 2}
```
3. Insert a new field after the first field:
```sql
   SELECT struct_insert(named_struct('a', 1, 'b', 2), 'x', 'hello', 1);
   -- Result: {"a":1, "x":"hello", "b": 2}
   ```
4. Insert a new field before the second field:
```sql
SELECT struct_insert(named_struct('a', 1, 'b', 2), 'y', 3, 2);
-- Result: {"a":1, "y":3, "b": 2, "x": "hello"}
```
5. Insert new fields into a structure that contains nested structures:
```sql
SELECT struct_insert(named_struct('outer', named_struct('inner', 'value')), 'newField', 'newValue');
-- Result: {"outer":{"inner":{"value"},"newField":"newValue"}}
```
### Notes
- Please ensure the `name` parameter is a string constant, otherwise it may cause the function to fail.
- The valid range for the `indexToInsert` parameter is from 0 to the number of struct fields (inclusive). Values outside this range will cause the function to fail.
- When the insertion position conflicts with existing fields (for example, attempting to insert a new field at the position of an existing field), the function will return an error.