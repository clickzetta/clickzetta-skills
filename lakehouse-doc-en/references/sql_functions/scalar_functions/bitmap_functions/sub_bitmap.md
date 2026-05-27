### SUB_BITMAP 

####  Description
The SUB_BITMAP function is used to extract a subset from the original bitmap type data, starting from the specified offset position and containing up to limit elements. This function is only applicable to data ranges of integer types.

#### Parameter Description
* bitmap: The original bitmap type data from which the subset needs to be extracted.
* offset: The position to start extracting the subset (integer type).
* limit: The maximum length of the subset to be extracted (integer type).

#### Return Result
Returns a bitmap type data containing a subset of up to limit elements starting from the offset position.

#### Usage Example
1. Extract a subset of 1 element starting from position 1:
```sql
SELECT sub_bitmap(bitmap_build(array(2, 1, 3)), 1, 1);
-- Result: [1]
```
2. Extract a subset of 2 elements starting from position 0:
```sql
SELECT sub_bitmap(bitmap_build(array(2, 1, 3, 4, 5)), 0, 2);
-- Result: [2, 1]
```
3. Extract a subset of 3 elements starting from position 2:
```sql
SELECT sub_bitmap(bitmap_build(array(2, 1, 3, 4, 5, 6, 7, 8, 9)), 2, 3);
-- Result: [3, 4, 5]
```
#### Notes
* When the offset or limit parameter exceeds the range of the original bitmap data, the function will return an empty bitmap type data.
* If the limit parameter is greater than the result of the original bitmap data length minus the offset parameter, the actual extracted subset length will be equal to the result of the original data length minus the offset parameter.
* The client does not support directly printing the bitmap type result. If you directly view the bitmap result, an error will occur. Therefore, in actual use, if you need to display the screen, you need to use bitmap_to_array to convert it into an array.