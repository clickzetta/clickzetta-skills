### Convert Bitmap to Array Function: bitmap_to_array

####  Description
The main function of `bitmap_to_array` is to convert the input bitmap type data into `array<bigint>` type data. This function is very useful in scenarios where bitmap data needs to be processed and converted into an array.

####  Syntax
```
bitmap_to_array(bitmap)
```
* bitmap : The bitmap type data that needs to be converted.

#### Return Type
This function returns data of type `array<bigint>`.

#### Usage Example
Below are several usage examples of the `bitmap_to_array` function:

Example 1: Combine with the `bitmap_build` function to convert an integer array to a bitmap, and then convert the bitmap back to an integer array.
```sql
SELECT bitmap_to_array(bitmap_build(array(1, 2, 3)));
-- The return result is [1, 2, 3]
```
Through the above example, you can see the flexibility and practicality of the `bitmap_to_array` function when handling bitmap data. In practical applications, you can convert bitmap data to an array as needed to facilitate more complex data processing and analysis.