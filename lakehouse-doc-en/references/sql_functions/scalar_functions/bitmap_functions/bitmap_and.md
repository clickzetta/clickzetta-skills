### BITMAP_AND

#### Description
The BITMAP_AND function is used to calculate the intersection of two bitmap type data. This function accepts two bitmap type parameters and returns a new bitmap type result that contains the common elements of the two input bitmaps.

#### Parameters
* left: The first bitmap type parameter.
* right: The second bitmap type parameter.

#### Return Type
Returns a result of bitmap type.

#### Example Usage
The following example demonstrates how to use the BITMAP_AND function to calculate the intersection of two bitmap type data.

Example 1:
```sql
SELECT bitmap_and(bitmap_build(array(1, 2, 3)), bitmap_build(array(2, 3, 4)));
```
Results:
```plaintext
[2, 3] -- The result is displayed in array form, the client supports bitmap type printing, you can use the bitmap_to_array function to display
```
Example 2:
```sql
SELECT bitmap_to_array(bitmap_and(bitmap_build(array(1, 2, 3, 5, 6)), bitmap_build(array(2, 3, 4, 6, 7))));
```
Results:
```plaintext
[2, 3, 6]
```
#### Precautions
* The BITMAP_AND function requires both input parameters to be of bitmap type, otherwise, the function execution will fail.
* The result is displayed in array form, but what is actually returned is a bitmap type data. The client may not support directly printing bitmap type data, so it is necessary to use the corresponding conversion function (such as bitmap_to_array) to convert it into a printable format.
* When the number of elements in the input bitmap type data is large, the calculation efficiency of the BITMAP_AND function may be affected. In this case, consider using other data types and methods for calculation.