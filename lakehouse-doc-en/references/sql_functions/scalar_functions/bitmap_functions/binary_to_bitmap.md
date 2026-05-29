### BINARY_TO_BITMAP
```
binary_to_bitmap(binary)
```
####  Description
The main function of `binary_to_bitmap` is to convert input data of binary type into bitmap type. This function is usually used in conjunction with the `bitmap_to_binary` function, which converts bitmap type to binary type. This conversion is very useful when dealing with bitmap data, especially in scenarios where conversion between different data formats is needed.

#### Parameter Description
* binary: The binary type data to be converted.

#### Return Result
Returns the converted bitmap type data.

####  Example

1. Create a bitmap array using the `bitmap_build` function, convert it to binary type using the `bitmap_to_binary` function, and finally restore it to bitmap type using the `binary_to_bitmap` function:
```sql
SELECT binary_to_bitmap(bitmap_to_binary(bitmap_build(array(1,2,3))));
-- [1,2,3]
```
#### Precautions
- Ensure that the input binary data is valid; otherwise, the function may not execute correctly.
- In practical applications, you may need to combine other bitmap functions to achieve more complex operations. Make sure to understand the usage of related functions before using the `binary_to_bitmap` function.

Through the above examples and explanations, you can better understand the purpose and usage of the `binary_to_bitmap` function. When dealing with bitmap data, this function can help you easily convert between different data formats, thereby improving data processing efficiency.