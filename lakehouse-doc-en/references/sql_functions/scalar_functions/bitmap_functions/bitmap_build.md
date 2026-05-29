### BITMAP_BUILD 

#### Description
The `bitmap_build` function is used to construct a bitmap type from an array expression (expr) of integer types. This function takes an array as input and returns a result of bitmap type.

#### Syntax
```
bitmap_build(expr)
```
#### Parameters
- `expr`: `array<T>` type, where T is an integer type.

#### Return Value
- Returns a result of bitmap type.

#### Example Usage
1. Construct a bitmap type from an array containing integers 1, 2, 3:
   ```sql
   SELECT bitmap_build(array(1, 2, 3));
   ```
The result will be displayed in the form of an array, but it is actually of the bitmap type:
   ```
   [1,2,3]
   ```
2. Convert the above result back to array form to verify its content:
   ```sql
   SELECT bitmap_to_array(bitmap_build(array(1, 2, 3)));
   ```
The result will be displayed in the form of an array:
   ```
   [1,2,3]
   ```
3. Construct a bitmap type containing multiple consecutive integers:
   ```sql
   SELECT bitmap_build(array(1, 2, 3, 4, 5));
   ```
The result will be displayed as:
   ```
   [1,2,3,4,5]
   ```
4. Constructing a bitmap type from an array containing negative integers and zero values:
   ```sql
   SELECT bitmap_build(array(-1, 0, 2, -3));
   ```
The result will be displayed as:
   ```
   [-1, 0, 2, -3]
   ```
#### Notes
- The client does not support directly printing bitmap type results. If you try to view bitmap results directly, an error will occur. Therefore, in actual use, if you need to display on the screen, you should use bitmap_to_array to convert it into an array.
- When processing large datasets, the bitmap type can improve query performance because it occupies relatively less memory space.

Through the above examples and explanations, you can better understand how to use the `bitmap_build` function to build a bitmap type from an integer array and leverage its advantages in practical applications.