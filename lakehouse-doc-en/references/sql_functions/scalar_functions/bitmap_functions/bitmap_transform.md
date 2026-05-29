### BITMAP_TRANSFORM 

#### Description
The `BITMAP_TRANSFORM` function is used to transform specified elements (from_array) in a bitmap type data into another set of elements (to_array). This function requires the input parameters from_array and to_array to be of the same length and only supports int type interval values.

#### Functionality
With this function, you can easily replace or transform elements in a bitmap. For example, you can convert a bitmap containing specific numbers into a bitmap containing another set of numbers, thereby achieving quick data transformation and processing.

#### Parameters
* `bitmap`: The input bitmap type data.
* `from_array`: An array containing the elements to be replaced, with elements of type bigint.
* `to_array`: An array containing the target elements used to replace the elements in from_array, with elements of type bigint.

#### Return Result
Returns a new bitmap type data where the elements in from_array have been replaced by the elements in to_array.

####  Example
1. Replace element 1 in the bitmap with 100, element 2 with 200, and element 3 with 300.
   ```sql
   SELECT bitmap_transform(bitmap_build(array(1, 2, 3)), array(1, 2, 3), array(100, 200, 300));
   ```
Return result: `[100, 200, 300]`

2. Replace element 5 in the bitmap with 10, and element 10 with 20.
   ```sql
   SELECT bitmap_transform(bitmap_build(array(5, 10, 15, 20)), array(5, 10), array(10, 20));
   ```
Return result: `[ 15, 20]`

3. Replace element 3 in the bitmap with 5, and element 7 with 9.
   ```sql
   SELECT bitmap_transform(bitmap_build(array(1, 3, 7, 8, 9)), array(3, 7), array(5, 9));
   ```
Return result: `[1, 5, 9, 8, 9]`

#### Notes
- The client does not support directly printing bitmap type results. If you try to view the bitmap result directly, an error will occur. Therefore, in actual use, if you need to display the screen, you need to use bitmap_to_array to convert it into an array.
* Ensure that the lengths of the input from_array and to_array parameters are the same, otherwise the function will not execute.
* Currently, this function only supports int type interval values. For other data types, use other methods for replacement and conversion.
* When performing replacement operations, ensure that the elements in the target array do not cause duplication or conflict in the bitmap.
