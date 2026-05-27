### TRANSFORM 

####  Description
The TRANSFORM function is used to transform elements in an array based on a given lambda expression. This function supports two forms of lambda expressions: single-parameter form and double-parameter form (including element index).

#### Parameter Description
- array: The input array, of type `array<T>`, where T can be any data type.
- x -> expr: Single-parameter form of the lambda expression, where x represents an element in the array, and expr is the new value calculated based on x. The return type is unrestricted.
- (x, i) -> expr: Double-parameter form of the lambda expression, where x represents an element in the array, and i represents the index of the element (starting from 0). The expr is the new value calculated based on x and i. The return type is unrestricted.

#### Return Value
Returns a new array of type `array<U>`, where U is the return type of the lambda expression.

####  Example

1. Calculate the square of each element in the array and return the result array:
```sql
SELECT transform(array(1, 2, 3), x -> x * x);
-- Output result: [1, 4, 9]
```
2. Convert the string elements in the array to uppercase and return the result array:
```sql
SELECT transform(array('hello', 'world'), x -> upper(x));
-- Output result: ['HELLO', 'WORLD']
```
3. Calculate a new array based on the index and value of the array elements, where each element's value is the sum of its index and value:
```sql
SELECT transform(array(2, 1, 3), (x, i) -> x + i);
-- Output result: [2, 2, 5]
```
4. Split the strings in the array and return the result array:
```sql
SELECT transform(array('hello,world', NULL, '1,2,3'), x -> split(x, ','));
-- Output result: [["hello","world"],null,["1","2","3"]]
```
5. Multiply each value in the array by 2 and return the resulting array:
```sql
SELECT transform(array(1, 3, 5), x -> x * 2);
-- Output result: [2, 6, 10]
```
#### Notes
- Please ensure that the parameter names in the lambda expression match the actual parameters passed in.
- When using a lambda expression with two parameters, note that the element index starts counting from 0.