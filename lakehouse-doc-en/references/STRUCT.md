# STRUCT

The `STRUCT` function is used to create a structure that can contain multiple values of different types. The composition of the structure is described by a series of field names and corresponding data types. Structures are very useful when dealing with complex data, as they conveniently organize multiple related data together.

## Syntax
```
STRUCT<field1_name: field1_type, field2_name: field2_type, …>
```
## Example

1. Create a struct that contains the company name and the number of employees:
    ```
   CREATE TABLE TABLE_STRUCT(col struct<company_name:string,employee_count:int>)
    ```
2. Use the `named_struct` function to create a structure with explicit field names:
   ```
   SELECT named_struct('company_name', 'ClickZetta', 'employee_count', 5);
   ```
3. Use structs in queries combined with other fields:
   ```
   SELECT
    col.company_name,
    col.employee_count,
   FROM TABLE_STRUCT;
   ```