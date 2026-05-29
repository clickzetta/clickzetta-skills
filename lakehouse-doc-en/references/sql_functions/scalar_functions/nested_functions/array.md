### ARRAY
``` sql
array(e1, e2, ... eN)
```
####  Description
The `array` function is used to create an array containing specified elements. This function accepts any number of arguments and treats them as elements of the array. All elements will be arranged in the order they are passed in.

#### Parameter Description
- `e1, e2, ... eN`: Type `T`, can be any values of the same type. If values of different types are passed in, the system will attempt implicit type conversion.

#### Return Type
- Returns an array of type `array<T>`, where `T` is the specific type of the elements.

#### Usage Example
1. Create an array containing integers:
   ```sql
   > SELECT array(1, 2, 3);
   [1, 2, 3]
   ```
2. Create an array containing floating point numbers:
   ```sql
   > SELECT array(1.5, 2.3, 4.7);
   [1.5, 2.3, 4.7]
   ```
3. Create an array containing strings:
   ```sql
   > SELECT array('apple', 'banana', 'cherry');
   ['apple', 'banana', 'cherry']
   ```
4. Implicit Type Conversion Example:
```sql
> SELECT array(1, '2', 3.0);
[1.0,2.0,3.0] -- The string '2' is implicitly converted to a numeric type
```
5. Use the `array` function in combination with the `SELECT` statement to select multiple fields from the table and create an array:
   ```sql
   > SELECT array(column1, column2, column3) FROM my_table;
   ```
Assuming `my_table` contains three columns `column1`, `column2`, `column3`, this query will return an array containing the values of these three columns for each row.

#### Notes
- When the types of the input parameters are inconsistent, the system will attempt implicit type conversion. If the conversion fails, the element will be returned as null.
- When creating arrays, ensure that all elements are type-compatible to avoid unnecessary type conversions and potential performance loss.

By using the `array` function, you can easily create and manage array data in SQL queries, allowing for more flexible handling and analysis of datasets.