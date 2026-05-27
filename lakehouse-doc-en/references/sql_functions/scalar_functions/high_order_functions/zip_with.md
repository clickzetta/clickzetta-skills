### ZIP_WITH 

####  Description
The ZIP_WITH function can calculate the corresponding elements of two arrays (array1 and array2) based on the provided lambda expression and generate a new array. When the lengths of the two input arrays are inconsistent, the missing elements of the shorter array will be filled with NULL values, and then the calculation will continue.

#### Parameter Description
- array1, array2: `array<T>` type, the two arrays to be operated on.
- (x1, x2) -> expr: A two-parameter lambda expression, where x1 corresponds to the elements of array1, and x2 corresponds to the elements of array2. expr is the content of the expression, and its return type is not restricted.

#### Return Type
Returns a new array, with the type of the array elements being the return type of the lambda expression.

#### Usage Example
1. Add the corresponding elements of two arrays and convert them to string type:

```sql
SELECT ZIP_WITH(array1, array2, (x1, x2) -> CAST(x1 + x2 AS STRING))
FROM table_name;
```
```sql
SELECT zip_with(array(1, 2), array(2, 3), (x, y) -> CAST((x + y) AS string));
-- Return result: ["3", "5"]
```
2. Calculate the difference between corresponding elements of two arrays:
```sql
SELECT zip_with(array(5, 3, 1), array(2, 4, 6), (x, y) -> x - y);
-- Return result: [3, -1, -5]
```


3. Concatenate corresponding elements of two arrays into a new string:
```sql
SELECT zip_with(array('a', 'b'), array('x', 'y'), (x, y) -> CONCAT(x, y));
-- Return result: ['ax', 'by']
```
4. When the array lengths are inconsistent, the missing elements in the shorter array will be filled with NULL values:
```sql
SELECT zip_with(array(1, 2), array(2, 3, 4), (x, y) -> x * y);
-- Return result: [2, 6, null]
```
#### Notes
- When the input array is empty, the ZIP_WITH function will return an empty array.
- When NULL values are used in the lambda expression, its behavior should conform to the handling rules of NULL in SQL.

Through the above description and examples, you can better understand and use the ZIP_WITH function to process array data.