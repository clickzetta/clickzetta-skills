### FILTER 

####  Description
The FILTER function is used to filter elements in an array based on a given lambda expression. This function supports two forms of lambda expressions: single-parameter form and dual-parameter form (including element index).

#### Parameter Description
- `array`: The input array, type `array<T>`.
- `x -> expr`: Single-parameter form of the lambda expression, where `x` represents an element in the array, and `expr` needs to return a boolean value (true or false).
- `(x, i) -> expr`: Dual-parameter form of the lambda expression, where `x` represents an element in the array, `i` represents the index of the element (starting from 0), and `expr` needs to return a boolean value (true or false).

#### Return Type
Returns a new array of type `array<T>`, containing elements that satisfy the lambda expression.

#### Usage Example
1. Filter out odd elements in the array:
```sql
SELECT filter(array(2, 1, 3, 5, 4), x -> x % 2 != 0);
-- Result: [1, 3, 5]
```
2. Select elements in the array with an index less than or equal to 2:
```sql
SELECT filter(array(4, 2, 6, 8, 10), (x, i) -> i <= 2);
-- Result: [4, 2, 6]
```
3. Filter out elements in the array that are greater than or equal to 10:
```sql
SELECT filter(array(10, 15, 20, 25, 30), x -> x >= 10);
-- Result: [10, 15, 20, 25, 30]
```
4. Get elements with odd indices in the array:
```sql
SELECT filter(array(1, 2, 3, 4, 5, 6), (x, i) -> i % 2 = 0);
-- Result: [1, 3, 5]
```
#### Notes
- Ensure that the return value of the `expr` in the lambda expression is of Boolean type.
- When using the two-parameter form of the lambda expression, the value range of `i` is from 0 to the length of the array minus 1.

By using the FILTER function, you can easily perform conditional filtering on arrays, thereby processing data more efficiently.