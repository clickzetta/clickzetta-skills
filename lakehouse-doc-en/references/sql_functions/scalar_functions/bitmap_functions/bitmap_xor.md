### BITMAP_XOR Function

`bitmap_xor` function is used to perform a set XOR (exclusive OR) operation on two bitmap type data. This function is very useful when dealing with set data, especially in scenarios where it is necessary to find different elements from two sets.

### Syntax
```
bitmap_xor(left, right)
```
### Parameters
* `left` and `right`: Input bitmap type data.

### Return Result
Returns a bitmap type result that contains the result of the XOR operation on the two input bitmaps.

### Usage Example
The following example demonstrates how to use the `bitmap_xor` function to process different bitmap data.

**Example 1**: Perform XOR operation on two simple bitmap data.
```sql
SELECT bitmap_xor(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4)));
```
Results:
```
[1, 4] -- The result is displayed in array form, the actual client may not support bitmap type printing
```
**Example 2**: Use the `bitmap_to_array` function to convert the result into an array format for viewing.
```sql
SELECT bitmap_to_array(bitmap_xor(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4))));
```
Results:
```
[1, 4]
```
**Example 3**: Perform XOR operation on two bitmaps containing duplicate elements.
```sql

```
Results:
```
[1, 4]
```
**Example 4**: Perform XOR operation on two bitmaps containing negative numbers.
```sql
SELECT bitmap_xor(bitmap_build(array(-1, -2, -3)), bitmap_build(array(-2, -4, -3)));
```
Results:
```
[-1, -4]
```
### Notes
* Please ensure that both input parameters are of the bitmap type, otherwise the function execution will fail.
* The client does not support directly printing the results of the bitmap type. If you directly view the bitmap results, an error will occur. Therefore, in actual use, if you need to display the results on the screen, you need to use bitmap_to_array to convert them into an array.
* When handling large datasets, please be aware of the performance impact. Where possible, try to optimize the input data to improve the function execution efficiency.