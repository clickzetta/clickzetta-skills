### ARRAY_REPEAT

####  Description
The `array_repeat` function is used to create a new array consisting of a specified number of identical elements. This function accepts two parameters: `expr` which represents the element to be repeated, and `count` which represents the number of repetitions. The function returns an array of type `array<T>`, where `T` is the type of the element.

#### Parameter Description
- `expr` (T): The element to be repeated.
- `count` (int): The number of times the element needs to be repeated.

#### Return Type
- Returns an array of type `array<T>`.

#### Usage Example
1. Repeat a string:
   ```sql
   SELECT array_repeat('hello', 3);
   ```
result：
   ```
   ["hello", "hello", "hello"]
   ```
2. Duplicate Values:
   ```sql
   SELECT array_repeat(42, 4);
   ```
result：
   ```
   [42, 42, 42, 42]
   ```
3. Use in conjunction with other functions: {#use-in-conjunction-with-other-functions}
   ```sql
   SELECT array_repeat(upper('a'), 5);
   ```
result：
   ```
   ["A", "A", "A", "A", "A"]
   ```
4. Repeated Date and Time:
   ```sql
   SELECT array_repeat(timestamp '2023-04-01 12:00:00', 2);
   ```
result：
   ```
   ["2023-04-01 12:00:00", "2023-04-01 12:00:00"]
   ```
#### Notes
- Ensure the `count` parameter is a non-negative integer. If `count` is negative, the function will return an empty array.
- When `expr` is a complex data type (such as an object or array), the entire structure will be repeated, not individual elements.

By using the `array_repeat` function, you can easily create arrays with repeated elements, simplifying the logic for data processing and transformation.